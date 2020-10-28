import discord
import io
import sys
import json
import os

current_rooms = []
OWNER = 258002965833449472

about = discord.Embed(title="Among Us", type='rich', color=discord.Color.from_rgb(207, 25, 32),
                      url="https://github.com/Minibeast/amongus-discord-bot")
about.set_thumbnail(url="https://i.imgur.com/lsXr8my.png")
about.add_field(name="About", value="This bot was made by [Minibeast](https://minibeast.github.io), and focuses on "
                                    "creating a seamless way for big Discord servers to manage a waiting list and game "
                                    "information for the game [Among Us](https://wikipedia.org/wiki/Among_Us).")

about.add_field(name="Commands",
                value="!makeroom - Makes a room\n!deleteroom - Deletes the room\n!join - Join the waiting "
                      "list\n!leave - Leave the waiting list\n!list - Lists the users in the waiting list\n!room - "
                      "Returns the jump url for the original room message\n\nAll the bot's commands are listed "
                      "on the GitHub's [README page]("
                      "https://github.com/Minibeast/amongus-discord-bot/blob/master/README.md).", inline=False)


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
        self.autodelete = True

    def update_max(self, max_players):
        self.max_players = max_players

    def update_owner(self, owner):
        self.owner = owner

    def update_code(self, code):
        self.code = code


async def update_room(room):
    voice_members = ""
    room.lobby = room.channel.members
    for x in room.lobby:
        voice_members += str(x.name) + "\n"

    if len(voice_members) == 0:
        voice_members = "No Players"
        if room.autodelete:
            await room.message.channel.send(f"<@{room.owner.id}> The Among Us room closed automatically because all "
                                            f"players left the associated Voice Channel '{room.channel.name}'.\nFor "
                                            f"reference, this feature can be toggled "
                                            f"with the command `!toggleautodelete`")
            await room.message.delete()
            current_rooms.remove(room)
            return

    room.embed.clear_fields()
    room.embed.add_field(name="In Lobby ({0}/{1})".format(len(room.lobby), room.max_players), value=voice_members)

    waiting_members = ""
    for x in room.waiting:
        if x not in room.lobby:
            waiting_members += str(x.name) + "\n"
        else:
            for i in current_rooms:
                if x in i.waiting:
                    i.waiting.remove(x)

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
        print('Logged on as {0}!\n'.format(self.user))
        async for guild in client.fetch_guilds():
            print(guild.name)

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

        if message.content.startswith("!about"):
            await message.channel.send(embed=about)

        elif message.content.startswith("!makeroom"):
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

        elif message.content.lower().startswith("!join") or message.content.lower().startswith("!peepoarrive"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author in x.waiting:
                        return
                    else:
                        x.waiting.append(message.author)
                        await update_room(x)
                        await message.add_reaction('✔️')
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
                await message.add_reaction('✔️')
            else:
                await message.channel.send("Only the room owner can change this value!")

        elif message.content.startswith("!leave") or message.content.lower().startswith("!peepoleave"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author in x.waiting:
                        x.waiting.remove(message.author)
                        await update_room(x)
                        await message.add_reaction('✔️')
                        return

        elif message.content.startswith("!deleteroom"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner or message.author.permissions_in(message.channel).manage_guild:
                        await x.message.delete()
                        current_rooms.remove(x)
                        await message.add_reaction('✔️')
                        return

        elif message.content.startswith("!setcode"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner:
                        try:
                            x.code = message.content.split()[1].upper()
                            await update_room(x)
                            await message.add_reaction('✔️')
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

        elif message.content.startswith("!dump"):
            data = {
                "channel": None,
                "waiting": [],
                "owner": None,
                "message": None
            }
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    for member in x.waiting:
                        data["waiting"].append(member.id)

                    data["channel"] = x.channel.id
                    data["owner"] = x.owner.id
                    data["text_channel"] = x.message.channel.id
                    data["message"] = x.message.id

                    break

            if data["channel"] is None:
                return

            amongus_dump = io.BytesIO(bytes(json.dumps(data), encoding="utf-8"))

            await message.channel.send(file=discord.File(amongus_dump, filename="amongus_roomdump.json"))

        elif message.content.startswith("!restore"):
            if message.author.id != OWNER:
                return

            try:
                await message.attachments[0].save("amongus_data.json")
            except LookupError and discord.HTTPException:
                await message.channel.send("Failed. Remember to attach a file")
                return

            with open("amongus_data.json") as amongus_data:
                restore_content = json.loads(amongus_data.read())
                amongus_data.close()

                try:
                    if not isinstance(restore_content["owner"], int) \
                            and not isinstance(restore_content["channel"], int) \
                            and not isinstance(restore_content["text_channel"], int) \
                            and not isinstance(restore_content["message"], int) \
                            and not isinstance(restore_content["waiting"], list):
                        await message.channel.send("Invalid file, aborting")
                        return
                except LookupError:
                    await message.channel.send("Invalid file, aborting")
                    return

                owner = discord.utils.find(lambda o: o.id == restore_content["owner"], message.channel.guild.members)
                channel = discord.utils.find(lambda c: c.id == restore_content["channel"],
                                             message.channel.guild.channels)

                text_channel = discord.utils.find(lambda c: c.id == restore_content["text_channel"],
                                                  message.channel.guild.channels)

                waiting = []
                for x in restore_content["waiting"]:
                    waiting.append(discord.utils.find(lambda m: m.id == x, message.channel.guild.members))

                current = AmongUs(owner, channel)
                current_rooms.append(current)
                current.waiting = waiting
                current.message = await text_channel.fetch_message(restore_content["message"])

                await update_room(current)
                os.remove("amongus_data.json")

        elif message.content.startswith("!remove"):
            if len(message.mentions) == 0:
                await message.channel.send("Please @ the user who you would like to kick.")
                return

            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner:
                        for i in x.waiting:
                            if i == message.mentions[0]:
                                x.waiting.remove(i)
                                await update_room(x)
                                await message.add_reaction('✔️')
                                return
                        await message.channel.send("Could not find user in waiting")
                        return

        elif message.content.startswith("!removeall"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner:
                        x.waiting = []
                        await update_room(x)
                        await message.add_reaction('✔️')
                        return

        elif message.content.startswith("!room"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    await message.channel.send(x.message.jump_url)

        elif message.content.startswith("!toggleautodelete"):
            for x in current_rooms:
                if x.guild == message.channel.guild:
                    if message.author == x.owner:
                        if x.autodelete:
                            x.autodelete = False
                        else:
                            x.autodelete = True
                        await message.add_reaction('✔️')
                        return


if __name__ == "__main__":
    client = MyClient()
    client.run(str(sys.argv[1]))
