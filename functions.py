from typing import Dict
from duckduckgo_search import DDGS

list = []

def search_text(args: Dict = None):
    """Search DuckDuckGo for a query

    Args:
        args (Dict, optional): The arguments to pass to the function. Defaults to None.

    Returns:
        str: The search results
    """    
    if args is None:
        args = {}
    try:
        query = args["query"]
    except KeyError:
        return "No query provided"
    results = []
    res_generator = DDGS().text(keywords=query)
    print(f"Searching text for {query}")
    for _ in range(5):
        try:
            results.append(next(res_generator))
        except StopIteration:
            break

    return str(results)

list.append({
    "name": "search_text",
    "description": "Search DuckDuckGo for a query using keywords",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for"
            }
        },
        "required": ["query"]
    }
})
    
def search_answers(args: Dict = None):
    """Search DuckDuckGo for an answer to a question

    Args:
        args (Dict, optional): The arguments to pass to the function. Defaults to None.

    Returns:
        str: The answer to the question
    """    
    if args is None:
        args = {}
    try:
        query = args["query"]
    except KeyError:
        return "No query provided"
    print(f"Searching answers for {query}")
    return str(DDGS().answers(keywords=query))

list.append({
    "name": "search_answers",
    "description": "Search DuckDuckGo for an answer to a question and return the result",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question to answer"
            }
        },
        "required": ["query"]
    }
})

def search_news(args: Dict = None):
    """Search DuckDuckGo for news

    Args:
        args (Dict, optional): The arguments to pass to the function. Defaults to None.

    Returns:
        str: The news results
    """    
    if args is None:
        args = {}
    try:
        query = args["query"]
    except KeyError:
        return "No query provided"
    print(f"Searching news for {query}")
    return str(DDGS().news(keywords=query))

list.append({
    "name": "search_news",
    "description": "Search DuckDuckGo for news and return the result",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to search for"
            }
        },
        "required": ["query"]
    }
})

# list.append({
#     "name": "get_weather",
#     "description": "Get the weather for a location. Returns a JSON object with the weather, temperature and wind speed.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "city": {
#                 "type": "string",
#                 "description": "The city formatted for OpenWeatherMap API, e.g. London"
#             },
#             "country": {
#                 "type": "string",
#                 "description": "The country code formatted for OpenWeatherMap API, e.g. UK"
#             },
#             "units": {
#                 "type": "string",
#                 "enum": ["imperial", "metric", "standard"],
#                 "description": "The temperature unit to use. Imperial is Fahrenheit, metric is Celcius and standard is Kelvin. Defaults to metric if not provided."
#             }
#         },
#         "required": ["city", "country"]
#     }
# })

# def exit_conversation(args: Dict = None):
#     del args
#     exit()

list.append({
    "name": "exit_conversation",
    "description": "Exit the conversation",
    "parameters": {
        "type": "object",
        "properties": {}
    }
})
