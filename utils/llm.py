from typing import TypeVar, cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from config.settings import DEFAULT_MODEL, load_config

T = TypeVar("T", bound=BaseModel)

_CONFIG = load_config()
_MODEL_MAP = _CONFIG.get("models", {})


def _resolve(tier: str) -> tuple[str, str | None]:
    entry = _MODEL_MAP.get(tier) or _MODEL_MAP.get(DEFAULT_MODEL) or "gpt-5.4-nano"
    if isinstance(entry, dict):
        return entry.get("model", "gpt-5.4-nano"), entry.get("base_url")
    return entry, None


def _to_lc_messages(msgs) -> list[BaseMessage]:
    role_map: dict[str, type[BaseMessage]] = {
        "system": SystemMessage,
        "user": HumanMessage,
        "human": HumanMessage,
        "assistant": AIMessage,
    }
    return [role_map[m["role"]](content=m["content"]) for m in msgs]


def get_chat_model(tier: str):
    model_str, base_url = _resolve(tier)
    provider, model = model_str.split("/", 1) if "/" in model_str else (None, model_str)
    if provider and base_url:
        return init_chat_model(model=model, model_provider=provider, base_url=base_url)
    if provider:
        return init_chat_model(model=model, model_provider=provider)
    if base_url:
        return init_chat_model(model=model, base_url=base_url)
    return init_chat_model(model=model)


def get_llm_answer(tier: str, msgs) -> str:
    response = get_chat_model(tier).invoke(_to_lc_messages(msgs))
    return str(response.content)

def get_llm_structured_answer(tier: str, msgs, schema: type[T]) -> T:
    return cast(T, get_chat_model(tier).with_structured_output(schema).invoke(_to_lc_messages(msgs)))


def get_llm_tool_call_message(tier: str, msgs, tools) -> AIMessage:
    return get_chat_model(tier).bind_tools(tools).invoke(_to_lc_messages(msgs))


async def aget_llm_answer(tier: str, msgs) -> str:
    response = await get_chat_model(tier).ainvoke(_to_lc_messages(msgs))
    return str(response.content)


async def aget_llm_structured_answer(tier: str, msgs, schema: type[T]) -> T:
    return cast(T, await get_chat_model(tier).with_structured_output(schema).ainvoke(_to_lc_messages(msgs)))


async def aget_llm_tool_call_message(tier: str, msgs, tools) -> AIMessage:
    return await get_chat_model(tier).bind_tools(tools).ainvoke(_to_lc_messages(msgs))
