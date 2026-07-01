import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()

from memory.store import MemoryStore


async def main(query: str, limit: int = 10) -> None:
    store = await MemoryStore.create()

    try:
        results = await store.search(content=query, limit=limit)

        if not results:
            print(f"No results found for '{query}'")
            return

        print(f"\n{len(results)} result(s) for '{query}':\n")

        for i, fact in enumerate(results, 1):
            print(f"[{i}] {fact}")
            print()
    finally:
        await store.close()


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        query = "Boss"
        limit = 10
    elif len(args) == 1 and args[0].isdigit():
        query = "Boss"
        limit = int(args[0])
    elif len(args) == 1:
        query = args[0]
        limit = 10
    else:
        query = args[0]
        limit = int(args[1])

    asyncio.run(main(query, limit))
