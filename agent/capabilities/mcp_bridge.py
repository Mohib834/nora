from langchain_mcp_adapters.client import MultiServerMCPClient
from config.settings import load_mcps
import logging
from agent.capabilities.types import Capability
import os

logger = logging.getLogger(__name__)

async def load_mcp_capabilities() -> list[Capability]:
    mcps = load_mcps()
    capabilities = []

    for mcp in mcps:
        envs = {}
        missing_env = None
        
        for env in mcp.get('env_vars', []):
            value = os.environ.get(env)
            envs[env] = value
            
            if not value:
                missing_env = env
                break
        
        if missing_env:
            logger.warning(f'Missing env value: {missing_env} for this mcp: {mcp['name']}')
            continue

        try:
            client = MultiServerMCPClient(connections={
                mcp['name']: {
                    'command': mcp['command'],
                    'args': mcp['args'],
                    'transport': mcp['transport'],
                    'env': envs
                }
            })
            
            tools = await client.get_tools()
            capabilities.append(Capability(name=mcp['name'], description=mcp['description'], tools=tools))
 
        except Exception as e:
            logger.warning(f'failed to load the tool call: {mcp['name']}: {e}')
            continue
        
    return capabilities