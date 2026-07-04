from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessageChunk
from agent.graph import app
from rich.console import Console
from rich.status import Status


console = Console()

NODE_LABELS = {
    "classifier": "analyzing request",
    "planner": "generating plan",
    "executor": "running tool",
    "responder": "responding",
}

def main():
    thread_id = 'thread-1'

    while True:
        user_input = input("You: ")

        response_content = ""
        responder_started = False
        status = Status("", console=console)
        status.start()

        try:
          stream = app.stream(
              {"messages": [HumanMessage(content=user_input)]},
              config={"configurable": {"thread_id": thread_id}},
              stream_mode=["messages", "updates"],
          )
        except Exception as e:
            status.stop()
            console.print(f"[red]Error:[/red] {e}")
            continue

        try:
            for stream_mode, data in stream:
                if stream_mode == "updates" and isinstance(data, dict):
                    node = list(data.keys())[0]
                    if node != "responder":
                        label = NODE_LABELS.get(node, node)
                        if node == "executor":
                            tool_name = data[node].get("current_tool", "")
                            label = f"running tool: {tool_name}"
                        status.update(f"[dim]{label}...[/dim]")

                elif stream_mode == "messages":
                    chunk, metadata = data
                    if (
                        isinstance(chunk, AIMessageChunk)
                        and chunk.content
                        and isinstance(metadata, dict)
                        and metadata.get("langgraph_node") == "responder"
                    ):
                        if not responder_started:
                            status.stop()
                            console.print("[bold]Nora:[/bold] ", end="")
                            responder_started = True
                        print(chunk.content, end="", flush=True)
                        response_content += str(chunk.content)
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}")

        try:
            status.stop()
        except Exception:
            pass

        print()

if __name__ == "__main__":
    main()
