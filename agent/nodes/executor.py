from typing import TypedDict
from langchain_core.messages import HumanMessage

from ..state import AgentState
from ..capabilities.registry import ALL_CAPABILITIES


class ExecutorOutput(TypedDict):
    messages: list
    plan: list[dict]
    current_tool: str


def executor_node(state: AgentState) -> ExecutorOutput:
    plan = state.get("plan", [])
    step = plan[0]

    tool = _find_tool(step["capability"])
    result = tool.invoke(step["input"])

    return ExecutorOutput(
        messages=[HumanMessage(content=f"Tool result [{step['capability']}]:\n{str(result)}")],
        plan=plan[1:],
        current_tool=step["capability"]
    )


def _find_tool(capability_name: str):
    for capability in ALL_CAPABILITIES:
        if capability["name"] == capability_name:
            return capability["tools"][0]
    raise ValueError(f"Unknown capability: {capability_name}")
