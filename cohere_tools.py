import os
from secrets_my import get_secret

import cohere
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper


"""
pip install wolframalpha
pip install cohere
pip install langchain langchain_cohere langchain_experimental
pip install langchain-core
pip install langchain-community
pip install langchain-cohere
"""

# Initialize Cohere client
co = cohere.Client(api_key=get_secret("test", "COHERE_API_KEY"))
model = "command-r-plus"

STEP = 0

WOLFRAM_ALPHA_APPID = get_secret("test", "WOLFRAM_ALPHA_APPID")
os.environ["WOLFRAM_ALPHA_APPID"] = WOLFRAM_ALPHA_APPID


def step(describe: str) -> None:
    global STEP
    # print(f"\n------\nStep {str(STEP)}: {describe}\n------\n")
    STEP += 1


def web_search(query: str) -> str:
    step("DuckDuckGo Search Start")
    search = DuckDuckGoSearchResults()
    print(f"\n------\nDuck Query: {query}\n------\n")
    result = search.run(query)
    return result


web_search_tool = {
    "name": "web_search",
    "description": "Performs a web search with the specified query using DuckDuckGo",
    "parameter_definitions": {
        "query": {
            "description": "the query to look up",
            "type": "str",
            "required": True,
        }
    },
}


def wolfram_alpha(query: str) -> str:
    step("Wolfram Alpha API")
    wolfram = WolframAlphaAPIWrapper()
    try:
        lines = query.strip().split("\n")  # LLM tool use issue...
        processed_query = lines[-1] if len(lines) == 1 else lines[-1]

        print(f"\n------\nOriginal Query: {query}\n")
        print(f"Processed Query: {processed_query}\n------\n")

        result = wolfram.run(processed_query)
    except Exception as e:
        result = f"Wolfram Alpha wasn't able to answer it: {str(e)}. Maybe try simplifying the question."
    return result


wolfram_alpha_tool = {
    "name": "wolfram_alpha",
    "description": "Performs advanced calculations and analysis, returns a single plain text result directly from Wolfram|Alpha",
    "parameter_definitions": {
        "query": {
            "description": "the mathematical expression or question to calculate or analyze. In form of a string, and follow Wolfram Language syntax.",
            "type": "str",
            "required": True,
        }
    },
}


def my_calculator(query: str) -> str:
    result = wolfram_alpha(query)
    return result


calculator_tool = {
    "name": "my_calculator",
    "description": "will automatically calculate any math expression that Command R or Command R+ generate in response to your natural language prompt if appropriate.",
    "parameter_definitions": {
        "expression": {
            "type": "string",
            "description": "The math expression to evaluate.",
        }
    },
}


def chat_with_tools(message: str, model: str = model):
    step("Run general chat")
    tools = [web_search_tool, wolfram_alpha_tool, calculator_tool]
    res = co.chat(model=model, message=message, force_single_step=False, tools=tools)

    while res.tool_calls:
        step(f"Run tool calls:\n{res}\n")
        print(f"Steps{STEP}: {res.text}\n")
        tool_results = []
        for call in res.tool_calls:
            try:
                if call.name == "web_search":
                    co_result = [{"answer": web_search(call.parameters["query"])}]
                elif call.name == "good_calculator":
                    print(f"\n------\nQuery: {call}\n------\n")
                    co_result = [{"answer": wolfram_alpha(call.parameters["query"])}]
                elif call.name == "my_calculator":
                    co_result = [
                        {"answer": my_calculator(call.parameters["expression"])}
                    ]
                else:
                    co_result = [{"answer": f"Unknown tool: {call.name}"}]
            except Exception as e:
                co_result = [
                    {
                        "answer": f"Error in tool: {call.name}: {e}. Skip this tool call in the following steps."
                    }
                ]

            result = {"call": call, "outputs": co_result}
            tool_results.append(result)
            step(f"Current tool_results\n{tool_results}")

        step("Run chat again to see either the final result or the next tool call\n")
        res = co.chat(
            model=model,
            chat_history=res.chat_history,
            message="",
            force_single_step=False,
            tools=tools,
            tool_results=tool_results,
        )

    return res.text


# Example usage
if __name__ == "__main__":
    user_message = "What's the population of the capital of France? Then calculate the square root of its population, round to 1 decimal place."
    response = chat_with_tools(user_message)
    print("Final response:", response)
    while True:
        user_message = input("Enter your message: ")
        response = chat_with_tools(user_message)
        print("\n\nFinal response:", response)
