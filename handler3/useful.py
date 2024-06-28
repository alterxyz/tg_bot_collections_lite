# useful md for myself and you.

from telebot import TeleBot
from telebot.types import Message
from expiringdict import ExpiringDict
from os import environ
import time
import datetime
import re

from . import *

from telegramify_markdown import convert
from telegramify_markdown.customize import markdown_symbol


#### Customization ####
markdown_symbol.head_level_1 = "📌"  # If you want, Customizing the head level 1 symbol
markdown_symbol.link = "🔗"  # If you want, Customizing the link symbol
chat_message_dict = ExpiringDict(max_len=100, max_age_seconds=120)
chat_user_dict = ExpiringDict(max_len=100, max_age_seconds=20)
Language = "zh-cn"  # "en" or "zh-cn".
SUMMARY = (
    "cohere"  # see the summary_xyz for what available, or set to None to disable it.
)


#### Telegra.ph init ####
# Will auto generate a token if not provided, restart will lose all TODO
TELEGRA_PH_TOKEN = environ.get("TELEGRA_PH_TOKEN")
# Edit "Store_Token = False" in "__init__.py" to True to store it
ph = TelegraphAPI(TELEGRA_PH_TOKEN)


#### LLMs init ####
#### OpenAI init ####
CHATGPT_USE = True
CHATGPT_API_KEY = environ.get("OPENAI_API_KEY")
CHATGPT_BASE_URL = environ.get("OPENAI_API_BASE") or "https://api.openai.com/v1"
if CHATGPT_USE and CHATGPT_API_KEY:
    from openai import OpenAI

    CHATGPT_PRO_MODEL = "gpt-4o-2024-05-13"
    client = OpenAI(api_key=CHATGPT_API_KEY, base_url=CHATGPT_BASE_URL, timeout=300)


#### Gemini init ####
GEMINI_USE = True
GOOGLE_GEMINI_KEY = environ.get("GOOGLE_GEMINI_KEY")
if GEMINI_USE and GOOGLE_GEMINI_KEY:
    import google.generativeai as genai
    from google.generativeai import ChatSession
    from google.generativeai.types.generation_types import StopCandidateException

    genai.configure(api_key=GOOGLE_GEMINI_KEY)

    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-pro-latest",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    convo = model.start_chat()


#### Cohere init ####
COHERE_USE = True
COHERE_API_KEY = environ.get("COHERE_API_KEY")

if COHERE_USE and COHERE_API_KEY:
    import cohere

    COHERE_MODEL = "command-r-plus"
    co = cohere.Client(api_key=COHERE_API_KEY)


#### Qwen init ####
QWEN_USE = False
QWEN_API_KEY = environ.get("TOGETHER_API_KEY")
QWEN_MODEL = "Qwen/Qwen2-72B-Instruct"

#### init end ####


def md_handler(message: Message, bot: TeleBot):
    """pretty md: /md <address>"""
    who = ""
    reply_id = bot_reply_first(message, who, bot)
    bot_reply_markdown(reply_id, who, message.text.strip(), bot)


def latest_handle_messages(message: Message, bot: TeleBot):
    """ignore"""
    chat_id = message.chat.id
    chat_user_id = message.from_user.id
    # if is bot command, ignore
    if message.text.startswith("/"):
        return
    # start command ignore
    elif message.text.startswith(
        (
            "md",
            "chatgpt",
            "gemini",
            "qwen",
            "map",
            "github",
            "claude",
            "llama",
            "dify",
            "tts",
            "sd",
            "map",
            "yi",
            "cohere",
        )
    ):
        return
    # answer_it command ignore
    elif message.text.startswith("answer_it"):
        return
    # if not text, ignore
    elif not message.text:
        return
    else:
        if chat_user_dict.get(chat_user_id):
            message.text += chat_message_dict[chat_id].text
            chat_message_dict[chat_id] = message
        else:
            chat_message_dict[chat_id] = message
        chat_user_dict[chat_user_id] = True
        print(chat_message_dict[chat_id].text)


def answer_it_handler(message: Message, bot: TeleBot):
    """answer_it: /answer_it"""
    # answer the last message in the chat group
    who = "answer_it"
    # get the last message in the chat

    chat_id = message.chat.id
    latest_message = chat_message_dict.get(chat_id)
    m = latest_message.text.strip()
    m = enrich_text_with_urls(m)
    full_answer = ""
    full_chat_id_list = []

    ##### Gemini #####
    if GEMINI_USE and GOOGLE_GEMINI_KEY:
        try:
            full_answer, chat_id = gemini_answer(latest_message, bot, full_answer, m)
            full_chat_id_list.append(chat_id)
        except Exception as e:
            print(f"Answer_it Error\n------\nGemini:\n{e}\n------\n")
            pass

    ##### ChatGPT #####
    if CHATGPT_USE and CHATGPT_API_KEY:
        try:
            full_answer, chat_id = chatgpt_answer(latest_message, bot, full_answer, m)
            full_chat_id_list.append(chat_id)
        except Exception as e:
            print(f"Answer_it Error\n------\nChatGPT:\n{e}\n------\n")
            pass

    ##### Cohere #####
    if COHERE_USE and COHERE_API_KEY:
        try:
            full_answer, chat_id = cohere_answer(latest_message, bot, full_answer, m)
            full_chat_id_list.append(chat_id)
        except Exception as e:
            print(f"Answer_it Error\n------\nCohere:\n{e}\n------\n")
            pass
        full, chat_id = cohere_answer(latest_message, bot, full_answer, m)
        full_chat_id_list.append(chat_id)
    else:
        pass

    ##### Telegraph #####
    final_answer(latest_message, bot, full, full_chat_id_list)


def gemini_answer(latest_message: Message, bot: TeleBot, full, m):
    """gemini answer"""
    who = "Gemini Pro"
    # show something, make it more responsible
    reply_id = bot_reply_first(latest_message, who, bot)

    try:
        r = convo.send_message(m, stream=True)
        s = ""
        start = time.time()
        for e in r:
            s += e.text
            if time.time() - start > 1.7:
                start = time.time()
                bot_reply_markdown(reply_id, who, s, bot, split_text=False)
        bot_reply_markdown(reply_id, who, s, bot)
        convo.history.clear()
    except Exception as e:
        print(f"Answer_it Inner function Error\n------\n{who}:\n{e}\n------\n")
        convo.history.clear()
        bot_reply_markdown(reply_id, who, "Error", bot)

    full += f"{who}:\n{s}"
    return full, reply_id.message_id


def chatgpt_answer(latest_message: Message, bot: TeleBot, full, m):
    """chatgpt answer"""
    who = "ChatGPT Pro"
    reply_id = bot_reply_first(latest_message, who, bot)

    player_message = [{"role": "user", "content": m}]

    try:
        r = client.chat.completions.create(
            messages=player_message,
            max_tokens=4096,
            model=CHATGPT_PRO_MODEL,
            stream=True,
        )
        s = ""
        start = time.time()
        for chunk in r:
            if chunk.choices[0].delta.content is None:
                break
            s += chunk.choices[0].delta.content
            if time.time() - start > 1.5:
                start = time.time()
                bot_reply_markdown(reply_id, who, s, bot, split_text=False)
        # maybe not complete
        try:
            bot_reply_markdown(reply_id, who, s, bot)
        except:
            pass

    except Exception as e:
        print(f"Answer_it Inner function Error\n------\n{who}:\n{e}\n------\n")
        bot_reply_markdown(reply_id, who, "answer wrong", bot)

    full += f"\n---\n{who}:\n{s}"
    return full, reply_id.message_id


def cohere_answer(latest_message: Message, bot: TeleBot, full, m):
    """cohere answer"""
    who = "Command R Plus"
    reply_id = bot_reply_first(latest_message, who, bot)

    try:
        current_time = datetime.datetime.now(datetime.timezone.utc)
        preamble = (
            f"You are Command R Plus, a large language model trained to have polite, helpful, inclusive conversations with people. People are looking for information that may need you to search online. Make an accurate and fast response. If there are no search results, then provide responses based on your general knowledge(It's fine if it's not accurate, it might still inspire the user."
            f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}, "
            f"UTC-4 (e.g. New York) is {current_time.astimezone(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y-%m-%d %H:%M:%S')}, "
            f"UTC-7 (e.g. Los Angeles) is {current_time.astimezone(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y-%m-%d %H:%M:%S')}, "
            f"and UTC+8 (e.g. Beijing) is {current_time.astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}."
        )

        stream = co.chat_stream(
            model=COHERE_MODEL,
            message=m,
            temperature=0.8,
            chat_history=[],  # One time, so no need for chat history
            prompt_truncation="AUTO",
            connectors=[{"id": "web-search"}],
            citation_quality="accurate",
            preamble=preamble,
        )

        s = ""
        source = ""
        start = time.time()
        for event in stream:
            if event.event_type == "stream-start":
                bot_reply_markdown(reply_id, who, "Thinking...", bot)
            elif event.event_type == "search-queries-generation":
                bot_reply_markdown(reply_id, who, "Searching online...", bot)
            elif event.event_type == "search-results":
                bot_reply_markdown(reply_id, who, "Reading...", bot)
                for doc in event.documents:
                    source += f"\n{doc['title']}\n{doc['url']}\n"
            elif event.event_type == "text-generation":
                s += event.text.encode("utf-8").decode("utf-8", "ignore")
                if time.time() - start > 1.5:
                    start = time.time()
                    bot_reply_markdown(
                        reply_id,
                        who,
                        f"\nStill thinking{len(s)}...\n{s}",
                        bot,
                        split_text=True,
                    )
            elif event.event_type == "stream-end":
                s += event.text.encode("utf-8").decode("utf-8", "ignore")
                break
        content = (
            s
            + "\n---\n"
            + source
            + f"\nLast Update{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} at UTC+8\n"
        )
        # maybe not complete
        try:
            bot_reply_markdown(reply_id, who, s, bot, split_text=True)
        except:
            pass
    except Exception as e:
        print(f"Answer_it Inner function Error\n------\n{who}:\n{e}\n------\n")
        bot_reply_markdown(reply_id, who, "Answer wrong", bot)
        return full, reply_id.message_id
    full += f"\n---\n{who}:\n{content}"
    return full, reply_id.message_id


# TODO: Perplexity looks good. `pplx_answer`


def final_answer(latest_message: Message, bot: TeleBot, full, answers_list):
    """final answer"""
    who = "Answer it"
    reply_id = bot_reply_first(latest_message, who, bot)
    ph_s = ph.create_page_md(title="Answer it", markdown_text=full)
    bot_reply_markdown(reply_id, who, f"[View]({ph_s})", bot)
    # delete the chat message, only leave a telegra.ph link
    for i in answers_list:
        bot.delete_message(latest_message.chat.id, i)

    #### Summary ####
    if SUMMARY == None:
        pass
    if COHERE_USE and COHERE_API_KEY and SUMMARY == "cohere":
        summary_cohere(bot, full, ph_s, reply_id)


def summary_cohere(bot: TeleBot, full_answer: str, ph_s: str, reply_id: int) -> None:
    """Receive the full text, and the final_answer's chat_id, update with a summary."""
    who = "Answer it"

    # inherit
    if Language == "zh-cn":
        s = f"[全文]({ph_s}) | "
    elif Language == "en":
        s = f"[Full Answer]({ph_s}) | "

    # filter
    length = len(full_answer)  # max 128,000t tokens...
    if length > 50000:
        full_answer = full_answer[:50000]

    try:
        preamble = """
        You are Command R Plus, a large language model trained to have polite, helpful, inclusive conversations with people. The user asked a question, and multiple AI have given answers to the same question, but they have different styles, and rarely they have opposite opinions or other issues, but that is normal. Your task is to summarize the responses from them in a concise and clear manner. The summary should:

Be written in bullet points.
Contain between two to ten sentences.
Highlight key points and main conclusions.
Note any significant differences in responses.
Provide a brief indication if users should refer to the full responses for more details.
For the first LLM's content, if it is mostly in any language other than English, respond in that language for all your output.
Start with "Summary:" or "总结:"
"""
        stream = co.chat_stream(
            model=COHERE_MODEL,
            message=full_answer,
            temperature=0.4,
            chat_history=[],
            prompt_truncation="OFF",
            connectors=[],
            preamble=preamble,
        )

        start = time.time()
        for event in stream:
            if event.event_type == "stream-start":
                bot_reply_markdown(reply_id, who, f"{s}Summarizing...", bot)
            elif event.event_type == "text-generation":
                s += event.text.encode("utf-8").decode("utf-8", "ignore")
                if time.time() - start > 0.8:
                    start = time.time()
                    bot_reply_markdown(reply_id, who, s, bot)
            elif event.event_type == "stream-end":
                s += event.text.encode("utf-8").decode("utf-8", "ignore")
                break

        try:
            bot_reply_markdown(reply_id, who, s, bot)
        except:
            pass

    except Exception as e:
        if Language == "zh-cn":
            bot_reply_markdown(reply_id, who, f"[全文]({ph_s})", bot)
        elif Language == "en":
            bot_reply_markdown(reply_id, who, f"[Full Answer]({ph_s})", bot)
        bot_reply_markdown(reply_id, who, s, bot)
        print(f"Summary Cohere Error{e}\n------\n")


if GOOGLE_GEMINI_KEY and CHATGPT_API_KEY:

    def register(bot: TeleBot) -> None:
        bot.register_message_handler(
            answer_it_handler, commands=["answer_it"], pass_bot=True
        )
        bot.register_message_handler(latest_handle_messages, pass_bot=True)