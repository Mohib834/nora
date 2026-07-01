import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from config.logging import setup_logging
setup_logging()

import aiosqlite
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from agent.graph import build_graph
from agent.nodes.reflect import reflect
from rich.console import Console
from rich.status import Status
from memory.store import MemoryStore
from config.settings import NODE_LABELS, PARALLEL_NODES, THREAD_ID, CONVERSATIONS_DB_PATH


console = Console()


async def main():
    thread_id = THREAD_ID

    store = await MemoryStore.create()
    os.makedirs(os.path.dirname(CONVERSATIONS_DB_PATH), exist_ok=True)

    async with aiosqlite.connect(CONVERSATIONS_DB_PATH) as conn:
        checkpointer = AsyncSqliteSaver(conn)
        app = build_graph(store, checkpointer)

        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "You: ")

                response_content = ""
                responder_started = False
                active_parallel: set[str] = set()
                status = Status("", console=console)
                status.start()

                async for event in app.astream_events(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"thread_id": thread_id}},
                    version="v2",
                ):
                    event_type = event["event"]
                    node_name = event.get("metadata", {}).get("langgraph_node", "")

                    if event_type == "on_chain_start" and event["name"] == node_name and node_name in NODE_LABELS:
                        if node_name in PARALLEL_NODES:
                            active_parallel.add(node_name)
                            label = " and ".join(NODE_LABELS[n] for n in NODE_LABELS if n in active_parallel)
                        elif node_name == "executor":
                            active_parallel.clear()
                            try:
                                input_data = event["data"].get("input") or {}
                                tool_name = input_data["plan"][0]["capability"]
                                label = f"running tool: {tool_name}"
                            except (KeyError, IndexError, TypeError):
                                label = NODE_LABELS[node_name]
                        else:
                            active_parallel.clear()
                            label = NODE_LABELS.get(node_name, node_name)
                        status.update(f"[dim]{label}...[/dim]")

                    elif event_type == "on_chat_model_stream" and node_name == "responder":
                        chunk = event["data"].get("chunk")
                        if chunk and chunk.content:
                            if not responder_started:
                                status.stop()
                                console.print("[bold]Nora:[/bold] ", end="")
                                responder_started = True
                            print(chunk.content, end="", flush=True)
                            response_content += str(chunk.content)

                try:
                    status.stop()
                except Exception:
                    pass

                print()

                # Reflect on the conversation turn and store it in the knowledge graph
                asyncio.create_task(reflect(store, app, {"configurable": {"thread_id": thread_id}}))

        finally:
            await store.close()


if __name__ == "__main__":
    asyncio.run(main())
