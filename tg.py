import argparse
from telebot import TeleBot

from handlers import list_available_commands, load_handlers


def main():
    # Init args
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")

    # 'disable-command' option
    # The action 'append' will allow multiple entries to be saved into a list
    # The variable name is changed to 'disable_commands'
    parser.add_argument(
        "--disable-command",
        action="append",
        dest="disable_commands",
        help="Specify a command to disable. Can be used multiple times.",
        default=[],
        choices=list_available_commands(),
    )

    options = parser.parse_args()
    print("Arg parse done.")

    # Init bot
    bot = TeleBot(options.tg_token)
    load_handlers(bot, options.disable_commands)
    print("Bot init done.")

    # Start bot
    print("Starting tg collections bot.")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


if __name__ == "__main__":
    main()
