# Nora

**An open-source, capability-driven personal AI platform. Build your own Friday.**

Nora is not a chatbot. Not a workflow tool. A persistent, capable, evolving personal AI — designed to feel like Friday from Iron Man. She plans, executes, remembers across sessions, and gets smarter over time.

---

## How it works

Every request flows through a graph. `recall` and `planner` run **in parallel** from the start, join at a barrier, then route to the executor loop or straight to the responder. After Nora replies, `compact` trims the conversation window, then `reflect` distills the turn into long-term memory — off the critical path, so it never slows the response.

```mermaid
graph LR
    A([User]) --> R[Recall]
    A --> P[Planner]
    R --> D[Dispatch]
    P --> D
    D -->|has plan| E[Executor]
    D -->|no tools needed| RE[Responder]
    E -->|more steps| E
    E -->|plan complete| RE
    RE --> C[Compact]
    C --> N([Nora])
    C -.background.-> RF[Reflect]
    RF -.writes.-> M[(Knowledge Graph)]
```

- **Recall** — searches long-term memory and loads relevant context into state before Nora responds (runs in parallel with the planner)
- **Planner** — a single LLM call that classifies complexity, assigns a model tier (fast / smart / vision), and generates a dynamic execution plan. Returns an empty plan for simple requests, skipping the executor entirely
- **Dispatch** — a sync barrier that joins the parallel `recall` + `planner` branches before routing
- **Executor** — runs the planned capabilities, looping until the plan is complete
- **Responder** — synthesizes results and replies as Nora, streaming token-by-token
- **Compact** — after the reply, counts tokens in the conversation window using `tiktoken` and drops the oldest messages when the thread exceeds the threshold (16K tokens by default). Keeps costs flat and prevents context overflow as the thread grows
- **Reflect** — distills the turn (intent, outcome, capability gaps) into the knowledge graph as a background task — runs after compact, never blocks the response

The graph is built on [LangGraph](https://github.com/langchain-ai/langgraph). State flows through every node — no hidden side effects.

---

## Memory

Nora has two complementary memory layers:

| Layer | Technology | What it stores |
|---|---|---|
| Conversation checkpointing | SQLite + LangGraph `AsyncSqliteSaver` | Full message history for the current thread |
| Long-term semantic memory | [Graphiti](https://github.com/getzep/graphiti) + embedded FalkorDB | Distilled knowledge — entities, relationships, capability gaps |

**One eternal thread.** Nora is always-on. A single constant `thread_id` — no session boundaries, no reset between conversations.

The knowledge graph tracks seven entity types (`memory/schema.py`): `Person`, `Goal`, `Project`, `Preference`, `CapabilityGap`, `CapabilityInsight`, `RunOutcome`. `CapabilityGap` and `CapabilityInsight` are the foundation of the self-improvement loop — Nora records what she couldn't do so she can learn what to build next.

---

## Architecture

```
nora/
├── agent/
│   ├── state.py              # AgentState — the heart of the system
│   ├── graph.py              # LangGraph graph assembly (parallel fan-out + barrier)
│   ├── router.py             # Edge routing logic
│   ├── nodes/
│   │   ├── recall.py         # Pulls long-term memory before responding
│   │   ├── planner.py        # Model tier + dynamic plan (one LLM call)
│   │   ├── dispatch.py       # Sync barrier joining the parallel branches
│   │   ├── executor.py       # Tool execution loop
│   │   ├── responder.py      # Nora's voice
│   │   ├── compact.py        # Token-based context window trimming (post-response)
│   │   └── reflect.py        # Distills each turn into the knowledge graph (background)
│   └── capabilities/
│       ├── registry.py       # All capabilities registered here
│       ├── types.py          # Capability type definition
│       ├── web_search/       # Search the web
│       └── introspect/       # Nora inspects her own capabilities
│
├── memory/
│   ├── schema.py             # Graphiti entity types
│   └── store.py              # MemoryStore — write_episode, search, close
│
├── config/
│   ├── settings.py           # Model map + DB paths + thread config
│   └── logging.py            # Logging setup
│
├── projects/                 # Per-project config (YAML only, no code)
├── data/                     # Runtime data (gitignored) — SQLite + FalkorDB
└── main.py                   # CLI entrypoint
```

### Core principles

- **State is primary** — the graph is not the product, the state is
- **Capabilities, not features** — every tool cluster is general and reusable
- **Planner, not router** — Nora generates dynamic plans, not switch statements
- **Memory from day one** — recall before, reflect after, on every turn
- **Projects as config** — YAML profiles, zero code changes per project

---

## Getting started

**Requirements:** Python 3.13+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/yourusername/nora.git
cd nora
uv sync
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here       # required if using OpenAI models
ANTHROPIC_API_KEY=your_key_here    # required if using Claude models
TAVILY_API_KEY=your_key_here
```

Optional overrides (sensible defaults are used if unset):

```env
CONVERSATIONS_DB_PATH=data/nora_conversations.db
FALKORDB_DB_PATH=data/graph/nora_knowledge.db
THREAD_ID=thread-1
```

Nora supports both OpenAI and Anthropic out of the box. Switch providers by editing the `models` section in `nora.yaml` — use `gpt-4o-mini` for OpenAI or `anthropic/claude-haiku-4-5-20251001` for Anthropic.

Run Nora:

```bash
uv run main.py
```

FalkorDB runs **embedded** (via `redislite`) — no separate database server to start. The knowledge graph and conversation history are persisted under `data/`.

---

## Capabilities

| Capability | What it does |
|---|---|
| `web_search` | Search the internet for up-to-date information |
| `introspect` | Inspect Nora's own capabilities, execution context, and known project profiles |

More capabilities coming. Contributions welcome.

---

## Roadmap

- [x] Recall ∥ Planner → Executor → Responder graph
- [x] Web search capability
- [x] Introspect capability (Nora knows her own tools)
- [x] Dynamic model tier selection
- [x] Merged classifier into planner (single LLM call)
- [x] Long-term semantic memory (Graphiti + embedded FalkorDB)
- [x] Recall node — memory context before responding
- [x] Reflect node — distill each turn into the knowledge graph
- [x] SQLite conversation persistence (one eternal thread)
- [x] `compact` node — token-based context window management
- [ ] MCP bridge — config-driven integrations (`config/mcps.yaml`)
- [ ] Self-improvement — Nora detects capability gaps, writes the code, opens a PR
- [ ] FastAPI layer
- [ ] Multi-project profile support

---

## Adding a capability

1. Create `agent/capabilities/your_capability/tools.py` — define your tools
2. Create `agent/capabilities/your_capability/capability.py` — export a `CAPABILITY` dict
3. Register it in `agent/capabilities/registry.py`

That's it. The planner picks it up automatically.

---

## Stack

- Python 3.13
- [LangGraph](https://github.com/langchain-ai/langgraph) — graph runtime + SQLite checkpointing
- [LangChain](https://github.com/langchain-ai/langchain) — tool/model abstractions
- [Graphiti](https://github.com/getzep/graphiti) + FalkorDB Lite (embedded) — long-term semantic memory
- OpenAI API — model tier configured in `nora.yaml` (fast / smart / reasoning / vision)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- OpenAI API (GPT-4o / GPT-4o-mini) or Anthropic API (Claude Haiku / Sonnet)
- Tavily (web search)

---

## License

MIT
