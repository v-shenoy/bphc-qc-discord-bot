import discord

from pdf2image import convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import emojis

from qc_bot.util import create_colored_message, send_slide
from qc_bot.quiz import QuizCommand, Participant
from qc_bot.qc_bot import bot


# General Commands
@bot.command(name="help")
async def command_help(ctx):
    reply = "```fix\nHelp for the Quiz Club Bot.\n"
    reply += f"The prefix for this bot is - {bot.prefix}.\n\n"

    for attr in dir(QuizCommand):
        if attr.startswith("command_"):

            command = getattr(QuizCommand, attr)
            if not command["general"]:
                reply += "* "

            reply += command["usage"] + " - \n\t\t" + command["desc"] + "\n\n"

    reply += "\n* - QM Only\n"
    reply += "```"
    await ctx.send(reply)


@bot.command(name="startQuiz")
async def start_quiz(ctx, *, quiz_name):
    if bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's already a quiz going on",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    bot.quiz_ongoing = True
    bot.quiz_name = quiz_name
    bot.quiz_channel = ctx.message.channel
    bot.quizmasters.append(ctx.author)
    bot.quizmaster_channel = await ctx.author.create_dm()
    bot.question_ongoing = False
    bot.participants = []
    bot.participating = {}
    bot.pouncing_allowed = False
    bot.joining_allowed = False
    bot.direct_participant = None
    bot.curr_participant = None
    bot.next_direct = 0
    bot.pounce_direction = "CW"
    bot.pounces = None
    bot.swearing = True

    reply = f"```fix\nStarting quiz - {quiz_name}.\n\n"
    reply += f"{ctx.author} will be your QM for this quiz.```"

    await ctx.send(reply)


@bot.command(name="join")
async def join(ctx, *, nick):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author in bot.quizmasters:
        reply = await create_colored_message(
            "QM cannot join the quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.joining_allowed:
        reply = await create_colored_message(
            "Joining is forbidden",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    idt = bot.participating.get(ctx.author.id)

    if idt is not None:
        participant = bot.participants[idt]
        reply = ""
        if participant.kicked:
            participant.kicked = False
            reply += await create_colored_message(
                "{} [Number. {}] has rejoined the quiz".format(
                    participant.member,
                    participant.id + 1
                ),
                swearing=False
            )
        else:
            reply = await create_colored_message(
                "You already joined once",
                swearing=bot.swearing
            )
        await ctx.send(reply)
        return

    participant = Participant(bot.no_of_participants, ctx.author, nick)

    bot.participants.append(participant)
    bot.participating[ctx.author.id] = bot.no_of_participants
    bot.no_of_participants += 1

    reply = "```fix\n"
    reply += "{} has joined the quiz as participant no. {}```".format(
        ctx.author,
        bot.no_of_participants
    )

    await ctx.send(reply)


@bot.command(name="list")
async def list_participants(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nList of participants in {bot.quiz_name} - \n\n"

    for idx, participant in enumerate(bot.participants):
        reply += "\t{}. {} as {} [Number. {}]".format(
            idx + 1,
            participant.member,
            participant.nick,
            participant.id + 1
        )

        if participant.kicked:
            reply += " [Kicked]"
        reply += "\n"

    reply += "```"
    await ctx.send(reply)


@bot.command(name="scoreboard")
async def scoreboard(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    sorted_list = sorted(
        bot.participants, key=lambda item: item.score, reverse=True)

    reply = f"```fix\nCurrent Scoreboard for {bot.quiz_name} -"
    reply += "\n\n"

    for idx, participant in enumerate(sorted_list):
        reply += "\t{}. {} as {} - {} points".format(
            idx + 1,
            participant.member,
            participant.nick,
            participant.score
        )

        if participant.kicked:
            reply += " [Kicked]"
        reply += "\n"

    reply += "```"
    await ctx.send(reply)


async def pass_and_bounce_util(ctx, reply):
    while True:
        if bot.pounce_direction == "CW":
            bot.curr_participant += 1
        else:
            bot.curr_participant -= 1
        bot.curr_participant %= bot.no_of_participants

        if bot.curr_participant == bot.direct_participant:
            break

        participant = bot.participants[bot.curr_participant]
        if participant.kicked:
            reply += await create_colored_message(
                f"{participant.member} [Number. {participant.id + 1}] "
                + "is not participating anymore",
                swearing=False
            )
        elif not participant.pounced:
            break
        else:
            reply += await create_colored_message(
                f"{participant.member} [Number. {participant.id + 1}] "
                + "has pounced. moving on",
                swearing=False
            )

    if bot.curr_participant == bot.direct_participant:
        reply += await create_colored_message(
            "None of you got it",
            swearing=bot.swearing,
            plural=True
        )

        if bot.bounce_type == "bangalore":
            bot.next_direct = bot.direct_participant + 1
        else:
            bot.next_direct = bot.direct_participant

        await ctx.send(reply)
        return

    reply += f"{participant.member.mention}"
    reply += await create_colored_message(
        f"[Number. {participant.id + 1}] -  It's your turn",
        swearing=bot.swearing
    )

    await ctx.send(reply)


@bot.command(name="pass")
async def pass_question(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[bot.curr_participant]
    if ctx.author != participant.member:
        reply = await create_colored_message(
            "It's not your turn",
            bot.swearing
        )
        await ctx.send(reply)
        return

    reply = ctx.author.mention
    reply += await create_colored_message(
        "Your turn is being passed over",
        swearing=False
    )

    await pass_and_bounce_util(ctx, reply)


@bot.command(name="remind")
async def remind(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[bot.curr_participant]

    reply = f"{participant.member.mention}"
    reply += await create_colored_message(
        f"[Number. {participant.id + 1}] -  It's your fucking turn",
        swearing=bot.swearing
    )

    await ctx.send(reply)


@bot.command(name="pounce")
async def pounce(ctx, *, answer):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.pouncing_allowed:
        reply = await create_colored_message(
            "Pounce is closed",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not isinstance(ctx.message.channel, discord.DMChannel):
        await ctx.message.delete()
        reply = await create_colored_message(
            "Pounce on DM",
            swearing=bot.swearing)
        await ctx.send(reply)
        return

    idt = bot.participating.get(ctx.author.id)
    if idt is None:
        reply = await create_colored_message(
            "You are not participating",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[idt]
    if participant.kicked:
        reply = await create_colored_message(
            "You are not participating",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    curr_participant = bot.participants[bot.curr_participant]
    if ctx.author == curr_participant.member:
        reply = await create_colored_message(
            "It's your direct",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if participant.pounced:
        reply = await create_colored_message(
            "You already pounced",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    participant.pounced = True
    pounce_answer = await create_colored_message(
        f"{ctx.author} [Number. {idt + 1}] -  {answer}",
        swearing=False
    )

    bot.pounces.append(pounce_answer)

    reply = await create_colored_message(
        "You have pounced for this question with the answer - \n\n"
        + answer,
        swearing=False
    )

    await ctx.send(reply)

    reply = await create_colored_message(
        f"{ctx.author} [Number. {idt + 1}] pounced for this question",
        swearing=False
    )

    await bot.quiz_channel.send(reply)


@bot.command(name="clues")
async def clues(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = "```fix\nWant clues?```"

    message = await ctx.send(reply)
    await message.add_reaction(emojis.encode(":thumbsup:"))
    await message.add_reaction(emojis.encode(":thumbsdown:"))


@bot.command(name="swearing")
async def swearing(ctx, mode):
    if mode == "on":
        bot.swearing = True
    elif mode == "off":
        bot.swearing = False
    else:
        reply = await create_colored_message(
            "Incorrect argument to command",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nSwearing has been turned {mode}.```"
    await ctx.send(reply)


@bot.command(name="leave")
async def leave(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    idt = bot.participating.get(ctx.author.id)
    if idt is None:
        reply = await create_colored_message(
            "You are not participating",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    participant = bot.participants[idt]

    reply = await create_colored_message(
            "{} [Number. {}] has left the quiz".format(
                participant.member,
                participant.id + 1,
            ),
            swearing=False
        )

    participant.kicked = True

    await ctx.send(reply)


# QM Commands
@bot.command(name="endQuiz")
async def end_quiz(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nEnding quiz - {bot.quiz_name}.\n"
    quizmasters = ", ".join([str(qm) for qm in bot.quizmasters])
    reply += f"QMs - {quizmasters}.\n\n"
    reply += "Thank you for participating.\n\n"

    sorted_list = sorted(
        bot.participants, key=lambda item: item.score, reverse=True)

    reply += f"Final Scoreboard for {bot.quiz_name} -"
    reply += "\n\n"

    for idx, participant in enumerate(sorted_list):
        reply += "\t{}. {} as {} - {} points".format(
            idx + 1,
            participant.member,
            participant.nick,
            participant.score
        )
        reply += "\n"

    reply += "```"

    bot.reset()

    await ctx.send(reply)


@bot.command(name="startJoining")
async def start_joining(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if bot.joining_allowed:
        reply = await create_colored_message(
            "Joining is already allowed",
            swearing=bot.swearing
        )

    bot.joining_allowed = True
    reply = await create_colored_message(
        f"Joining period for {bot.quiz_name} has begun.\n\n"
        + "Type 'qc!join nick' to join the quiz.",
        swearing=False
    )

    await ctx.send(reply)


@bot.command(name="endJoining")
async def end_joining(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.joining_allowed:
        reply = await create_colored_message(
            "Joining is already forbidden",
            swearing=bot.swearing
        )

    bot.joining_allowed = False
    reply = await create_colored_message(
        f"Joining period for {bot.quiz_name} has ended",
        swearing=False
    )

    await ctx.send(reply)


@bot.command(name="pounceRound")
async def pounce_round(ctx, direction="CW"):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = None
    if direction == "CW":
        reply = await create_colored_message(
            "Clockwise pounce round beginning",
            swearing=False
        )
        bot.pounce_direction = direction
        bot.next_direct = 0
    elif direction == "ACW":
        reply = await create_colored_message(
            "Anti-Clockwise pounce round beginning",
            swearing=False
        )
        bot.pounce_direction = direction
        bot.next_direct = bot.no_of_participants - 1
    else:
        reply = await create_colored_message(
            "Unknown pounce direction",
            swearing=bot.swearing
        )

    await ctx.send(reply)


@bot.command(name="direct")
async def direct(ctx, team_num=None):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    try:
        team_num = int(team_num) - 1
    except (TypeError, ValueError):
        bot.next_direct %= bot.no_of_participants
        team_num = bot.next_direct

    bot.direct_participant = team_num
    bot.curr_participant = team_num

    participant = bot.participants[bot.curr_participant]
    if participant.kicked:
        reply = await create_colored_message(
            f"[Number. {participant.id + 1}] is not participating anymore",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    bot.question_ongoing = True

    reply = f"{participant.member.mention}"
    reply += await create_colored_message(
        f"[Number. {participant.id + 1}] -  It's your direct now",
        swearing=False
    )

    for participant in bot.participants:
        participant.pounced = False

    await ctx.send(reply)


@bot.command(name="startPounce")
async def start_pounce(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if bot.pouncing_allowed:
        reply = await create_colored_message(
            "Pounce is already open",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    bot.pouncing_allowed = True
    bot.pounces = []

    reply = await create_colored_message(
        "Pouncing for this question is now allowed.\n\n"
        + "DM your answers to the bot as 'qc!pounce answer'",
        swearing=False
    )

    await ctx.send(reply)


@bot.command(name="endPounce")
async def end_pounce(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.pouncing_allowed:
        reply = await create_colored_message(
            "Pounce is already closed",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    bot.pouncing_allowed = False
    reply = "```fix\n\n\nPounces for this question - \n\n```"
    reply += "\n\n".join(bot.pounces)

    await bot.quizmaster_channel.send(reply)

    reply = await create_colored_message(
        "Pouncing for this round is closed",
        swearing=False
    )

    await ctx.send(reply)


@bot.command(name="bounce")
async def bounce(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.question_ongoing:
        reply = await create_colored_message(
            "There's no ongoing question",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = ctx.author.mention
    reply += await create_colored_message(
        "Question is begin bounced over",
        swearing=False
    )

    await pass_and_bounce_util(ctx, reply)


@bot.command(name="score")
async def score(ctx, points, *participants):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    try:
        points = int(points)
    except ValueError:
        reply = await create_colored_message(
            "Points are supposed to be integers",
            swearing=False
        )
        await ctx.send(reply)

    reply = "```fix\n"
    for participant in participants:
        try:
            team_num = int(participant) - 1
            reply += "\t{}'s score went from {} to {}.\n".format(
                bot.participants[team_num].member,
                bot.participants[team_num].score,
                bot.participants[team_num].score + points,
            )
            bot.participants[team_num].score += points
            bot.next_direct = team_num + 1

        except (ValueError, IndexError):
            reply += "Error - Could not score participant number {}".format(
                participant
            )
            reply += ".\n"

    reply += "```"
    await ctx.send(reply)


@bot.command(name="bounceType")
async def bounce_type(ctx, bounce_type):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if bounce_type != "bangalore" and bounce_type != "normal":
        reply = await create_colored_message(
            "Unknown bounce type",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    bot.bounce_type = bounce_type
    reply = await create_colored_message(
        f"Bounce type changed to {bounce_type}",
        swearing=False
    )
    await ctx.send(reply)


@bot.command(name="kick")
async def kick(ctx, *participants):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = "```fix\n"
    for num in participants:
        try:
            team_num = int(num) - 1
            participant = bot.participants[team_num]

            if participant.kicked:
                continue

            reply += "{} [Number. {}] has been kicked from the quiz".format(
                participant.member,
                participant.id + 1,
            )
            reply += ".\n"
            participant.kicked = True
        except (KeyError, ValueError, IndexError):
            reply += f"Error - Could not kick participant number {num}.\n"

    reply += "```"

    await ctx.send(reply)


@bot.command(name="quizFile")
async def quiz_file(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not isinstance(ctx.message.channel, discord.DMChannel):
        await ctx.message.delete()
        reply = await create_colored_message(
            "Send file on DM",
            swearing=bot.swearing)
        await ctx.send(reply)
        return

    if not ctx.message.attachments:
        reply = await create_colored_message(
            "Could not find file",
            swearing=bot.swearing)
        await ctx.send(reply)
        return

    images = None
    try:
        attachment = ctx.message.attachments[0]
        attachment_bytes = await attachment.read()
        images = convert_from_bytes(attachment_bytes, fmt="JPEG")
    except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError):
        reply = await create_colored_message(
            "Error in PDF file",
            swearing=False
        )
        await ctx.send(reply)
        return

    reply = await create_colored_message(
        "Received the file",
        swearing=False
    )

    bot.quiz_file = images
    bot.curr_slide = -1

    await ctx.send(reply)


@bot.command(name="slide")
async def slide(ctx, num=None):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if bot.quiz_file is None or len(bot.quiz_file) == 0:
        reply = await create_colored_message(
            "No slide to display",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if num is not None:
        try:
            num = int(num) - 1
            bot.curr_slide = num
        except ValueError:
            reply = await create_colored_message(
                "Slide number not an integer",
                swearing=bot.swearing
            )
            await ctx.send(reply)
            return
    else:
        bot.curr_slide += 1

    bot.slide_message = await send_slide(ctx, bot)


@bot.command(name="addQM")
async def add_quizmaster(ctx, *text):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author not in bot.quizmasters:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    for member in ctx.message.mentions:
        bot.quizmasters.append(member)

        reply = await create_colored_message(
            f"{member} has been added as QM",
            swearing=False
        )

        await ctx.send(reply)
