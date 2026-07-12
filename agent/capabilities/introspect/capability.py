from .tools import make_get_capabilities_tool
from ..types import Capability


def make_introspect_capability(other_capabilities: list[Capability]) -> Capability:
    name = 'introspect'
    description = "Inspect Nora's own capabilities, active execution context, and known project profiles"
    tool = make_get_capabilities_tool(other_capabilities, {'name': name, 'description': description})

    return Capability(name=name, description=description, tools=[tool])