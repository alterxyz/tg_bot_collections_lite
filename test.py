from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
import cohere
from secrets_my import get_secret
import os


co = cohere.Client(api_key=get_secret("test", "COHERE_API_KEY"))
wolfram_alpha_appid = get_secret("test", "WOLFRAM_ALPHA_APPID")
os.environ["WOLFRAM_ALPHA_APPID"] = wolfram_alpha_appid


def cohere(message: str) -> str:
    """Input message, will print"""
    stream = co.chat_stream(
        model="command-r-plus",
        message=message,
        temperature=0.3,
        chat_history=[],
        prompt_truncation="AUTO",
        connectors=[{"id": "web-search"}],
    )

    for event in stream:
        if event.event_type == "text-generation":
            print(event.text, end="")


def DuckDuckGoSearch(query: str) -> str:
    """Input query, will return (may need manual print)"""
    search = DuckDuckGoSearchResults()
    result = search.run(query)
    return result


def wolfram_alpha(query: str) -> str:
    """Input query, will return (may need manual print)"""
    wolfram = WolframAlphaAPIWrapper()
    result = wolfram.run(query)
    return result


if __name__ == "__main__":
    input_m = input("Enter your message: ")
    print(wolfram_alpha(input_m))
