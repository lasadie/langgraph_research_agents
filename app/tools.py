from langchain_community.tools.tavily_search import TavilySearchResults
from config import tavily_api_key

def search_web(query: str) -> list:
    """
    Search the web for a query.
    :return: Return list of results
    """
    tavily_search = TavilySearchResults(api_key=tavily_api_key, max_results=2, search_depth='advanced', max_tokens=1000)
    results = tavily_search.invoke(query)

    return results