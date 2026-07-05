import logging
import os
from datetime import datetime, timezone

from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from langsmith import traceable
from redislite.async_falkordb_client import AsyncFalkorDB

from config.settings import FALKORDB_DATABASE, FALKORDB_DB_PATH, load_config
from memory.schema import ENTITY_TYPES

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self, graphiti: Graphiti, db: AsyncFalkorDB):
        self.graphiti = graphiti
        self.db = db

    @classmethod
    async def create(cls) -> "MemoryStore":
        logger.info(f"Initializing embedded FalkorDB at {FALKORDB_DB_PATH}")
        os.makedirs(os.path.dirname(FALKORDB_DB_PATH), exist_ok=True)

        db = AsyncFalkorDB(dbfilename=FALKORDB_DB_PATH)
        driver = FalkorDriver(falkor_db=db, database=FALKORDB_DATABASE)

        _models = load_config().get("models", {})
        llm_client = OpenAIClient(
            config=LLMConfig(
                model=_models.get("smart", "gpt-5.4"),
                small_model=_models.get("fast", "gpt-5.4-nano"),
            ),
            reasoning="",
        )
        llm_client.verbosity = None  # verbosity guard is `is not None`, so None skips the param
        embedder = OpenAIEmbedder(config=OpenAIEmbedderConfig())

        graphiti = Graphiti(graph_driver=driver, llm_client=llm_client, embedder=embedder)

        logger.info("Building indices and constraints...")
        await graphiti.build_indices_and_constraints()
        logger.info("MemoryStore ready")

        return cls(graphiti, db)

    async def close(self):
        logger.info("Closing MemoryStore...")

        try:
            await self.db.client.bgsave()
            logger.info("MemoryStore: data saved to disk")
        except Exception as e:
            logger.warning(f"MemoryStore: save failed: {e}")

        await self.graphiti.close()

        logger.info("MemoryStore closed")

    @traceable(run_type="chain", name="memory.write_episode")
    async def write_episode(self, name: str, episode_body: str, source_description: str) -> None:
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
            await self.db.client.bgsave()
        except Exception as e:
            logger.error(f"Failed to write episode '{name}': {e}")

    async def get_all_facts(self, limit: int = 50) -> list[str]:
        result = await self.graphiti.driver.execute_query(
            f"MATCH (n:Entity)-[e:RELATES_TO]->(m:Entity) WHERE e.fact IS NOT NULL RETURN e.fact ORDER BY e.created_at DESC LIMIT {limit}"
        )
        facts = []
        for row in result:
            item = row[0] if isinstance(row, (list, tuple)) else row
            if isinstance(item, dict) and item.get("e.fact"):
                facts.append(item["e.fact"])
        return facts

    async def debug_graph(self) -> dict:
        nodes = await self.graphiti.driver.execute_query(
            "MATCH (n) RETURN labels(n) AS labels, n.name AS name, n.fact AS fact LIMIT 100"
        )
        edges = await self.graphiti.driver.execute_query(
            "MATCH ()-[e]->() RETURN type(e) AS rel, e.fact AS fact LIMIT 100"
        )
        return {"nodes": nodes, "edges": edges}

    @traceable(run_type="retriever", name="memory.search")
    async def search(self, content: str, limit: int = 5) -> list[str]:
        logger.info(f"Searching memory: '{content[:50]}' limit={limit}")

        result = await self.graphiti.search(content, num_results=limit)

        logger.info(f"Found {len(result)} memories")

        return [r.fact for r in result]
