import operator
from typing import TypedDict, Annotated, NotRequired

from langchain_core.messages import AnyMessage


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    responder_model: NotRequired[str]
    plan: NotRequired[list[dict]]
    current_tool: NotRequired[str]
    memory_context: NotRequired[str]
