import os
from secrets_my import get_secret

import cohere
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper


"""
pip install cohere wolframalpha duckduckgo-search langchain-community
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
    search = DuckDuckGoSearchResults()
    return search.run(query)


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
    wolfram = WolframAlphaAPIWrapper()
    try:
        lines = query.strip().split("\n")  # LLM tool use issue...
        processed_query = lines[-1] if len(lines) == 1 else lines[-1]
        result = wolfram.run(processed_query)
    except Exception as e:
        result = f"Wolfram Alpha wasn't able to answer. Try simplifying the question."
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
    tools = [web_search_tool, wolfram_alpha_tool, calculator_tool]
    res = co.chat(model=model, message=message, force_single_step=False, tools=tools)

    while res.tool_calls:
        print(res.text)
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


def chat_stream_with_tools(message, model=model):
    tools = [web_search_tool, wolfram_alpha_tool, calculator_tool]
    res = co.chat_stream(
        model=model, message=message, force_single_step=False, tools=tools
    )
    # We try get the tool call, or the text generation. Since we had force_single_step=False, so either one of them will be returned.
    for event in res:
        if event.event_type == "stream-start":
            pass
        elif event.event_type == "tool-calls-chunk":
            if hasattr(event, "text") and event.text:
                print(event.text, end="")
        elif event.event_type == "text-generation":
            print(event.text, end="")
        elif event.event_type == "stream-end":
            end_event = event.response
            print("\n\n")
    res = end_event
    (
        print("\n#####\n#YES#\n#####\n")
        if res.tool_calls
        else print("\n#####\n#END#\n#####\n")
    )
    while res.tool_calls:
        # print(res.text) # This will be an observation and a plan with next steps
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

            # call chat again with tool results
        res = co.chat_stream(
            model=model,
            chat_history=res.chat_history,
            message="",
            force_single_step=False,
            tools=tools,
            tool_results=tool_results,
        )
        for event in res:
            if event.event_type == "stream-start":
                pass
            elif event.event_type == "tool-calls-chunk":
                if hasattr(event, "text") and event.text:
                    print(event.text, end="")
            elif event.event_type == "text-generation":
                print(event.text, end="")
            elif event.event_type == "stream-end":
                end_event = event.response
                print("\n\n")
        res = end_event
        (
            print("\n#####\n#YES#\n#####\n")
            if res.tool_calls
            else print("\n#####\n#END#\n#####\n")
        )


def cohere_stream():
    # co = cohere.Client("<<apiKey>>")

    response = co.chat_stream(
        chat_history=[
            {"role": "USER", "message": "Who discovered gravity?"},
            {
                "role": "CHATBOT",
                "message": "The man who is widely credited with discovering gravity is Sir Isaac Newton",
            },
        ],
        message="What year was he born?",
        # perform web search before answering the question. You can also use your own custom connector.
        connectors=[{"id": "web-search"}],
    )

    for event in response:
        if event.event_type == "text-generation":
            print(event.text, end="")


# Example usage
if __name__ == "__main__":
    user_message = "What's the population of the capital of France? Then calculate the square root of its population, round to 1 decimal place."
    response = chat_stream_with_tools(user_message)
    print("Final response:", response)
    while True:
        user_message = input("Enter your message: ")
        response = chat_with_tools(user_message)
        print("\n\nFinal response:", response)
