# A lite ver from tg_bot_collections

tg_bot_collection <https://github.com/yihong0618/tg_bot_collections>

## Usage

`git clone https://github.com/alterxyz/tg_bot_collections_lite`

Pick one of the handler(folder), delete the rest, rename the left one to `handler`.

```shell
sudo python3 env_setup.py # Optional
source /etc/environment
python3 tg.py ${BOT_TOKEN}
```

## For Environment keys

If you need to check the env setup, `cd` to this directory and run `env_setup.py` manually.

## Manual pip install

```shell
pip install openai
pip install telebot
pip install telegramify-markdown
pip install expiringdict
pip install google-generativeai
pip install --upgrade together
pip install urlextract
pip install groq
pip install dify-client
pip install Markdown
pip install beautifulsoup4
pip install black
```

## About Sync

Try install FreeFileSync and run the `SyncSettings.ffs_gui` file.

### Unexisted file from non lite

- env_setup.py
- example.json

### Different file from non lite

- README.md
- requirements.txt

### Same

- Folder handler
