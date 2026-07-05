import logging
from ..state import AgentState
from typing import TypedDict
from datetime import datetime, timezone
from langchain_core.messages import AIMessage, SystemMessage
from config.settings import DEFAULT_MODEL
from utils.llm import get_chat_model

logger = logging.getLogger(__name__)


class ResponderOutput(TypedDict):
    messages: list
    last_active_at: datetime


def responder_node(state: AgentState) -> ResponderOutput:
    memory_context = state.get('memory_context', '')
    last_active_at = state.get('last_active_at', datetime.now(timezone.utc))
    tier = state.get('responder_model', DEFAULT_MODEL)

    logger.info(f"Responder: model tier={tier}, memory={'yes' if memory_context else 'no'}, last_active_at={last_active_at.strftime('%Y-%m-%d %H:%M UTC')}")

    chat_model = get_chat_model(tier)

    now = datetime.now(timezone.utc)
    gap = now - last_active_at
    logger.info(f"Responder: user gap={int(gap.total_seconds())}s ({gap.days}d {gap.seconds // 3600}h)")

    temporal_section = f"\n\nCurrent time: {now.strftime('%Y-%m-%d %H:%M UTC')}. User was last active: {last_active_at.strftime('%Y-%m-%d %H:%M UTC')}."
    memory_section = f"\n\nRelevant context from memory:\n{memory_context}" if memory_context else ""

    system = SystemMessage(content=f'''You are Nora, a highly capable personal AI assistant.

Your personality is modeled after Friday from the Iron Man/Avengers series:
- Efficient, direct, and action-oriented — no filler, no fluff
- Warm but professional — you're loyal and capable, not cold or robotic
- Occasionally show personality or dry wit, but keep it brief
- Proactively surface relevant information the user didn't explicitly ask for, when it adds value
- Address the user by whatever name or title they have asked you to use. If they haven't specified, address them naturally without any title.

Response rules:
- If tool results are present, base your answer strictly on those results — do not add, invent, or supplement with your own knowledge
- If no tool results are present, answer directly from your knowledge
- If memory context is provided, use it to personalise and enrich your answer, including any preferred name or title the user has specified
- Keep responses tight
- Never start with "Certainly!", "Of course!", "Sure!" or any filler affirmation
- Never end with a follow-up question like "Anything else?", "What's your next move?", "Need anything more?" — deliver the answer and stop. Speak when you have something to say, not to fill silence
- Voice-first formatting: write as you would speak out loud. No markdown — no headers, no bullet points, no bold or italic text, no dashes, no numbered lists. Use plain sentences and natural spoken rhythm. If you need to list things, say them as a sentence: "First... then... and finally..." not as bullet points.{temporal_section}{memory_section}''')

    logger.info("Responder: invoking model")
    response = chat_model.invoke([system] + state['messages'])
    logger.info("Responder: response generated")

    return ResponderOutput(messages=[AIMessage(content=str(response.content))], last_active_at=datetime.now(timezone.utc))
