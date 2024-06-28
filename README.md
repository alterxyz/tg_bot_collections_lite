# A lite ver from tg_bot_collections

tg_bot_collection <https://github.com/yihong0618/tg_bot_collections>.

This project would maximize the similarity with the original project such as core functions and usage.

Try others like gpt or gemini or cohere at <https://t.me/tealmoon_ai_v1_bot>

Try `/answer_it` (V2) at <https://t.me/tealmoon_ai_v1_alt_bot>

## Usage

### Run the bot

Run the bot with the following command after the [Setup](#setup).:

```shell
source /etc/environment # Optional: Reload the environment keys
python3 tg.py ${TELEGRAM_BOT_TOKEN}
```

---

### Setup

#### Init the repo

```shell
git clone https://github.com/alterxyz/tg_bot_collections_lite
cd tg_bot_collections_lite

```

#### Setup the environment keys

If you had environment api keys already, you can skip this step.

(run `python3 env.py check` to check the environment keys status.)

##### Option 1: Manual setup (Good for first time users)

1. Run `python3 env.py init`
2. Edit the `token_key.json` file with your API key.
3. Run `sudo python3 env.py load` to load(overwrite) the environment keys from the "token_key.json" file.

##### Option 2: Paste the file

1. Paste the "token_key.json" file in the root directory of the project.
2. Run `sudo python3 env.py load` to load(overwrite) the environment keys from the "token_key.json" file.

#### Select the handler

Pick one of the handler(folder), rename the folder to `handler`.

The handler(folder) are:

1. bots with usage as `/command <text>` or `command: <text>`, like `/gpt <text>` or `gpt: <text>`.
2. pure message, then come with `/answer_it` (Ver.1)
3. pure message, then come with `/answer_it` (Ver.2, modularized, summary, and more llm models supported.)

### Install the dependencies

#### Manual pip install - Recommended

```shell
pip install openai
pip install telebot
pip install telegramify-markdown
pip install expiringdict
pip install google-generativeai
pip install together
pip install urlextract
pip install groq
pip install dify-client
pip install Markdown
pip install beautifulsoup4
pip install black
pip install cohere
```

(`pip install --upgrade ${something}` for risk takers like me)

#### Or install from the requirements.txt

`pip install -r requirements.txt` for Ubuntu

`pip3 install -r requirements_win.txt` for Windows

## Development Notes

### About Sync

Try install FreeFileSync and run the `SyncSettings.ffs_gui` file.

Or manually compare and edit the files.

### Unexisted file from non lite

- env.py
- example_token_key.json

### Different file from non lite

- README.md
- requirements.txt

### Same

- Core codes
- most handlers
