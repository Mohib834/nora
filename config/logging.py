import logging
import os


def setup_logging() -> None:
    debug = os.getenv("DEBUG", "false").lower() in ("1", "true")

    logging.basicConfig(level=logging.WARNING, format="%(name)s | %(levelname)s | %(message)s")

    if debug:
        for name in ("memory.store", "agent", "agent.nodes.reflect", "config"):
            logging.getLogger(name).setLevel(logging.INFO)
