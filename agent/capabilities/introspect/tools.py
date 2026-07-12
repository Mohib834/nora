#   # get_active_context
#   """Returns Nora's current execution state — the active plan and the tool being run, if any."""

#   # get_project_profiles
#   """Returns all known project profiles from the projects directory, including their names and goals."""
  
from langchain.tools import tool

def make_get_capabilities_tool(other_capabilities, self_entry):
    @tool
    def get_capabilities():
        """Returns all registered capabilities Nora can currently invoke, including their names and descriptions."""
        entries = [{'name': c['name'], 'description': c['description']} for c in other_capabilities]
        entries.append(self_entry)
        return entries

    return get_capabilities
   
   

