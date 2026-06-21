from langchain.tools import tool
from langchain_tavily import TavilySearch

@tool
def search_web(query: str):
    """ Use this tool to search web """
    
    tavily_search = TavilySearch(max_results=5, topic='general')
    
    result = tavily_search.invoke(query)
    
    return result