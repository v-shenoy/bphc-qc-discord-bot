import json

from qc_bot.qc_bot import bot
from qc_bot import bot_commands, bot_events
# Modules bot_commands, bot_events are imported
# just to run the code in them


if __name__ == "__main__":
    config = None
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    discord_api_key = config["API_KEY"]
    bot.run(discord_api_key)
