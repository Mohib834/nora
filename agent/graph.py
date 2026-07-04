from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from .state import AgentState
from .nodes.planner import planner_node
from .nodes.executor import executor_node
from .nodes.responder import responder_node
from .nodes.dispatch import dispatch_node
from .router import should_continue
from memory.store import MemoryStore
from agent.nodes.recall import make_recall_node
from agent.nodes.compact import compact_node

def build_graph(store: MemoryStore, checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
    recall_node = make_recall_node(store)

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("responder", responder_node)
    graph.add_node("recall", recall_node)
    graph.add_node('dispatch', dispatch_node)
    graph.add_node('compact', compact_node)

    graph.add_edge(START, "recall")
    graph.add_edge(START, "planner")

    graph.add_edge("recall", "dispatch")
    graph.add_edge("planner", "dispatch")

    graph.add_conditional_edges("dispatch", should_continue)
    graph.add_conditional_edges("executor", should_continue)
    
    graph.add_edge('responder', 'compact')
    graph.add_edge('compact', END)

    return graph.compile(checkpointer=checkpointer)
