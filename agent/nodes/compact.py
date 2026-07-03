import logging
import tiktoken

from config.settings import COMPACT_TOKEN_LEN
from agent.state import AgentState
from typing import TypedDict, NotRequired
from langchain_core.messages import RemoveMessage, AnyMessage

logger = logging.getLogger(__name__)
enc = tiktoken.get_encoding("o200k_base")

class CompactNodeOutput(TypedDict):
    messages: NotRequired[list[RemoveMessage]]

def compact_node(state: AgentState) -> CompactNodeOutput:
    messages = state.get('messages', [])
    total = len(messages)

    logger.info(f"Compact: {total} messages in thread, counting tokens...")

    token_count = 0
    strip_idx = 0

    for idx in range(total - 1, -1, -1):
        msg = messages[idx].content

        if not isinstance(msg, str):
            continue

        token_count += len(enc.encode(msg))

        if token_count > COMPACT_TOKEN_LEN:
            strip_idx = idx + 1
            break

    msg_to_remove = messages[:strip_idx]

    if not msg_to_remove:
        logger.info(f"Compact: no-op — {token_count} tokens across {total} messages, under threshold ({COMPACT_TOKEN_LEN})")
        return CompactNodeOutput()

    logger.info(f"Compact: {token_count} tokens exceeded threshold ({COMPACT_TOKEN_LEN}) — removing {len(msg_to_remove)} messages, retaining {total - len(msg_to_remove)}")

    return CompactNodeOutput(messages=[RemoveMessage(id=msg.id) for msg in msg_to_remove if msg.id is not None])