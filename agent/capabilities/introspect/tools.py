#   # get_active_context
#   """Returns Nora's current execution state — the active plan and the tool being run, if any."""

#   # get_project_profiles
#   """Returns all known project profiles from the projects directory, including their names and goals."""
  
from langchain.tools import tool

@tool
def get_capabilities():
    """Returns all registered capabilities Nora can currently invoke, including their names and descriptions."""
   
    from agent.capabilities.registry import ALL_CAPABILITIES
    return [{'name': capability['name'], 'description': capability['description']} for capability in ALL_CAPABILITIES]
   
   

