import sys

import emojis

from qc_bot.util import create_colored_message, send_slide
from qc_bot.qc_bot import bot


# @bot.event
# async def on_ready():
#     for guild in bot.guilds:
#         if guild.system_channel is None:
#             pass

#         reply = await create_colored_message(
#             "Hey, I am up and running now",
#             swearing=False
#         )

#         await guild.system_channel.send(reply)


@bot.event
async def on_reaction_add(reaction, member):
    if bot.slide_message is None:
        return

    if reaction.message.id != bot.slide_message.id:
        return

    if member != bot.quizmaster:
        return

    if reaction.emoji == emojis.encode(":arrow_forward:"):
        bot.curr_slide += 1
        bot.slide_message = await send_slide(reaction.message.channel, bot)
    elif reaction.emoji == emojis.encode(":arrow_backward:"):
        bot.curr_slide -= 1
        bot.slide_message = await send_slide(reaction.message.channel, bot)


@bot.event
async def on_command_error(ctx, error):
    print(error, file=sys.stderr)
    reply = await create_colored_message(
        "Something went wrong.\n\n"
        + "Try viewing help",
        swearing=bot.swearing
    )

    await ctx.send(reply)
