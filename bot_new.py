import random
import sys
import io

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import DMChannel
import emojis
from pdf2image import convert_from_bytes

# TODO
# Allow quizes on multiple channels

# Constants
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


async def create_colored_message(message, swearing, plural=False):
    error = f"```fix\n{message}"
    if swearing:
        error += ", " + random.choice(swears)
    if plural:
        error += "s"
    error += ".```"

    return error


async def send_image(ctx, bot, direction="Forward"):
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


# Class Definitions
class Participant:
    """ Participant in the quiz.

    Mostly a bag of data.

    Attribute:
        id (int): unique id number given the to participant
        member (discord.user.User): object representing Discord member
        nick (str): nick of the participant for the quiz
        score (int): score of the participant for the quiz
    """

    def __init__(self, idt, member, nick, score=0):
        self.id = idt
        self.member = member
        self.nick = nick
        self.score = score


class QuizCommands:
    """ Class containing the list of commands that the bot offers.

    Contains a dictionary mapping the name to the usage, and
    help description.
    """

    # General Commands
    command_help = {
        "usage": "help",
        "desc": "display the help menu"}
    command_start_quiz = {
        "usage": "startQuiz quiz_name",
        "desc": "become the QM, and start a quiz with given name"}
    command_join = {
        "usage": "join nick",
        "desc": "join the quiz with chosen nick"}
    command_list = {
        "usage": "list",
        "desc": "view the members participating in the quiz"}
    command_scoreboard = {
        "usage": "scoreboard",
        "desc": "view the scoreboard for the quiz"}
    command_pass = {
        "usage": "pass",
        "desc": "pass your direct to the next participant"}
    command_remind = {
        "usage": "remind",
        "desc": "remind the current participant to answer the question"}
    command_pounce = {
        "usage": "pounce answer",
        "desc": "pounce on the current question with your answer on DM " +
                "to the bot"}
    command_clues = {
        "usage": "clues",
        "desc": "set up a poll for checking if people want clues"
    }
    command_swearing = {
        "usage": "swearing mode",
        "desc": "set swearing mode on (default) or off"}

    # QM Only Commands
    command_end_quiz = {
        "usage": "endQuiz",
        "desc": "end the quiz"}
    command_start_joining = {
        "usage": "startJoining",
        "desc": "start the joining period for the quiz"}
    command_end_joining = {
        "usage": "endJoining",
        "desc": "end the joining period for the quiz"}
    command_pounce_round = {
        "usage": "pounceRound direction",
        "desc": "start a pounce round in given direction, CW (default) or ACW"}
    command_direct = {
        "usage": "direct [team_number]",
        "desc": "give the next question with a chosen direct team (optional)"}
    command_start_pounce = {
        "usage": "startPounce",
        "desc": "start pouncing period for the current question"}
    command_end_pounce = {
        "usage": "endPounce",
        "desc": "end pouncing period for the current question"}
    command_bounce = {
        "usage": "bounce",
        "desc": "bounce the question to the next team"}
    command_score = {
        "usage": "score points participant1 participant2...",
        "desc": "give scores to the participants"}
    command_bounce_type = {
        "usage": "bounceType type",
        "desc": "set bounce type bangalore (default) or normal"}
    command_kick = {
        "usage": "kick team_num1 team_num2...",
        "desc": "kick participants from the quiz"}
    command_quiz_file = {
        "usage": "quizFile [along with an attached pdf file]",
        "desc": "send the bot the pdf file to be used for the quiz"
    }


class QCBot(Bot):
    """ QuizClub bot for helping run pounce-n-bounce quizzes on a Discord
    server.

    Attributes:
        preix (str): prefix for the commands
        quiz_ongoing (bool): indicates whether a quiz is going on currently
        quiz_name (str): name of the quiz going on currently
        quiz_channel (discord.abc.GuildChannel): Channel on which the quiz is
            happening
        quizmaster (discord.user.User): User object of the person that is
            currently the quizmaster
        quizmaster_channel (discord.DMChannel): DMChannel of the current
            quizmaster
        question_ongoing (bool): indicates whether a question is going on
            currently
        participants ([Participant]): list of participants
        participating ({str: bool}): dictionary marking participating members
        no_of_participants (int): number of participants in the quiz
        pouncing_allowed (bool): indicates whether participants can pounce
        joining_allowed (bool): indicates whether new members can join
            the quiz
        direct_participant (int): no. of the participant that got the
            question as direct
        curr_participant (int): no. of the participant currently supposed
            to answer
        next_direct (int): keeps track of who gets the next direct
        pounce_direction (str): CW or ACW represnging clockwise or
            anti-clockwise
        pounces ([Str]): list of pounces for the current question
        pounced ({str:}): dictionary indication which participants have
            pounced
        bounce_type (str): indicates type of bounce, bangalore (default)
            or normal
        swearing (bool): indicates whether the bot should swear or not
        quiz_file (TODO - add class): list of images in the quiz
        curr_slide (int): index into quiz_file
        slide_message (discord.)
    """

    def __init__(self):
        super(QCBot, self).__init__(
            command_prefix=commands.when_mentioned_or(prefix))

        self.prefix = prefix
        self.quiz_ongoing = None
        self.quiz_name = None
        self.quiz_channel = None
        self.quizmaster = None
        self.quizmaster_channel = None
        self.question_ongoing = None
        self.participants = None
        self.participating = None
        self.no_of_participants = 0
        self.pouncing_allowed = None
        self.joining_allowed = None
        self.direct_participant = None
        self.curr_participant = None
        self.next_direct = None
        self.pounce_direction = None
        self.pounces = None
        self.pounced = None
        self.bounce_type = "bangalore"
        self.swearing = True
        self.quiz_file = None
        self.curr_slide = None
        self.slide_message = None

    def reset(self):
        self.quiz_ongoing = None
        self.quiz_name = None
        self.quiz_channel = None
        self.quizmaster = None
        self.quizmaster_channel = None
        self.question_ongoing = None
        self.participants = None
        self.participating = None
        self.no_of_participants = 0
        self.pouncing_allowed = None
        self.joining_allowed = None
        self.direct_participant = None
        self.curr_participant = None
        self.next_direct = None
        self.pounce_direction = None
        self.pounces = None
        self.pounced = None
        self.bounce_type = "bangalore"
        self.swearing = True
        self.quiz_file = None
        self.curr_slide = None
        self.slide_message = None


bot = QCBot()
bot.remove_command(name="help")


# Bot Commands
# General Commands
@bot.command(name="help")
async def command_help(ctx):
    reply = "```fix\n"
    reply += "Help for the Quiz Club Bot.\n"
    reply += f"The prefix for this bot is - {bot.prefix}.\n\n"
    reply += "General Commands - \n\n"
    reply += (
        "\t" + QuizCommands.command_help["usage"] + " -\n\t\t" +
        QuizCommands.command_help["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_start_quiz["usage"] + " -\n\t\t" +
        QuizCommands.command_start_quiz["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_join["usage"] + " -\n\t\t" +
        QuizCommands.command_join["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_list["usage"] + " -\n\t\t" +
        QuizCommands.command_list["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_scoreboard["usage"] + " -\n\t\t" +
        QuizCommands.command_scoreboard["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_pass["usage"] + " -\n\t\t" +
        QuizCommands.command_pass["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_remind["usage"] + " -\n\t\t" +
        QuizCommands.command_remind["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_pounce["usage"] + " -\n\t\t" +
        QuizCommands.command_pounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_swearing["usage"] + " -\n\t\t" +
        QuizCommands.command_swearing["desc"] + "\n")
    reply += "\nQM Commands - \n\n"
    reply += (
        "\t" + QuizCommands.command_end_quiz["usage"] + " -\n\t\t" +
        QuizCommands.command_end_quiz["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_start_joining["usage"] + " -\n\t\t" +
        QuizCommands.command_start_joining["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_end_joining["usage"] + " -\n\t\t" +
        QuizCommands.command_end_joining["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_pounce_round["usage"] + " -\n\t\t" +
        QuizCommands.command_pounce_round["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_direct["usage"] + " -\n\t\t" +
        QuizCommands.command_direct["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_start_pounce["usage"] + " -\n\t\t" +
        QuizCommands.command_start_pounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_end_pounce["usage"] + " -\n\t\t" +
        QuizCommands.command_end_pounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_bounce["usage"] + " -\n\t\t" +
        QuizCommands.command_bounce["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_score["usage"] + " -\n\t\t" +
        QuizCommands.command_score["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_bounce_type["usage"] + " -\n\t\t" +
        QuizCommands.command_bounce_type["desc"] + "\n")
    reply += (
        "\t" + QuizCommands.command_kick["usage"] + " -\n\t\t" +
        QuizCommands.command_kick["desc"] + "\n")
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
    bot.quizmaster = ctx.author
    bot.quizmaster_channel = await bot.quizmaster.create_dm()
    bot.question_ongoing = False
    bot.participants = []
    bot.participating = {}
    bot.pouncing_allowed = False
    bot.joining_allowed = False
    bot.direct_participant = False
    bot.curr_participant = None
    bot.next_direct = 0
    bot.pounce_direction = "CW"
    bot.pounces = None
    bot.pounced = None
    bot.swearing = True

    reply = f"```fix\nStarting quiz - {quiz_name}.\n\n"
    reply += f"{bot.quizmaster} will be your QM for this quiz.```"

    await ctx.send(reply)


@bot.command(name="join")
async def join(ctx, *, nick):
    if ctx.author == bot.quizmaster:
        reply = await create_colored_message(
            "QM cannot join the quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
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

    if bot.participating.get(ctx.author.id) is not None:
        reply = await create_colored_message(
            "You are already participating",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    participant = Participant(
        bot.no_of_participants, ctx.author, nick)

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
        reply += "\t{}. {} as {}".format(
            idx + 1,
            participant.member,
            participant.nick,
        )
        reply += "\n"

    reply += "```"
    await ctx.send(reply)


@bot.command(name="scoreboard")
async def scoreboard(ctx):
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
        reply += "\n"

    reply += "```"
    await ctx.send(reply)


async def pounce_and_bounce_util(ctx, reply):
    while True:
        if bot.pounce_direction == "CW":
            bot.curr_participant = (
                (bot.curr_participant + 1) % bot.no_of_participants
            )
        else:
            bot.curr_participant = (
                (bot.curr_participant - 1) % bot.no_of_participants
            )

        if bot.curr_participant == bot.direct_participant:
            break

        participant = bot.participants[bot.curr_participant]
        if not bot.pounced.get(str(participant.member)):
            break
        else:
            reply += await create_colored_message(
                f"{participant.member} [Number. {participant.id + 1}] "
                + "has pounced. moving on.\n",
                swearing=False
            )

    if bot.curr_participant == bot.direct_participant:
        reply += await create_colored_message(
            "None of you got it",
            bot.swearing,
            swearing=True
        )

        if bot.bounce_type == "bangalore":
            bot.direct_participant = bot.direct_participant + 1

        await ctx.send(reply)
        return

    reply = f"{participant.member.mention}"
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

    await pounce_and_bounce_util(ctx, reply)


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

    if not isinstance(ctx.message.channel, DMChannel):
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

    participant = bot.participants[bot.curr_participant]
    if ctx.author == participant.member:
        reply = await create_colored_message(
            "It's your direct",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if bot.pounced.get(ctx.author.id):
        reply = await create_colored_message(
            "You already pounced",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    bot.pounced[ctx.author.id] = True
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
            "Not a valid mode",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nSwearing has been turned {mode}.```"
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

    if ctx.author != bot.quizmaster:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    reply = f"```fix\nEnding quiz - {bot.quiz_name}.\n"
    reply += f"QM - {bot.quizmaster}.\n\n"
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

    if ctx.author != bot.quizmaster:
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
async def endJoining(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author != bot.quizmaster:
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

    if ctx.author != bot.quizmaster:
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
        bot.direction = direction
        bot.next_direct = 0
    elif direction != "ACW":
        reply = await create_colored_message(
            "Anti-Clockwise pounce round beginning",
            swearing=False
        )
        bot.direction = direction
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

    if ctx.author != bot.quizmaster:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    try:
        team_num = int(team_num) - 1
    except ValueError:
        team_num = bot.next_direct

    if bot.quiz_file is not None and len(bot.quiz_file) != 0:
        bot.curr_slide += 1
        bot.slide_message = await send_image(ctx, bot)

    bot.question_ongoing = True
    bot.direct_participant = team_num
    bot.curr_participant = team_num

    participant = bot.participants[bot.curr_participant]

    reply = f"{participant.member.mention}"
    reply += await create_colored_message(
        f"[Number. {participant.id + 1}] -  It's your turn",
        swearing=False
    )

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

    if ctx.author != bot.quizmaster:
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
    bot.pounced = {}

    reply = await create_colored_message(
        "Pouncing for this question is now allowed.\n\n"
        + "DM your answers to the bot as 'qc!pounce answer'",
        swearing=False
    )

    await ctx.send(reply)


@bot.command(name="endPounce")
async def endPounce(ctx):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author != bot.quizmaster:
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
    reply = "```fix\nPounces for this question - \n\n```"
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

    if ctx.author != bot.quizmaster:
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

    await pounce_and_bounce_util(ctx, reply)


@bot.command(name="score")
async def score(ctx, points, *participants):
    if not bot.quiz_ongoing:
        reply = await create_colored_message(
            "There's no ongoing quiz",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if ctx.author != bot.quizmaster:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    try:
        points = int(points)
    except Exception:
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
            bot.next_direct = team_num

        except (ValueError, IndexError):
            pass

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

    if ctx.author != bot.quizmaster:
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

    if ctx.author != bot.quizmaster:
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
            reply += "{} [Number. {}] has been kicked from the quiz".format(
                participant.member,
                participant.id + 1,
            )
            reply += ".\n"
            del bot.participants[team_num]
        except (ValueError, IndexError):
            pass

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

    if ctx.author != bot.quizmaster:
        reply = await create_colored_message(
            "You are not the QM",
            swearing=bot.swearing
        )
        await ctx.send(reply)
        return

    if not isinstance(ctx.message.channel, DMChannel):
        reply = await create_colored_message(
            "Send file on DM",
            swearing=bot.swearing)
        await ctx.send(reply)
        return

    if not ctx.message.attachments:
        reply = await create_colored_message(
            "Coult not find file",
            swearing=bot.swearing)
        await ctx.send(reply)
        return

    images = []
    for attachment in ctx.message.attachments:
        attachment_bytes = await attachment.read()
        images.extend(convert_from_bytes(attachment_bytes, fmt="JPEG"))

    reply = await create_colored_message(
        "Received the file",
        swearing=False
    )

    bot.quiz_file = images
    bot.curr_slide = -1

    await ctx.send(reply)


# Bot Events
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.system_channel is None:
            pass

        reply = await create_colored_message(
            "Hey, I am up and running now",
            swearing=False
        )

        await guild.system_channel.send(reply)


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
        bot.slide_message = await send_image(
            reaction.message.channel, bot)
    elif reaction.emoji == emojis.encode(":arrow_backward:"):
        bot.curr_slide -= 1
        bot.slide_message = await send_image(
            reaction.message.channel, bot)


@bot.event
async def on_command_error(ctx, error):
    print(error, file=sys.stderr)
    reply = await create_colored_message(
        "I am not really sure what you tried to do there.\n\n"
        + "Try viewing help",
        swearing=bot.swearing
    )

    await ctx.send(reply)


if __name__ == "__main__":
    # This is the old API token for my bot.
    # Replace this with your generated token before running.
    discord_api_key = ""
    bot.run(discord_api_key)
