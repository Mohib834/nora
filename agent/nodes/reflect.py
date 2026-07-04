import json
import logging
from datetime import datetime, timezone

from langgraph.graph.state import CompiledStateGraph, RunnableConfig

from memory.store import MemoryStore
from utils.llm import aget_llm_answer

logger = logging.getLogger(__name__)


async def reflect(store: MemoryStore, app: CompiledStateGraph, config: RunnableConfig) -> None:
    logger.info("Reflect: starting")

    snapshot = await app.aget_state(config)
    all_messages = snapshot.values.get("messages", [])

    logger.info(f"Reflect: {len(all_messages)} total messages in thread")

    turn_start = 0
    for i in range(len(all_messages) - 1, -1, -1):
        msg = all_messages[i]
        if msg.type == "human" and not str(msg.content).startswith("Tool result ["):
            turn_start = i
            break

    turn_messages = all_messages[turn_start:]

    logger.info(f"Reflect: current turn has {len(turn_messages)} messages (start index {turn_start})")

    turn_text = "\n".join(
        f"{'User' if m.type == 'human' else 'Nora'}: {str(m.content)[:800]}"
        for m in turn_messages
    )

    logger.debug(f"Reflect: turn text:\n{turn_text}")

    prompt = f"""You are Nora's memory module. Extract durable facts from this conversation turn for Nora's long-term knowledge graph.

Write only what remains true across sessions. Focus on four categories:
1. Boss's goals and decisions — what Boss is trying to achieve or has decided
2. Preferences — how Boss likes things, what matters to them, stated criteria
3. System state — what capabilities exist, what is being built, current architecture facts
4. Capability gaps — name the specific missing capability (e.g. "task_automation", "calendar_read"), not vague "Nora couldn't answer X"

Rules:
- Write facts, not stories. "Boss is evaluating X" not "Boss requested Nora evaluate X"
- Never write "Nora found...", "Nora was unable to...", "Nora answered..." — omit execution narration entirely
- Be specific — include names, decisions, criteria, capability names
- Under 120 words — dense facts only
- Skip if the turn has no durable signal (greetings, acknowledgments, trivial confirmations)

Output raw JSON only:
{{
    "name": "<3-5 word kebab-case topic slug>",
    "episode_body": "<facts>" | null
}}

If no durable facts, return: {{"name": null, "episode_body": null}}

Conversation turn:
{turn_text}"""

    logger.info("Reflect: calling LLM to distill episode")

    try:
        raw = await aget_llm_answer('fast', [{'role': 'system', 'content': prompt}])
        raw = (raw or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw) if raw else {}
    except Exception as e:
        logger.warning(f"Reflect: LLM call failed: {e}")
        return

    episode_body = result.get('episode_body')
    name = result.get('name')

    logger.debug(f"Reflect: LLM output — name='{name}', body='{episode_body}'")

    if not episode_body or not name:
        logger.info("Reflect: trivial turn, skipping write")
        return

    episode_name = f"{name}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    logger.info(f"Reflect: writing episode '{episode_name}' to Graphiti")

    try:
        await store.write_episode(
            name=episode_name,
            episode_body=episode_body,
            source_description="Nora conversation turn",
        )
        logger.info(f"Reflect: episode '{episode_name}' written successfully")
    except Exception as e:
        logger.warning(f"Reflect: write_episode failed: {e}")
