# A lite ver from tg_bot_collections

tg_bot_collection <https://github.com/yihong0618/tg_bot_collections>.

This project would maximize the similarity with the original project such as core functions and usage.

Try <https://t.me/tealmoon_ai_v1_alt_bot>

## Sync and Todo

- [ ] 2024/07/09
    - [ ] chore: UX improvement
    - [ ] `useful.py`: Let user know `/answer_it` usage: Type or **click the blue text**.
    - [ ] `cohere.py`: Enable link preview disabled for cleaner output.

## Usage

### Run the bot

Run the bot with the following command after the [Setup](#setup).:

```shell
source /etc/environment # Optional: Reload the environment keys
python3 tg.py ${TELEGRAM_BOT_TOKEN}
```

---

### Update the bot

```shell
git checkout main
git pull origin main

# If Aborting due to local changes
# Option 1:
git stash
git pull origin main
git stash pop

# Option 2:
git diff --stat origin/main..HEAD
# Make sure your files that do not want to be overwritten are not in the list.
git reset --hard origin/main
```

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

### TODO

- [ ] Naming issue:

Rename `useful.py` to something else, otherwise it will block other handlers.

Currently it is renamed to `danger.py`, <https://t.me/tealmoon_ai_v1_alt_bot> all commands are working.

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

See [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

### About Sync

Try install FreeFileSync and run the `SyncSettings.ffs_gui` file.

Or manually compare and edit the files.

### Unexisted file from non lite

- env.py
- example_token_key.json

### Different file from non lite

- README.md
- __init__.py # Skipped same text to avoid Error message, since we are edit message frequently.

### Same

- Core codes
- most handlers
