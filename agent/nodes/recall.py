import logging

from memory.store import MemoryStore
from typing import TypedDict
from agent.state import AgentState

logger = logging.getLogger(__name__)

class RecallNodeOutput(TypedDict):
    memory_context: str

def make_recall_node(store: MemoryStore):
    async def recall_node(state: AgentState) -> RecallNodeOutput:
        last_message = state['messages'][-1].content

        if not isinstance(last_message, str):
            return RecallNodeOutput(memory_context="")

        if len(last_message.split()) < 3:
            logger.info("Recall: message too short, skipping search")
            return RecallNodeOutput(memory_context="")

        logger.info(f"Recall: searching memory for '{last_message[:60]}'")

        try:
            results = await store.search(content=last_message)

            logger.info(f"Recall: {len(results)} result(s) found")

            for i, fact in enumerate(results):
                logger.debug(f"Recall [{i + 1}]: {fact}")

            recalled_content = "\n".join(results)

            return RecallNodeOutput(memory_context=recalled_content)
        except Exception as e:
            logger.warning(f"Recall search failed: {e}")
            return RecallNodeOutput(memory_context="")

    return recall_node