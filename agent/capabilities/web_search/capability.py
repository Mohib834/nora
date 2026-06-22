from .tools import search_web
from ..types import Capability

CAPABILITY = Capability(
    name='web_search', 
    description='Search the internet for up-to-date information', 
    tools=[search_web] 
)