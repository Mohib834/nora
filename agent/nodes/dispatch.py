from agent.state import AgentState
from typing import TypedDict

class DispatchNodeOutput(TypedDict):
    pass

def dispatch_node(state: AgentState) -> DispatchNodeOutput:
    ''' A sync node for fan out handling for parallel nodes.(Use if next node is behind conditional routing) '''
    return DispatchNodeOutput()



