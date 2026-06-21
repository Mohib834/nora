from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes.classifier import classifier_node
from .nodes.planner import planner_node
from .nodes.executor import executor_node
from .nodes.responder import responder_node
from .router import should_continue

graph = StateGraph(AgentState)

graph.add_node("classifier", classifier_node)
graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("responder", responder_node)

graph.add_edge(START, "classifier")
graph.add_edge("classifier", "planner")
graph.add_conditional_edges("planner", should_continue)
graph.add_conditional_edges("executor", should_continue)

app = graph.compile()
