from typing import TypedDict, Annotated, NotRequired
from datetime import datetime

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    responder_model: NotRequired[str]
    plan: NotRequired[list[dict]]
    current_tool: NotRequired[str]
    memory_context: NotRequired[str]
    
    last_active_at: NotRequired[datetime]
