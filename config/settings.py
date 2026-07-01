import os

MODEL_MAP = {
    "fast": "gpt-4o-mini",
    "smart": "gpt-4o",
    "vision": "gpt-4o",
}

DEFAULT_MODEL = "fast"

CONVERSATIONS_DB_PATH = os.getenv("CONVERSATIONS_DB_PATH", "data/nora_conversations.db")
FALKORDB_DB_PATH = os.getenv("FALKORDB_DB_PATH", "data/graph/nora_knowledge.db")
FALKORDB_DATABASE = os.getenv("FALKORDB_DATABASE", "nora_graph")

THREAD_ID = os.getenv("THREAD_ID", "thread-1")

NODE_LABELS: dict[str, str] = {
    "recall": "Recalling past memory",
    "planner": "planning",
    "executor": "Running tool",
    "responder": "Responding",
}

PARALLEL_NODES: set[str] = {"recall", "planner"}