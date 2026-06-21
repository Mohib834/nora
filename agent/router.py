from .state import AgentState


def should_continue(state: AgentState) -> str:
    plan = state.get('plan', [])
    
    if plan:
        return "executor"
    return "responder"
