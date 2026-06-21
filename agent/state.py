import operator
from typing import TypedDict, Annotated, NotRequired
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    planner_model: NotRequired[str]
    responder_model: NotRequired[str]
    plan: NotRequired[list[dict]]
    current_tool: NotRequired[str]
