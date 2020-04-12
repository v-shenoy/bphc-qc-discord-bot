class QuizCommand:
    """ Class containing the list of commands that the bot offers.

    Contains a dictionary mapping the name to the usage, and
    help description.
    """

    # General Commands
    command_help = {
        "usage": "help",
        "desc": "display the help menu",
        "general": True}
    command_start_quiz = {
        "usage": "startQuiz quiz_name",
        "desc": "become the QM, and start a quiz with given name",
        "general": True}
    command_join = {
        "usage": "join nick",
        "desc": "join the quiz with chosen nick",
        "general": True}
    command_list = {
        "usage": "list",
        "desc": "view the members participating in the quiz",
        "general": True}
    command_scoreboard = {
        "usage": "scoreboard",
        "desc": "view the scoreboard for the quiz",
        "general": True}
    command_pass = {
        "usage": "pass",
        "desc": "pass your direct to the next participant",
        "general": True}
    command_remind = {
        "usage": "remind",
        "desc": "remind the current participant to answer the question",
        "general": True}
    command_pounce = {
        "usage": "pounce answer",
        "desc": "pounce on the current question with your answer on DM " +
                "to the bot",
        "general": True}
    command_clues = {
        "usage": "clues",
        "desc": "set up a poll for checking if people want clues",
        "general": True}
    command_swearing = {
        "usage": "swearing mode",
        "desc": "set swearing mode on (default) or off",
        "general": True}
    command_leave = {
        "usage": "leave",
        "desc": "leave the quiz",
        "general": True}

    # QM Only Commands
    command_end_quiz = {
        "usage": "endQuiz",
        "desc": "end the quiz",
        "general": False}
    command_start_joining = {
        "usage": "startJoining",
        "desc": "start the joining period for the quiz",
        "general": False}
    command_end_joining = {
        "usage": "endJoining",
        "desc": "end the joining period for the quiz",
        "general": False}
    command_pounce_round = {
        "usage": "pounceRound direction",
        "desc": "start a pounce round in given direction, CW (default) or ACW",
        "general": False}
    command_direct = {
        "usage": "direct [team_number]",
        "desc": "give the next question with a chosen direct team (optional)",
        "general": False}
    command_start_pounce = {
        "usage": "startPounce",
        "desc": "start pouncing period for the current question",
        "general": False}
    command_end_pounce = {
        "usage": "endPounce",
        "desc": "end pouncing period for the current question",
        "general": False}
    command_bounce = {
        "usage": "bounce",
        "desc": "bounce the question to the next team",
        "general": False}
    command_score = {
        "usage": "score points participant1 participant2...",
        "desc": "give scores to the participants",
        "general": False}
    command_bounce_type = {
        "usage": "bounceType type",
        "desc": "set bounce type bangalore (default) or normal",
        "general": False}
    command_kick = {
        "usage": "kick team_num1 team_num2...",
        "desc": "kick participants from the quiz",
        "general": False}
    command_quiz_file = {
        "usage": "quizFile [along with an attached pdf file]",
        "desc": "send the bot the pdf file to be used for the quiz",
        "general": False}
    command_slide = {
        "usage": "slide [ slide_number ]",
        "desc": "send the given numbered slide, number is optional",
        "general": False}


class Participant:
    """ Participant in the quiz.

    Mostly a bag of data.

    Attribute:
        id (int): unique id number given the to participant
        member (discord.user.User): object representing Discord member
        nick (str): nick of the participant for the quiz
        score (int): score of the participant for the quiz
        kicked (bool): if the participant has left the quiz
        pounced (bool): if participant has pounced for the current question
    """

    def __init__(self, idt, member, nick):
        self.id = idt
        self.member = member
        self.nick = nick
        self.score = 0
        self.kicked = False
        self.pounced = False
