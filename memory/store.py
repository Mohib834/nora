import logging
import os
from datetime import datetime, timezone

from redislite.async_falkordb_client import AsyncFalkorDB
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from config.settings import FALKORDB_DB_PATH, FALKORDB_DATABASE
from memory.schema import ENTITY_TYPES

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self, graphiti: Graphiti):
        self.graphiti = graphiti

    @classmethod
    async def create(cls) -> "MemoryStore":
        logger.info(f"Initializing embedded FalkorDB at {FALKORDB_DB_PATH}")
        os.makedirs(os.path.dirname(FALKORDB_DB_PATH), exist_ok=True)
        db = AsyncFalkorDB(dbfilename=FALKORDB_DB_PATH)
        driver = FalkorDriver(falkor_db=db, database=FALKORDB_DATABASE)

        graphiti = Graphiti(graph_driver=driver)

        logger.info("Building indices and constraints...")
        await graphiti.build_indices_and_constraints()
        logger.info("MemoryStore ready")

        return cls(graphiti)

    async def close(self):
        logger.info("Closing MemoryStore...")

        await self.graphiti.close()

        logger.info("MemoryStore closed")

    async def write_episode(
        self,
        name: str,
        episode_body: str,
        source_description: str,
    ) -> None:
        logger.info(f"Writing episode: {name}")
        logger.info(f"Episode body: {episode_body}")

        try:
            await self.graphiti.add_episode(
                name=name,
                episode_body=episode_body,
                source_description=source_description,
                reference_time=datetime.now(timezone.utc),
                entity_types=ENTITY_TYPES,
            )
            logger.info(f"Episode written successfully: {name}")
        except Exception as e:
            logger.error(f"Failed to write episode '{name}': {e}")

    async def search(self, content: str, limit: int = 5) -> list[str]:
        logger.info(f"Searching memory: '{content[:50]}' limit={limit}")

        result = await self.graphiti.search(content, num_results=limit)

        logger.info(f"Found {len(result)} memories")

        return [r.fact for r in result]
