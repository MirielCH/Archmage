# Archmage

Simple enchant mute for EPIC RPG.  
Goes without saying but nonetheless: Please note that you can not mute yourself in a server that you are admin in.  

**Setup**
• Make a copy of `default.env` and name the copy `.env`. Edit the file, and change `DISCORD_TOKEN` to your bot token. In your live bot, change the setting `DEBUG_MODE` to `OFF`. This will register the slash commands as global commands (see below).
• Make a copy of `default_db.db` and name the copy `archmage_db.db`.
• Change `OWNER_ID` and `DEV_GUILDS` in `resources/settings.py` to your liking.

**Usage**  
This bot uses the following slash commands:
• `set enchant`: Sets a target enchant
• `settings`: Shows your current enchant
• `about`: Shows some bot stats (bot latency, API latency, user count, server count)
• `dev reload`: Reloads cogs and modules. Does not work properly at this date due to bugs in the pycord library.
• `dev shutdown`: Shuts down the bot.
The two dev commands are never registered globally, no matter the `DEBUG_MODE` setting. They are also only usable by the owner.

**Permissions**
The bot needs the following permissions to run properly:
• The scope `application.commands` in the guild for the slash commands.
• Permissions `Send Messages`, `Change Permissions`, `Add Reactions` and `View Channel` in the channel you want use the bot in.
Note that due to the fact that slash commands work outside of the channel permissions currently, you can set an enchant in channels where the bot won't mute. The bot checks for these permissions when setting an enchant and lets you know when it wont't work.

**Warning Emojis**
If the bot reacts with a warning emoji to an enchant message, it either couldn't extract necessary data from the embed or it couldn't find the user that triggered the enchant. If you encounter such a warning emoji, you should have a close look at the user name of the user that enchanted and see in the debugger to find out what is going wrong.
