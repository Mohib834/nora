from typing import TypedDict
from langchain.tools import BaseTool

class Capability(TypedDict):
    name: str
    description: str
    tools: list[BaseTool]
