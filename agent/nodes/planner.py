import json
from typing import TypedDict

from ..state import AgentState
from utils.llm import get_llm_answer
from ..capabilities.registry import ALL_CAPABILITIES


class PlanStep(TypedDict):
    capability: str
    input: str


class PlannerOutput(TypedDict):
    responder_model: str
    plan: list[PlanStep]


def planner_node(state: AgentState) -> PlannerOutput:
    recent_messages = state['messages'][-6:]
    conversation = "\n".join(
        f"{'User' if m.type == 'human' else 'Nora'}: {m.content}"
        for m in recent_messages
    )

    capabilities_str = "\n".join(
        f"- {c['name']}: {c['description']}" for c in ALL_CAPABILITIES
    )

    result_json = get_llm_answer('fast', [
        {
            'role': 'system',
            'content': f"""You are Nora's planning module — the internal reasoning layer for a personal AI assistant. Analyze the latest request in context of the conversation, assign the right response model, and produce a structured execution plan.

Available capabilities:
{capabilities_str}

Model tiers:
- "fast": cheap, low-latency (simple Q&A, math, text transformation)
- "smart": high reasoning (multi-step planning, complex analysis, research)
- "reasoning": deep chain-of-thought (logic puzzles, debugging, multi-step deduction, architectural decisions)
- "vision": image or visual content understanding

Rules:
- Only use capabilities from the list above
- Think step by step about what is needed to fulfill the request
- If the request needs no external action (e.g. simple Q&A, math, writing, general knowledge), return an empty plan array
- Any question about Nora's own capabilities, tools, or limitations MUST use the introspect capability — never answer from general knowledge
- Keep steps minimal — don't add steps that aren't necessary
- Output raw JSON only, no explanation

Output format:
{{
    "responder_model": "fast" | "smart" | "vision",
    "plan": [
        {{"capability": "<capability_name>", "input": "<what to pass to it>"}}
    ]
}}

Conversation so far:
{conversation}
"""
        }
    ])

    try:
        clean = (result_json or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(clean) if clean else {}
    except json.JSONDecodeError:
        result = {}

    return PlannerOutput(
        responder_model=result.get('responder_model', 'fast'),
        plan=result.get('plan', []),
    )
