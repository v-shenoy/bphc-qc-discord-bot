from qc_bot.qc_bot import bot
import qc_bot.bot_commands
import qc_bot.bot_events
# Modules bot_commands, bot_events are imported
# just to run the code in them


if __name__ == "__main__":
    # Insert your generated API token before running.
    discord_api_key = ""
    bot.run(discord_api_key)
