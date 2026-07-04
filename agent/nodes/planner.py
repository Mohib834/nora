import json
from ..state import AgentState
from typing import TypedDict
from utils.llm import get_llm_answer
from config.settings import MODEL_MAP, DEFAULT_MODEL
from ..capabilities.registry import ALL_CAPABILITIES


class PlanStep(TypedDict):
    capability: str
    input: str

class PlannerOutput(TypedDict):
    plan: list[PlanStep]

def planner_node(state: AgentState) -> PlannerOutput:
    tier = state.get('planner_model', DEFAULT_MODEL)
    model = MODEL_MAP.get(tier, MODEL_MAP[DEFAULT_MODEL])
    last_msg = state['messages'][-1].content

    capabilities_str = "\n".join(
        f"- {c['name']}: {c['description']}" for c in ALL_CAPABILITIES
    )

    result_json = get_llm_answer(model, [
        {
         'role': 'system',
         'content': f"""You are Nora's planning module — the internal reasoning layer for a personal AI assistant serving Mohib Arshi (Boss). Analyze the request and produce a structured execution plan.

        Available capabilities:
        {capabilities_str}

        Rules:
        - Only use capabilities from the list above
        - Think step by step about what is needed to fulfill the request
        - If the request needs no external action (e.g. simple Q&A, math, writing, general knowledge), return an empty array
        - Any question about Nora's own capabilities, tools, or limitations MUST use the introspect capability — never answer from general knowledge
        - Keep steps minimal — don't add steps that aren't necessary
        - Output raw JSON only, no explanation

        Output a JSON array of steps:
        [
            {{"capability": "<capability_name>", "input": "<what to pass to it>"}}
        ]

        User request: {last_msg}
        """
        }
    ])

    try:
        clean = (result_json or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        plan = json.loads(clean) if clean else []
    except json.JSONDecodeError:
        plan = []
    return PlannerOutput(plan=plan)
