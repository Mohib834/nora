import json

from ..state import AgentState
from utils.llm import get_llm_answer
from config.settings import DEFAULT_MODEL, MODEL_MAP
from typing import TypedDict

class ClassifierOutput(TypedDict):
    planner_model: str
    responder_model: str

def classifier_node(state: AgentState) -> ClassifierOutput:
    """ Classifies request complexity and assigns model tiers to state """

    last_msg_content = state['messages'][-1].content

    result_json = get_llm_answer(MODEL_MAP[DEFAULT_MODEL], [
        {"role": 'system',
         "content": f'''
            Classify the user's request and assign the appropriate model tier for each stage.

            Model tiers:
            - "fast": cheap, low-latency (simple Q&A, math, text transformation)
            - "smart": high reasoning (multi-step planning, complex analysis)
            - "vision": image or visual content understanding

            Simple request: single-step, no external data needed
            Complex request: multi-step, requires search, files, or planning

            Output a single JSON object:
            {{
                "complexity": "simple" | "complex",
                "planner_model": "fast" | "smart" | "vision",
                "responder_model": "fast" | "smart" | "vision"
            }}

            User request: {last_msg_content}

            Output raw JSON only. No explanation.
            '''
         }
    ])

    if not result_json:
        return ClassifierOutput(planner_model=DEFAULT_MODEL, responder_model=DEFAULT_MODEL)

    result = json.loads(result_json)

    return ClassifierOutput(
        planner_model=result['planner_model'],
        responder_model=result['responder_model']
    )

    


