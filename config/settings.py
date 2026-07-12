import os
import yaml

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
    "compact": "Running compaction"
}

PARALLEL_NODES: set[str] = {"recall", "planner"}
COMPACT_TOKEN_LEN = 16_000


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "..", "nora.yaml")
    with open(config_path) as f:
        return (yaml.safe_load(f) or {}).get("nora", {})
    
def load_mcps() -> dict:
    default_mcp_path = os.path.join(os.path.dirname(__file__), "mcps.yaml")
    mcp_path =  os.getenv("MCP_CONFIG_PATH", default_mcp_path)
    
    with open(mcp_path) as f:
        return (yaml.safe_load(f) or {}).get("mcps", {})