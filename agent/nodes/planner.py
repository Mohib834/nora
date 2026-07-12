from typing import Literal, NotRequired, TypedDict

from pydantic import BaseModel

from ..state import AgentState
from utils.llm import aget_llm_structured_answer, aget_llm_tool_call_message
from agent.capabilities.types import Capability
from langchain.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class PlanStep(TypedDict):
    tool: str
    input: dict
    id: str


class PlannerOutput(TypedDict):
    responder_model: str
    plan: list[PlanStep]
    messages: NotRequired[list]


class PlannerClassification(BaseModel):
    responder_model: Literal["fast", "smart", "reasoning", "vision"]
    needs_tool: bool
    capabilities: list[str] = []


def _build_capability_summary(all_capabilities: list[Capability]) -> str:
    return "\n".join(f"- {c['name']}: {c['description']}" for c in all_capabilities)


def make_planner_node(all_capabilities: list[Capability]):
    tools_by_capability = {c["name"]: c["tools"] for c in all_capabilities}
    capability_summary = _build_capability_summary(all_capabilities)

    async def planner_node(state: AgentState) -> PlannerOutput:
        recent_messages = state['messages'][-6:]
        conversation = "\n".join(
            f"{'User' if m.type == 'human' else 'Nora'}: {m.content}"
            for m in recent_messages
        )

        classification = await aget_llm_structured_answer('fast', [
            {
                'role': 'system',
                'content': f"""You are Nora's planning module — the internal reasoning layer for a personal AI assistant. Analyze the latest request in context of the conversation and decide two things: which model tier should answer, and whether fulfilling the request requires calling any of Nora's capabilities.

Available capabilities:
{capability_summary}

Model tiers:
- "fast": cheap, low-latency (simple Q&A, math, text transformation)
- "smart": high reasoning (multi-step planning, complex analysis, research)
- "reasoning": deep chain-of-thought (logic puzzles, debugging, multi-step deduction, architectural decisions)
- "vision": image or visual content understanding

Rules:
- Set "needs_tool" to true only if fulfilling the request genuinely requires one of the capabilities listed above — not for anything answerable directly from general knowledge or conversation
- When "needs_tool" is true, set "capabilities" to the name(s) of every capability from the list above that look relevant — a request can need more than one (e.g. both "filesystem" and "github")
- Any question about Nora's own capabilities, tools, or limitations MUST set "needs_tool" to true and "capabilities" to ["introspect"] — never answer from general knowledge
- If the message is a greeting, filler, acknowledgement, or has no clear task intent (e.g. "hey", "ok", "thanks", "cool"), always use "fast", set "needs_tool" to false, and leave "capabilities" empty
- Choose the tier based on the complexity of the response required, independent of whether a tool is needed

Conversation so far:
{conversation}
"""
            }
        ], PlannerClassification)

        responder_model = classification.responder_model

        if not classification.needs_tool:
            return PlannerOutput(responder_model=responder_model, plan=[])

        relevant_tools: list[BaseTool] = []
        for name in classification.capabilities:
            for tool in tools_by_capability.get(name, []):
                relevant_tools.append(tool)

        ai_message = await aget_llm_tool_call_message('fast', [
            {
                'role': 'system',
                'content': f"""You are Nora's planning module. Based on the conversation, call the tool(s) needed to fulfill the request, with the correct arguments for each.

Conversation so far:
{conversation}
"""
            }
        ], relevant_tools)
        
        logger.debug(f'Tool call response in planner: {ai_message}')

        plan: list[PlanStep] = []
        for call in ai_message.tool_calls:
            call_id = call["id"]
            if call_id is None:
                raise ValueError("tool call missing id")
            plan.append({"tool": call["name"], "input": call["args"], "id": call_id})

        return PlannerOutput(responder_model=responder_model, plan=plan, messages=[ai_message])

    return planner_node
