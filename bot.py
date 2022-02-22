# bot.py

import discord

from discord.ext import commands

from resources import settings


intents = discord.Intents.none()
intents.guilds = True       # For on_guild_join() and all guild objects
intents.messages = True
intents.members = True      # To get the user object from the user name
intents.message_content = True # For detecting enchants


if settings.DEBUG_MODE == 'ON': # Make sure you have debug mode set to ON when debugging
    bot = commands.Bot(help_command=None, case_insensitive=True, intents=intents,
                       debug_guilds=settings.DEV_GUILDS, owner_id=settings.OWNER_ID)
else:
    bot = commands.Bot(help_command=None, case_insensitive=True, intents=intents,
                       owner_id=settings.OWNER_ID)

EXTENSIONS = [
    'cogs.main',
    'cogs.dev',
    'cogs.enchant_mute',
    'cogs.settings',
]

if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)


bot.run(settings.TOKEN)