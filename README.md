# Among Us Discord Bot

### Invite

The bot is still in development, if any issues arise please report it on GitHub

https://discord.com/oauth2/authorize?client_id=750905866827464825&scope=bot&permissions=101376

### Commands
- `!about` - Generic about message
- `!makeroom` - Makes the room. You must be in a Voice Channel for the command to work
- `!join` - Join the waiting list
- `!leave` - Leave the waiting list
- `!add` - Add a player to the waiting list (requires ownership)
- `!remove` - Removes a player from the waiting list (requires ownership)
- `!removeall` - Clears the waiting list (requires ownership)
- `!transferowner` - Transfers the room owner to someone else (requires ownership)
- `!setcode` - Set the Among Us private game code (requires ownership)
- `!toggleautodelete` - Toggles this property of the room: when no players are remaining in the Voice Channel, the room is auto deleted. This setting is ON by default (requires ownership)
- `!deleteroom` - Deletes the room (requires ownership or manage server perms)
- `!list` - Lists the users in the waiting list
- `!room` - Returns the jump url for the original room message

### Dev Commands
- `!debugmakeroom` - Allows you to make a room without being in a Voice Channel by using Channel IDs.
- `!dump` - Dumps the room information into a json file
- `!restore` - Restores a room from a json file if the bot dies (can only be done by the bot owner)