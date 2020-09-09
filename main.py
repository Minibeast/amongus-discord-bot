import discord
import sys

current_rooms = []


class AmongUs:
    def __init__(self, owner, channel):
        self.channel = channel
        self.guild = channel.guild
        self.lobby = channel.members
        self.waiting = []
        self.max_players = 10
        self.owner = owner
        self.code = ""
        self.embed = discord.Embed(title="Among Us", type='rich', color=discord.Color.from_rgb(207, 25, 32))
        self.embed.set_thumbnail(url="https://i.imgur.com/lsXr8my.png")
        self.embed.set_footer(text="Room Owner: {}".format(self.owner))
        self.message = None

    def update_max(self, max_players):
        self.max_players = max_players

    def update_owner(self, owner):
        self.owner = owner

    def update_code(self, code):
        self.code = code

    def kick(self, username=None, user=None):
        print("kick code")


async def update_room(room):
    voice_members = ""
    room.lobby = room.channel.members
    for x in room.lobby:
        voice_members += str(x.name) + "\n"

    if len(voice_members) == 0:
        voice_members = "No Players"

    room.embed.clear_fields()
    room.embed.add_field(name="In Lobby ({0}/{1})".format(len(room.lobby), room.max_players), value=voice_members)

    waiting_members = ""
    for x in room.waiting:
        if x not in room.lobby:
            waiting_members += str(x.name) + "\n"
        else:
            room.waiting.remove(x)

    if len(waiting_members) == 0:
        waiting_members = "No Players"

    room.embed.add_field(name="Waiting ({})".format(len(room.waiting)), value=waiting_members)

    room.embed.set_footer(text="Room Owner: {}".format(room.owner))

    if len(room.code) != 0:
        room.embed.description = "Code: {}".format(room.code)

    try:
        await room.message.edit(embed=room.embed)
    except discord.errors.NotFound:
        current_rooms.remove(room)
        return


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_voice_state_update(self, member, before, after):
        for x in current_rooms:
            if before.channel is not None and before.channel == x.channel:
                await update_room(x)
            elif after.channel is not None and after.channel == x.channel:
                await update_room(x)

    async def on_message(self, message):
        if message.author == client.user:
            return

        def check(arg):
            return message.author == arg.author

        if message.content.startswith("!makeroom"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    return

            voice_chan = None
            game_owner = None
            for x in message.guild.channels:
                if type(x) == discord.channel.VoiceChannel:
                    for i in x.members:
                        if i == message.author:
                            game_owner = message.author
                            voice_chan = x

            if voice_chan is None:
                await message.channel.send("Please be connected to a Voice Channel!")
                return

            current = AmongUs(game_owner, voice_chan)
            current_rooms.append(current)

            current.message = await message.channel.send(embed=current.embed)
            await update_room(current)
            # await current_rooms[len(current_rooms) - 1]["message"].pin(reason="Among Us game")

        elif message.content.startswith("!join"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author in x.waiting:
                        return
                    else:
                        x.waiting.append(message.author)
                        await update_room(x)
                        return

        elif message.content.startswith("!transferowner"):
            if len(message.mentions) == 0:
                await message.channel.send("Please @ the user who you would like to transfer room ownership to.")
                return

            room = None

            for x in current_rooms:
                if x.guild == message.channel.guild:
                    room = x

            if room is None:
                return

            if message.author == room.owner:
                room.update_owner(message.mentions[0])
                await update_room(room)
            else:
                await message.channel.send("Only the room owner can change this value!")

        elif message.content.startswith("!leave"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author in x.waiting:
                        x.waiting.remove(message.author)
                        await update_room(x)
                        return

        elif message.content.startswith("!deleteroom"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner or message.author.permissions_in(message.channel).manage_guild:
                        await x.message.delete()
                        current_rooms.remove(x)
                        return

        elif message.content.startswith("!setcode"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner:
                        try:
                            x.code = message.content.split()[1].upper()
                            await update_room(x)
                        except IndexError and LookupError:
                            await message.channel.send("Please enter the code with the command")

        elif message.content.startswith("!list"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    await update_room(x)
                    waiting_list = ""
                    for i in x.waiting:
                        waiting_list += str(i.name) + "\n"

                    if len(waiting_list) == 0:
                        waiting_list = "No Waiting"

                    await message.channel.send(waiting_list)
                    return


client = MyClient()
client.run(str(sys.argv[1]))
