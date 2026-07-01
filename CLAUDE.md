# arshi-pa — Personal AI Agent Platform

## Project Vision

**Build Nora — a Jarvis/Friday-style personal AI.**

Not a chatbot. Not a workflow tool. A persistent, capable, evolving personal AI that knows the user, remembers everything, and gets smarter over time.

### The End Goal
Nora should feel like Friday from Iron Man:
- Proactive — surfaces information the user didn't ask for but needs
- Capable — can search, write, manage projects, execute code, control integrations
- Contextual — remembers past conversations, preferences, decisions, and ongoing work
- Self-improving — identifies gaps in her own capabilities, writes the code to fix them, and raises a PR

### How We Get There
This is a platform, not a feature. Every piece we build must be general:
- **Capabilities** = reusable tool clusters (research, communication, code execution, calendar)
- **Memory** = persistent context across sessions (Graphiti + FalkorDB Lite)
- **Profiles** = per-project configuration in YAML, never in code
- **Self-improvement** = Nora detects recurring capability gaps, generates the capability code, and opens a PR for human review

The limiting factor is capability breadth and memory depth — not architecture. Keep building.

## Mentorship Rules (CRITICAL — READ FIRST)

This project is being built under active architectural mentorship.

- **Do NOT generate large code blocks unless explicitly asked**
- **Do NOT skip the design/review phase before implementation**
- **Always explain concepts before suggesting code**
- **Always challenge architectural decisions before accepting them**
- **Always ask the user to answer design questions before proceeding**
- **Do NOT ask trivial or obvious follow-up questions** — if the answer is architecturally obvious (e.g. append vs replace for message history), skip it and move forward
- Teaching order matters: State → Nodes → Edges → Routing → Tools → Memory → Persistence → Multi-Agent → Planning

## Architecture Principles

### What to Avoid
- Hardcoded workflows
- Feature-specific agents (no `screenforge_agent.py`, no `seo_agent.py`)
- Single-purpose code
- Routing disguised as planning

### What to Prefer
- General capabilities reusable across all projects
- Tool-based architecture
- Dynamic planning (planner generates a plan, executor follows it)
- Project profiles as pure configuration (YAML/JSON — no code changes per project)
- Long-term memory from day one in design (even if not implemented yet)
- Extensible systems over convenient shortcuts

### Core Distinction: Tools vs Capabilities
- **Tool** = single atomic operation (`search_web`, `send_email`)
- **Capability** = cluster of related tools + business logic (`research`, `communication`)
- The planner thinks at the **capability level**, not the tool level

### Core Distinction: Planner vs Router
- **Router** = picks from a fixed list of paths (switch statement in disguise)
- **Planner** = generates a dynamic execution plan based on intent
- This system uses a **Planner**, not a Router

### Core Distinction: MCP-Bridged vs Native Capabilities
Two types of capabilities — the planner sees no difference:
- **MCP-bridged** = generic operations backed by an MCP server (GitHub, Gmail, Calendar, filesystem). Registered automatically via the MCP bridge from config — zero Python code per integration.
- **Native Python** = capabilities that need AgentState access, memory integration, or have no MCP server (e.g. `introspect`, `memory`, `self_improve`).

Never write a hand-coded capability wrapper just to call an MCP server. That is redundant. Add it to `config/mcps.yaml` instead.

### Core Distinction: Capability vs MCP Tool
- **MCP tool** = raw protocol-exposed function. Stateless. Generic. No awareness of Nora's state.
- **Capability** = opinionated orchestration. Has AgentState access. Adds Nora-specific rules on top of raw tools.
- Use MCP for commodity plumbing. Use native capabilities for Nora-specific intent.

## Technology Stack

- Python 3.13
- LangGraph (graph runtime)
- LangChain (tool/model abstractions)
- FastAPI (API layer — future)
- Graphiti + FalkorDB Lite (long-term semantic memory)
- SQLite via LangGraph `SqliteSaver` (conversation checkpointing — one eternal thread)
- OpenAI / Claude APIs
- `langchain-mcp-adapters` (MCP bridge — future)

## Folder Structure

```
arshi-pa/
├── agent/
│   ├── state.py              # AgentState — the heart of the system
│   ├── graph.py              # LangGraph graph assembly
│   ├── nodes/
│   │   ├── planner.py        # Classify complexity + model tier + dynamic plan — one LLM call
│   │   ├── executor.py       # Tool execution loop
│   │   ├── responder.py      # Nora's voice
│   │   ├── recall.py         # Pulls memory context before planning
│   │   └── reflect.py        # Writes distilled knowledge to memory after response (future)
│   └── router.py             # Edge routing logic (separate from nodes)
│
├── agent/capabilities/
│   ├── registry.py           # All capabilities registered here
│   ├── types.py              # Capability type definitions
│   ├── web_search/
│   │   ├── tools.py
│   │   └── capability.py
│   └── introspect/
│       ├── tools.py
│       └── capability.py
│
├── memory/
│   ├── schema.py             # Graphiti entity types (Person, Goal, Project, Preference,
│   │                         #   CapabilityGap, CapabilityInsight, RunOutcome)
│   └── store.py              # MemoryStore — write_episode, search, close (future)
│
├── config/
│   ├── settings.py           # Model map + file paths (db paths must be mount-safe for server)
│   └── mcps.yaml             # MCP server registry — add integrations here, not in code (future)
│
├── projects/                 # Pure config — no code per project
├── data/                     # Runtime data (gitignored)
│   ├── nora.db               # SQLite — LangGraph conversation checkpointer
│   └── graph/                # FalkorDB Lite — Graphiti knowledge graph (future)
│
└── main.py
```

## LangGraph Principles

- **State is primary** — the graph is not the product, the state is
- Every node: reads state → does work → writes back to state
- Edges decide what runs next based on state
- Never put routing logic inside nodes
- Never put business logic inside edges

## Project Profiles (projects/*.yaml)

Projects are configuration, never code. A profile contains:
- name, goals, audience
- websites, analytics sources
- content style guidelines
- important documents / knowledge sources

The same capability system must work for every project without code changes.

## Graph Structure

```
START → recall → planner → executor (loop) → responder → reflect → compact → END
```

- **recall** — pulls relevant long-term memory into `state['memory_context']` before planning
- **planner** — single LLM call: classifies complexity, assigns `responder_model`, generates execution plan. Returns `[]` plan for simple requests, skipping executor entirely.
- **executor** — runs tools, loops until plan is complete
- **responder** — synthesizes results and replies as Nora
- **reflect** — LLM call that distills the run into Graphiti episodes (MUST run before compact)
- **compact** — trims message history to prevent context overflow

**Thread model:** One eternal thread. Single constant `thread_id`. No session boundaries.
Nora is always-on — she doesn't reset between conversations.

## Memory Architecture

Two complementary layers:

| Layer | Technology | What it stores |
|---|---|---|
| Conversation checkpointing | SQLite + LangGraph `SqliteSaver` | Full message history for the current thread |
| Long-term semantic memory | Graphiti + FalkorDB Lite | Distilled knowledge — entities, relationships, capability gaps |

**Entity types** (`memory/schema.py`): `Person`, `Goal`, `Project`, `Preference`, `CapabilityGap`, `CapabilityInsight`, `RunOutcome`

**Reflect runs before compact** — if compact runs first, reflect loses the raw detail it needs.

**FalkorDB Lite path must be configurable** in `config/settings.py` so it can be volume-mounted on a server deployment.

## Self-Improvement Loop (Future)

```
1. reflect node detects failure → writes CapabilityGap episode
2. Graphiti accumulates gaps → extracts CapabilityInsight
3. recall surfaces high-priority insights to the planner
4. self_improve capability:
   a. reads CapabilityInsight.suggested_capability from memory
   b. reads existing capability patterns from the codebase
   c. generates new tools.py + capability.py following the pattern
   d. uses github MCP to create a branch, commit files, open a PR
5. Human reviews and merges — Nora never merges her own code
```

## MCP Integration Pattern (Future)

MCP servers are registered in `config/mcps.yaml` — not in Python code.
A generic MCP bridge reads this config at startup and auto-registers tools into the capability registry.

```yaml
# config/mcps.yaml
mcps:
  - name: github
    description: "Create branches, commit files, open PRs"
  - name: gmail
    description: "Read and send emails"
  - name: google-calendar
    description: "Read and create calendar events"
```

**Never write a hand-coded Python wrapper just to call an MCP server.** Config is enough.

## Latency & Performance

Every request goes through sequential LLM API calls — each one adds 500-1000ms. The goal is to reduce the number of sequential hops, move work off the critical path, and eventually eliminate latency by having answers ready before the user asks.

### Completed Optimizations
- **Merged classifier + planner** — was 2 sequential LLM calls (classify → plan), now 1. Simple requests: 2 total LLM calls (planner + responder). Complex: 3 (planner + tools + responder).
- **`astream_events` with `on_chain_start`** — node labels now show when a node begins, not when it ends. UI reflects real-time state.

### Planned Optimizations
- **Parallelize recall + planner** — recall and planner have no dependency (planner doesn't use `memory_context` yet). Run them simultaneously via LangGraph fan-out. Saves one full sequential hop on every request.
- **Tool result caching** — cache executor results with a TTL. Identical tool calls (same capability + input) within a window return the cached result. Zero tool latency on repeated queries.
- **Adaptive plan caching** — after enough turns, Nora recognises recurring request patterns and reuses their plans directly, skipping the planner call.

### Friday-Style: Moving Work Off the Critical Path
The deeper fix isn't faster responses — it's making the question irrelevant by having the answer ready before it's asked.

- **Streaming input + early pipeline start** — begin recall + planning as the user types, not after Enter. By the time they submit, part of the work is done. This hides latency behind typing time.
- **Predictive pre-planning** — after each response, predict the 2-3 most likely follow-up questions and pre-run their plans in the background. When the user asks, the plan is already computed.
- **Push model** — for known recurring needs (morning briefing, email digest, project status), pre-compute and surface proactively. Zero request latency because the answer already exists.

### Embedding Model
Graphiti uses OpenAI `text-embedding-3-small` by default (network call per recall). Local alternative: `nomic-embed-text` via Ollama (~137M params, ~274MB VRAM, CPU-capable). Quality is comparable for conversational memory retrieval. **Switching embedding models requires re-embedding all existing graph data** — the two vector spaces are incompatible. Migrate only when the memory store is empty or schedule a full re-index. Once recall is parallelized with planner, embedding latency is off the critical path anyway — the primary reason to switch becomes cost and data privacy, not speed.

## Milestones

### Milestone 1 ✅
- [x] Define `AgentState` in `agent/state.py`
- [x] Establish folder structure
- [x] Graph: planner → executor → responder
- [x] Web search capability
- [x] Introspect capability (Nora knows her own tools)
- [x] SQLite conversation persistence (one eternal thread)
- [x] Merged classifier into planner — single LLM call for model tier + plan

### Milestone 2 (Current)
- [x] `memory/store.py` — MemoryStore with FalkorDB Lite + Graphiti
- [x] `agent/nodes/recall.py` — pull memory context before planning
- [x] Add `memory_context` to `AgentState`
- [x] Wire recall into `graph.py`
- [ ] `agent/nodes/reflect.py` — distill run into Graphiti after response
- [ ] Wire reflect into `graph.py`
- [ ] Pass `memory_context` into planner prompt

### Milestone 3
- MCP bridge — generic config-driven integration layer (`config/mcps.yaml`)
- GitHub MCP integration (for self-improvement PR flow)
- `compact` node — context window management
- Parallelize recall + planner (LangGraph fan-out)
- Tool result caching in executor

### Milestone 4
- `self_improve` capability — reads CapabilityInsight, generates code, raises PR
- FastAPI layer — expose Nora as an API
- Adaptive plan caching

### Milestone 5
- Multi-project profile support (`projects/*.yaml`)
- Communication gateway (OpenClaw-style — connect Nora to WhatsApp/Telegram)
- Streaming input + predictive pre-planning

## Review Checklist (Before Each Commit)

- Does the code add Screenforge-specific logic? → Reject, make it general
- Does a new node contain routing logic? → Move to router.py
- Does a new node contain business logic that belongs in a capability? → Refactor
- Is a new project represented as code instead of config? → Convert to YAML
- Is state being mutated outside of nodes? → Fix immediately
