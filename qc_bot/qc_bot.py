from discord.ext import commands

from qc_bot.util import prefix
# TODO
# Allow quizes on multiple channels


class QCBot(commands.Bot):
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
        self.bounce_type = "bangalore"
        self.swearing = True
        self.quiz_file = None
        self.curr_slide = None
        self.slide_message = None


bot = QCBot()
bot.remove_command(name="help")
