from typing import TypedDict

from langchain_core.messages import ToolMessage

from ..state import AgentState
from agent.capabilities.types import Capability


class ExecutorOutput(TypedDict):
    messages: list
    plan: list[dict]
    current_tool: str


def make_executor_node(all_capabilities: list[Capability]):
    tools_by_name = {}
    
    for capability in all_capabilities:
        for tool in capability["tools"]:
            tools_by_name[tool.name] = tool

    async def executor_node(state: AgentState) -> ExecutorOutput:
        plan = state.get("plan", [])
        step = plan[0]

        tool = tools_by_name[step["tool"]]
        result = await tool.ainvoke(step["input"])

        return ExecutorOutput(
            messages=[ToolMessage(content=str(result), tool_call_id=step["id"])],
            plan=plan[1:],
            current_tool=step["tool"],
        )

    return executor_node
