import logging
import os


def setup_logging() -> None:
    os.makedirs("data", exist_ok=True)

    file_handler = logging.FileHandler("data/nora.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))

    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(file_handler)

    for name in ("memory.store", "agent", "agent.nodes.reflect", "config"):
        logging.getLogger(name).setLevel(logging.INFO)

    for name in ("httpx", "httpcore", "openai", "anthropic"):
        logging.getLogger(name).setLevel(logging.WARNING)
