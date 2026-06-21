from .tools import search_web

CAPABILITY = {
    "name": "web_search",
    "description": "Search the internet for up-to-date information",
    "tools": [search_web]
}