import discord


class QCClient(discord.Client):
    """ TODO - Add docstring
    """

    def __init__(self):
        super(QCClient, self).__init__()
        self.quiz_ongoing = None
        self.quiz_name = None
        self.quiz_master = None
        self.scorers = None
        self.quiz_participants = None
        self.no_of_participants = None
        self.curr_participant = None
        self.pouncing_allowed = None
        self.joining_allowed = None
        self.clockwise = None
        self.quiz_file = None

    async def on_ready(self):
        print(self.user)

    async def on_message(self, message):
        split_message = message.content.split()

        if split_message[0] == "qc!help":
            await self.help(message)
            return

        if split_message[0] == "qc!start_quiz":
            if not self.quiz_ongoing:
                await self.start_quiz(message, split_message)
            else:
                return_message = "```There's already a fucking quiz" + \
                        f"({self.quiz_name}) going on, ya moron.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!end_quiz":
            if self.quiz_ongoing:
                await self.end_quiz(message)
            else:
                return_message = "```There's no ongoing quiz, ya shitfuck.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!start_joining":
            if self.quiz_ongoing:
                if self.joining_allowed:
                    return_message = "```Joining is already allowed, ya weirdo.```"
                    await message.channel.send(return_message)
                    return

                if message.author != self.quiz_master:
                    return_message = "```You are not the QM, you idjit.```"
                    await message.channel.send(return_message)
                    return

                self.joining_allowed = True

                return_message = f"```Joining period for " + \
                    f"{self.quiz_name} has begun.\n\n"

                return_message += "Type qc!join nick to join the quiz.```"
                await message.channel.send(return_message)
            else:
                return_message = "```There's no ongoing quiz, ya cunt.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!end_joining":
            if self.quiz_ongoing:
                if not self.joining_allowed:
                    return_message = "```Joining is already forbidden, ya nitwit.```"
                    await message.channel.send(return_message)
                    return

                if message.author != self.quiz_master:
                    return_message = "```You are not the QM, you idjit.```"
                    await message.channel.send(return_message)
                    return

                self.joining_allowed = False

                return_message = f"```Joining period for " + \
                    f"{self.quiz_name} has ended.\n\n```"

                await message.channel.send(return_message)
            else:
                return_message = "```There's no ongoing quiz, ya retard.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!join":
            if self.quiz_ongoing:
                if not self.joining_allowed:
                    return_message = "```Joining is forbidden, ya fucker.```"
                    await message.channel.send(return_message)
                    return

                await self.join_quiz(message, split_message)
            else:
                return_message = "```There's no ongoing quiz, ya dick.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!list_participants":
            if self.quiz_ongoing:
                await self.list_participants(message)
            else:
                return_message = "```There's no ongoing quiz, ya dimwit.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!scoreboard":
            if self.quiz_ongoing:
                await self.scoreboard(message)
            else:
                return_message = "```There's no ongoing quiz, ya dunce.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!pass":
            if self.quiz_ongoing:
                await self.pass_question(message)
            else:
                return_message = "```There's no ongoing quiz, ya dolt.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!bounce":
            if self.quiz_ongoing:
                if message.author != self.quiz_master:
                    return_message = "```You are not the QM, you dumbbell.```"
                    await message.channel.send(return_message)
                    return

                await self.bounce(message)
            else:
                return_message = "```There's no ongoing quiz, ya dolt.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!score":
            if self.quiz_ongoing:
                if message.author != self.quiz_master:
                    return_message = "```You are not the QM, you idjit.```"
                    await message.channel.send(return_message)
                    return

                await self.score(message, split_message)
            else:
                return_message = "```There's no ongoing quiz, ya retard.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!pounce_round":
            if self.quiz_ongoing:
                if message.author != self.quiz_master:
                    return_message = "```You are not the QM, you buffoon.```"
                    await message.channel.send(return_message)
                    return

                await self.pounce_round(message, split_message)
            else:
                return_message = "```There's no ongoing quiz, ya nincompoop.```"
                await message.channel.send(return_message)
            return

        if split_message[0] == "qc!next_question":
            if self.quiz_ongoing:
                if message.author != self.quiz_master:
                    return_message = "```You are not the QM, you ninny.```"
                    await message.channel.send(return_message)
                    return

                await self.next_question(message, split_message)
            else:
                return_message = "```There's no ongoing quiz, ya cretin.```"
                await message.channel.send(return_message)
            return

    async def help(self, message):
        return_message = "```Help for BPHC Quiz Club Bot.\n\n"
        return_message += "Here's a list of commands -\n\n"
        return_message += "\tqc!help - get a list of commands\n\n"
        return_message += "\tqc!start_quiz quiz_name - start a quiz with given name with you as qm\n\n"
        return_message += "\tqc!end_quiz - end the quiz\n\n"
        return_message += "\tqc!start_joining - for qm start joining period for quiz participants\n\n"
        return_message += "\tqc!end_joining - for qm end joining period for quiz participants\n\n"
        return_message += "\tqc!join nick - join quiz with given nick as your team-name\n\n"
        return_message += "\tqc!list_participants - view a list of participants\n\n"
        return_message += "\tqc!scoreboard - view the current scoreboard\n\n"
        return_message += "\tqc!pass - pass your direct\n\n"
        return_message += "\tqc!bounce - for qm to bounce the direct\n\n"
        return_message += "\tqc!score [participans ...] points - for qm to score the participants\n\n"
        return_message += "\tqc!pounce_round dir - new pounce round in given direction\n\n"
        return_message += "\tqc!next_question direct_team - give next question to direct team\n\n"
        return_message += "```"
        await message.channel.send(return_message)

    async def start_quiz(self, message, split_message):
        if len(split_message) < 2:
            return_message = "```That is not how it's done, ya infidel.\n\n"
            return_message += "correct usage:\n"
            return_message += "\t\tqc!start_quiz quiz_name```"
            await message.channel.send(return_message)
            return

        self.quiz_ongoing = True
        self.quiz_name = split_message[1]
        self.quiz_master = message.author
        self.scorers = []
        self.quiz_participants = {}
        self.participating = {}
        self.no_of_participants = 0
        self.joining_allowed = False
        self.pouncing_allowed = False

        return_message = f"```Starting quiz - {self.quiz_name}.\n\n"
        return_message += f"{self.quiz_master} will be your QM for this quiz.```"

        await message.channel.send(return_message)

    async def end_quiz(self, message):
        self.quiz_ongoing = None
        self.quiz_name = None
        self.quiz_master = None
        self.scorers = None
        self.quiz_participants = None
        self.no_of_participants = None
        self.curr_participant = None
        self.pouncing_allowed = None
        self.joining_allowed = None

        return_message = f"```Ending quiz - {self.quiz_name}.```"
        await message.channel.send(return_message)

    async def join_quiz(self, message, split_message):
        if len(split_message) < 2:
            return_message = "```That is not how it's done, ya asshole.\n\n"
            return_message += "correct usage:\n"
            return_message += "\t\tqc!join nick```"
            await message.channel.send(return_message)
            return

        if self.participating.get(str(message.author)):
            return_message = "```You are already participating, ya mofo.\n\n```"
            await message.channel.send(return_message)
            return

        participant = {
                "id": message.author,
                "nick": split_message[1],
                "score": 0,
                "num": self.no_of_participants
        }
        self.quiz_participants[self.no_of_participants] = participant
        self.no_of_participants += 1

        self.participating[str(message.author)] = True

        return_message = message.author.mention + \
            f" `has joined the quiz as " + \
            f"participant no. {self.no_of_participants}.`"

        await message.channel.send(return_message)

    async def list_participants(self, message):
        return_message = f"```List of participants in {self.quiz_name} -"
        return_message += "\n\n"

        for idx, participant in self.quiz_participants.items():
            return_message += "\t{}. {} as {}".format(
                idx + 1,
                participant["id"],
                participant["nick"],
            )
            return_message += "\n"

        return_message += "```"
        await message.channel.send(return_message)

    async def scoreboard(self, message):

        sorted_list = sorted(self.quiz_participants.values(), key=lambda item: item["score"], reverse=True)
        return_message = f"```Scoreboard for {self.quiz_name} -"
        return_message += "\n\n"

        for idx, participant in enumerate(sorted_list):
            return_message += "\t{}. {} as {} - {} points".format(
                idx + 1,
                participant["id"],
                participant["nick"],
                participant["score"]
            )
            return_message += "\n"

        return_message += "```"
        await message.channel.send(return_message)

    async def pass_question(self, message):
        if message.author != self.quiz_participants[self.curr_participant]["id"]:
            return_message = "``` It's not your turn, you. blockhead```"
            await message.channel.send(return_message)
            return

        return_message = message.author.mention + " `has passed his turn.`\n\n"
        if self.clockwise:
            self.curr_participant = (self.curr_participant + 1) % self.no_of_participants
        else:
            self.curr_participant = (self.curr_participant - 1) % self.no_of_participants

        next_participant = self.quiz_participants[self.curr_participant]
        return_message += next_participant["id"].mention + " `'s turn to answer next.`"
        await message.channel.send(return_message)

    async def bounce(self, message):
        if self.clockwise:
            self.curr_participant = (self.curr_participant + 1) % self.no_of_participants
        else:
            self.curr_participant = (self.curr_participant - 1) % self.no_of_participants

        next_participant = self.quiz_participants[self.curr_participant]
        return_message = next_participant["id"].mention + " `'s turn to answer next.`"
        await message.channel.send(return_message)

    async def score(self, message, split_message):
        if len(split_message) < 2:
            return_message = "```That is not how it's done, ya ignoramus.\n\n"
            return_message += "correct usage:\n"
            return_message += "\t\tqc!score [participans ...] points```"
            await message.channel.send(return_message)
            return

        points = None
        try:
            points = int(split_message[-1])
        except Exception:
            return_message = "``` Points are supposed to be integers, you fucktard.```"
            await message.channel.send(return_message)
            return

        return_message = ""
        for num in split_message[1:-1]:
            try:
                team_num = int(num) - 1
                return_message += "\t{}'s score went from {} to {}.\n".format(
                    self.quiz_participants[team_num]["id"],
                    self.quiz_participants[team_num]["score"],
                    self.quiz_participants[team_num]["score"] + points,
                )
                self.quiz_participants[team_num]["score"] += points

            except Exception:
                pass

        if len(return_message) > 0:
            return_message = "```Done scoring -\n\n" + return_message + "```"
            await message.channel.send(return_message)

    async def pounce_round(self, message, split_message):
        if len(split_message) < 2:
            return_message = "```That is not how it's done, ya imbecile.\n\n"
            return_message += "correct usage:\n"
            return_message += "\t\tqc!pounce_round dir```"
            await message.channel.send(return_message)
            return

        return_message = " pounce round beginning."
        if split_message[1] == "CW":
            return_message = "Clockwise" + return_message
            self.clockwise = True
        elif split_message[1] == "ACW":
            return_message = "Anti-Clockwise" + return_message
            self.clockwise = False
        else:
            return_message = "That's not a valid direction, you pinhead."

        return_message = "```" + return_message + "```"
        await message.channel.send(return_message)

    async def next_question(self, message, split_message):
        if len(split_message) < 2:
            return_message = "```That is not how it's done, ya dork.\n\n"
            return_message += "correct usage:\n"
            return_message += "\t\tqc!next_question direct_team```"
            await message.channel.send(return_message)
            return

        direct_participant = None
        try:
            self.curr_participant = int(split_message[-1]) - 1
            direct_participant = self.quiz_participants[self.curr_participant]["id"]
        except Exception:
            return_message = "``` Team numbers are supposed to be integers, you fucktard.```"
            await message.channel.send(return_message)
            return

        return_message = ""
        if self.quiz_file is not None:
            pass

        return_message = "`New question -` " + direct_participant.mention + "`'s direct.`"

        await message.channel.send(return_message)


if __name__ == "__main__":

    client = QCClient()
    client.run("NjkxNzIzMDUzMTMwMDU1Nzkx.XnkvXg.hSNLP5eCvVvD8pVOP9sO0dbHTVc")
