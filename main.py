import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from config.logging import setup_logging
setup_logging()

import aiosqlite
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
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

        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "You: ")

                response_content = ""
                responder_started = False
                nora_header_printed = False
                active_parallel: set[str] = set()
                think_buffer = ""
                in_think = False
                status = Status("", console=console)
                status.start()

                async for event in app.astream_events(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config,
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
                                responder_started = True

                            think_buffer += str(chunk.content)

                            while think_buffer:
                                if not in_think:
                                    if "<think>" in think_buffer:
                                        idx = think_buffer.index("<think>")
                                        prefix = think_buffer[:idx]
                                        if prefix:
                                            if not nora_header_printed:
                                                console.print("[bold]Nora:[/bold] ", end="")
                                                nora_header_printed = True
                                            print(prefix, end="", flush=True)
                                            response_content += prefix
                                        in_think = True
                                        console.print("\n[dim]▸ thinking[/dim]")
                                        think_buffer = think_buffer[idx + 7:]
                                    else:
                                        safe = think_buffer[:-7] if len(think_buffer) > 7 else ""
                                        if safe:
                                            if not nora_header_printed:
                                                console.print("[bold]Nora:[/bold] ", end="")
                                                nora_header_printed = True
                                            print(safe, end="", flush=True)
                                            response_content += safe
                                            think_buffer = think_buffer[len(safe):]
                                        break
                                else:
                                    if "</think>" in think_buffer:
                                        idx = think_buffer.index("</think>")
                                        think_text = think_buffer[:idx]
                                        if think_text:
                                            console.print(think_text, style="dim", end="")
                                        think_buffer = think_buffer[idx + 9:]
                                        in_think = False
                                        console.print()
                                        if not nora_header_printed:
                                            console.print("[bold]Nora:[/bold] ", end="")
                                            nora_header_printed = True
                                    else:
                                        safe = think_buffer[:-9] if len(think_buffer) > 9 else ""
                                        if safe:
                                            console.print(safe, style="dim", end="")
                                            think_buffer = think_buffer[len(safe):]
                                        break

                try:
                    status.stop()
                except Exception:
                    pass

                if think_buffer:
                    if in_think:
                        console.print(think_buffer, style="dim", end="")
                    else:
                        if not nora_header_printed:
                            console.print("[bold]Nora:[/bold] ", end="")
                        print(think_buffer, end="", flush=True)
                        response_content += think_buffer

                print()

                # Reflect on the conversation turn and store it in the knowledge graph
                asyncio.create_task(reflect(store, app, config))

        finally:
            await store.close()


if __name__ == "__main__":
    asyncio.run(main())
