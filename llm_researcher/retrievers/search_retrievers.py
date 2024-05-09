import os
from tavily import TavilyClient
from duckduckgo_search import DDGS

def tavily_search(query, max_results=7):
    try:
        api_key = os.environ["TAVILY_API_KEY"]
        client = TavilyClient(api_key)
    except:
        raise Exception("Tavily API key not found. Please set the TAVILY_API_KEY environment variable. "
                        "You can get a key at https://app.tavily.com")

    try:
        # Search the query
        results = client.search(query, search_depth="advanced", max_results=max_results)
        # Return the results
        search_response = [{"href": obj["url"], "body": obj["content"]} for obj in results.get("results", [])]
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"Error: {e}")
        search_response = []
        #ddg = DDGS()
        #search_response = ddg.text(query, region='wt-wt', max_results=max_results)

    search_response = [obj for obj in search_response if "youtube.com" not in obj["href"]]
    return search_response
