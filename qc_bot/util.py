import random
import io

import discord
import emojis


prefix = "qc!"
swears = [
    "ya fool",
    "ya ass",
    "ya halfwit",
    "ya nincompoop",
    "ya dunce",
    "ya dolt",
    "ya ignoramus",
    "ya cretin",
    "ya imbecile",
    "ya moron",
    "ya simpleton",
    "ya dope",
    "ya ninny",
    "ya chump",
    "ya dimwit",
    "ya dumbo",
    "ya dum-dum",
    "ya dumb-bell",
    "ya loon",
    "ya jackass",
    "ya bonehead",
    "ya fathead",
    "ya numbskull",
    "ya blockhead",
    "ya knucklehead",
    "ya thickhead",
    "ya airhead",
    "ya pinhead",
    "ya birdbrain",
    "ya jerk",
    "ya donkey",
    "ya noodle",
    "ya twit",
    "ya git",
    "ya muppet",
    "ya schmuck",
    "ya dork",
    "ya dingbat",
    "ya wing-nut",
    "ya knobhead",
    "ya mofo",
    "ya arse",
    "chutiye",
    "bhosdike",
    "bhadwe",
    "madarchod",
    "behenchod"
]


async def create_colored_message(message_string, swearing, plural=False):
    error = f"```fix\n{message_string}"
    if swearing:
        error += ", " + random.choice(swears)
        if plural:
            error += "s"
    error += ".```"

    return error


async def send_slide(ctx, bot, direction="Forward"):
    if bot.curr_slide == -1:
        reply = await create_colored_message(
            "Reached the beginning of the quiz file",
            swearing=False
        )
        await ctx.send(reply)
        return

    if bot.curr_slide == len(bot.quiz_file):
        reply = await create_colored_message(
            "Reached the end of the quiz file",
            swearing=False
        )
        await ctx.send(reply)
        return

    with io.BytesIO() as image_binary:
        image = bot.quiz_file[bot.curr_slide]
        image.save(image_binary, "JPEG")
        image_binary.seek(0)

        reply = await create_colored_message(
            f"Slide {bot.curr_slide + 1}",
            swearing=False
        )
        await ctx.send(reply)

        message = await ctx.send(
            file=discord.File(
                fp=image_binary,
                filename=f"Slide_{bot.curr_slide}.jpg"
            )
        )

        await message.add_reaction(emojis.encode(":arrow_backward:"))
        await message.add_reaction(emojis.encode(":arrow_forward:"))

        return message
