# arshi-pa — Personal AI Agent Platform

## Project Vision

**Build Nora — a Jarvis/Friday-style personal AI for Mohib Arshi (Boss).**

Not a chatbot. Not a workflow tool. A persistent, capable, evolving personal AI that knows Boss, remembers everything, and gets smarter over time.

### The End Goal
Nora should feel like Friday from Iron Man:
- Proactive — surfaces information Boss didn't ask for but needs
- Capable — can search, write, manage projects, execute code, control integrations
- Contextual — remembers past conversations, preferences, decisions, and ongoing work
- Self-improving — identifies gaps in her own capabilities and flags or builds new tools

### How We Get There
This is a platform, not a feature. Every piece we build must be general:
- **Capabilities** = reusable tool clusters (research, communication, code execution, calendar)
- **Memory** = persistent context across sessions (Supabase + pgvector)
- **Profiles** = per-project configuration in YAML, never in code
- **Self-improvement** = a meta-capability that inspects the registry, logs unfulfilled requests, and proposes new tools

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

## Technology Stack

- Python 3.13
- LangGraph (graph runtime)
- LangChain (tool/model abstractions)
- FastAPI (API layer — future)
- Supabase + Postgres + pgvector (memory + persistence — future)
- OpenAI / Claude APIs

## Folder Structure

```
arshi-pa/
├── agent/
│   ├── state.py          # AgentState — the heart of the system
│   ├── graph.py          # LangGraph graph assembly
│   ├── nodes/
│   │   ├── planner.py    # Planning node
│   │   ├── executor.py   # Tool execution node
│   │   └── responder.py  # Final response node
│   └── router.py         # Edge routing logic (separate from nodes)
│
├── capabilities/
│   └── web_search/
│       ├── tools.py
│       └── capability.py
│
├── projects/             # Pure config — no code per project
│   └── screenforge.yaml
│
├── memory/               # Phase 2
├── config/
│   └── settings.py
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

## Milestones

### Milestone 1 (Current)
- [ ] Define `AgentState` in `agent/state.py`
- [ ] Establish folder structure
- [ ] Migrate `main.py` skeleton into `agent/graph.py`
- [ ] Create `projects/screenforge.yaml` profile

### Milestone 2
- Planner node (structured plan generation)
- Executor node (single tool)
- Router logic

### Milestone 3
- Real tool integration (web_search)
- Capability wrapper pattern

### Milestone 4
- Memory layer design (Supabase + pgvector)
- Long-term memory retrieval node

### Milestone 5
- FastAPI layer
- Multi-project support

## Review Checklist (Before Each Commit)

- Does the code add Screenforge-specific logic? → Reject, make it general
- Does a new node contain routing logic? → Move to router.py
- Does a new node contain business logic that belongs in a capability? → Refactor
- Is a new project represented as code instead of config? → Convert to YAML
- Is state being mutated outside of nodes? → Fix immediately
