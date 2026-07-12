from langchain.tools import BaseTool

from agent.capabilities.web_search.capability import CAPABILITY as web_search
from agent.capabilities.introspect.capability import make_introspect_capability
from agent.capabilities.types import Capability

NATIVE_CAPABILITIES = [web_search]


def build_all_capabilities(mcp_capabilities: list[Capability]) -> list[Capability]:
    combined = NATIVE_CAPABILITIES + mcp_capabilities
    introspect_capability = make_introspect_capability(combined)
    return combined + [introspect_capability]

def flatten_all_tools(all_capabilities: list[Capability]):
    tools: list[BaseTool] = []
    
    for capability in all_capabilities:
        if capability['tools']:
            for tool in capability['tools']:
                tools.append(tool)
    
    return tools