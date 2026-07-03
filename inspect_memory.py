import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()

from memory.store import MemoryStore


async def main(query: str | None, limit: int = 50) -> None:
    store = await MemoryStore.create()

    try:
        data = await store.debug_graph()

        print("\n=== NODES ===")
        for row in data["nodes"]:
            print(row)

        print("\n=== EDGES ===")
        for row in data["edges"]:
            print(row)

        if query:
            print(f"\n=== SEARCH: '{query}' ===")
            results = await store.search(content=query, limit=limit)
            if results:
                for i, fact in enumerate(results, 1):
                    print(f"[{i}] {fact}")
            else:
                print("No results found")
    finally:
        await store.close()


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        query = None
        limit = 50
    elif len(args) == 1 and args[0].isdigit():
        query = None
        limit = int(args[0])
    elif len(args) == 1:
        query = args[0]
        limit = 50
    else:
        query = args[0]
        limit = int(args[1])

    asyncio.run(main(query, limit))
