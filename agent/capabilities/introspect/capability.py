from .tools import get_capabilities
from ..types import Capability

CAPABILITY = Capability(
    name='introspect', 
    description='Inspect Nora\'s own capabilities, active execution context, and known project profiles', 
    tools=[get_capabilities] 
)