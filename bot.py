# bot.py

import os
import discord
import sqlite3
import shutil
import asyncio
import global_data
import emojis
import logging
import logging.handlers

from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime
from discord.ext.commands import CommandNotFound

# Check if log file exists, if not, create empty one
log_dir = global_data.log_dir
logfile = global_data.logfile

if not os.path.exists(log_dir):
    os.mkdir(log_dir)
if not os.path.isfile(logfile):
    open(logfile, 'a').close()

# Initialize logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename=logfile,when='D',interval=1, encoding='utf-8', utc=True)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Read the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set name of database files
dbfile = global_data.dbfile

# Open connection to the local database
archmage_db = sqlite3.connect(dbfile, isolation_level=None)


# --- Database: Get Data ---

# Check database for stored prefix, if none is found, a record is inserted and the default prefix - is used, return all bot prefixes
async def get_prefix_all(bot, ctx):

    try:
        cur=archmage_db.cursor()
        cur.execute('SELECT * FROM settings_guild where guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()

        if record:
            prefixes = (record[1],'rpg ','Rpg ','rPg ','rpG ','RPg ','rPG ','RpG ','RPG ')
        else:
            cur.execute('INSERT INTO settings_guild VALUES (?, ?)', (ctx.guild.id, global_data.default_prefix,))
            prefixes = (global_data.default_prefix,'rpg ','Rpg ','rPg ','rpG ','RPg ','rPG ','RpG ','RPG ')
    except sqlite3.Error as error:
        await log_error(ctx, error)

    return commands.when_mentioned_or(*prefixes)(bot, ctx)

# Check database for stored prefix, if none is found, the default prefix - is used, return only the prefix (returning the default prefix this is pretty pointless as the first command invoke already inserts the record)
async def get_prefix(bot, ctx, guild_join=False):

    if guild_join == False:
        guild = ctx.guild
    else:
        guild = ctx

    try:
        cur=archmage_db.cursor()
        cur.execute('SELECT * FROM settings_guild where guild_id=?', (guild.id,))
        record = cur.fetchone()

        if record:
            prefix = record[1]
        else:
            prefix = global_data.default_prefix
    except sqlite3.Error as error:
        if guild_join == False:
            await log_error(ctx, error)
        else:
            await log_error(ctx, error, True)

    return prefix

# Get user count
async def get_user_number(ctx):

    try:
        cur=archmage_db.cursor()
        cur.execute('SELECT COUNT(*) FROM settings_user')
        record = cur.fetchone()

        if record:
            user_number = record
        else:
            await log_error(ctx, 'No user data found in database.')
    except sqlite3.Error as error:
        await log_error(ctx, error)

    return user_number

# Check database for user settings, if none is found, the default settings TT0 and not ascended are saved and used, return both
async def get_settings(ctx):

    try:
        cur=archmage_db.cursor()
        cur.execute('SELECT target_enchant FROM settings_user where user_id=?', (ctx.author.id,))
        record = cur.fetchone()

        if record:
            current_settings = record
        else:
            await set_enchant(ctx, 13) # Set enchant to "None", so this message doesn't trigger multiple times
            await first_time_user(bot, ctx)

    except sqlite3.Error as error:
        await log_error(ctx, error)

    return current_settings



# --- Database: Write Data ---

# Set new prefix
async def set_prefix(bot, ctx, new_prefix):

    try:
        cur=archmage_db.cursor()
        cur.execute('SELECT * FROM settings_guild where guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()

        if record:
            cur.execute('UPDATE settings_guild SET prefix = ? where guild_id = ?', (new_prefix, ctx.guild.id,))
        else:
            cur.execute('INSERT INTO settings_guild VALUES (?, ?)', (ctx.guild.id, new_prefix,))
    except sqlite3.Error as error:
        await log_error(ctx, error)

# Set enchant setting
async def set_enchant(ctx, enchant):

    try:
        cur=archmage_db.cursor()
        cur.execute('SELECT * FROM settings_user where user_id=?', (ctx.author.id,))
        record = cur.fetchone()

        if record:
            cur.execute('UPDATE settings_user SET target_enchant = ? where user_id = ?', (enchant, ctx.author.id,))
        else:
            cur.execute('INSERT INTO settings_user VALUES (?, ?)', (ctx.author.id, enchant,))
    except sqlite3.Error as error:
        await log_error(ctx, error)



# --- Error Logging ---

# Error logging
async def log_error(ctx, error, guild_join=False):

    if guild_join == False:
        try:
            settings = ''
            try:
                user_settings = await get_settings(ctx)
                settings = f'Enchant {user_settings[0]}'
            except:
                settings = 'N/A'
            cur=archmage_db.cursor()
            cur.execute('INSERT INTO errors VALUES (?, ?, ?, ?)', (ctx.message.created_at, ctx.message.content, str(error), settings))
        except sqlite3.Error as db_error:
            print(print(f'Error inserting error (ha) into database.\n{db_error}'))
    else:
        try:
            cur=archmage_db.cursor()
            cur.execute('INSERT INTO errors VALUES (?, ?, ?, ?)', (datetime.now(), 'Error when joining a new guild', str(error), 'N/A'))
        except sqlite3.Error as db_error:
            print(print(f'Error inserting error (ha) into database.\n{db_error}'))



# --- First Time User ---

# Welcome message to inform the user of his/her initial settings
async def first_time_user(bot, ctx):

    try:

        prefix = await get_prefix(bot, ctx)

        await ctx.send(
            f'Hey, **{ctx.author.name}**, I can help you with your enchanting if you like!\n'
            f'Use `{prefix}set [enchant]` to set the enchant you are going for and I will mute you once you reach the set enchant (or a higher one, of course).'
        )
    except:
        raise
    else:
        raise FirstTimeUser("First time user, pls ignore")



# --- Command Initialization ---

bot = commands.Bot(command_prefix=get_prefix_all, help_command=None, case_insensitive=True)

# Custom exception for first time users so they stop spamming my database
class FirstTimeUser(commands.CommandError):
        def __init__(self, argument):
            self.argument = argument



# --- Ready & Join Events ---

# Set bot status when ready
@bot.event
async def on_ready():

    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'your enchants'))

# Send message to system channel when joining a server
@bot.event
async def on_guild_join(guild):

    try:
        prefix = await get_prefix(bot, guild, True)

        welcome_message =   f'Hello **{guild.name}**! I\'m here to make sure you don\'t lose your precious enchants!\n\n'\
                            f'To set the enchant you want, use `{prefix}set [enchant]`.\n'\
                            f'If you don\'t like this prefix, use `{prefix}setprefix` to change it.\n\n'\
                            f'Tip: If you ever forget the prefix, simply ping me with a command.\n\n'\

        await guild.system_channel.send(welcome_message)
    except:
        return



# --- Error Handling ---

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    elif isinstance(error, (commands.MissingPermissions)):
        missing_perms = ''
        for missing_perm in error.missing_perms:
            missing_perm = missing_perm.replace('_',' ').title()
            if not missing_perms == '':
                missing_perms = f'{missing_perms}, `{missing_perm}`'
            else:
                missing_perms = f'`{missing_perm}`'
        await ctx.reply(f'Sorry **{ctx.author.name}**, you need the permission(s) {missing_perms} to use this command.', mention_author=False)
    elif isinstance(error, (commands.BotMissingPermissions)):
        missing_perms = ''
        for missing_perm in error.missing_perms:
            missing_perm = missing_perm.replace('_',' ').title()
            if not missing_perms == '':
                missing_perms = f'{missing_perms}, `{missing_perm}`'
            else:
                missing_perms = f'`{missing_perm}`'
        await ctx.send(f'Sorry **{ctx.author.name}**, I\'m missing the permission(s) {missing_perms} to work properly.')
    elif isinstance(error, (commands.NotOwner)):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'You\'re missing some arguments.', mention_author=False)
    elif isinstance(error, FirstTimeUser):
        return
    else:
        await log_error(ctx, error)



# --- Server Settings ---

# Command "setprefix" - Sets new prefix (if user has "manage server" permission)
@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.bot_has_permissions(send_messages=True)
async def setprefix(ctx, *new_prefix):

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        if new_prefix:
            if len(new_prefix)>1:
                await ctx.reply(f'The command syntax is `{ctx.prefix}setprefix [prefix]`.', mention_author=False)
            else:
                await set_prefix(bot, ctx, new_prefix[0])
                await ctx.reply(f'Prefix changed to `{await get_prefix(bot, ctx)}`.', mention_author=False)
        else:
            await ctx.reply(f'The command syntax is `{ctx.prefix}setprefix [prefix]`.', mention_author=False)

# Command "prefix" - Returns current prefix
@bot.command()
@commands.bot_has_permissions(send_messages=True)
async def prefix(ctx):

    if not ctx.prefix == 'rpg ':
        current_prefix = await get_prefix(bot, ctx)
        await ctx.reply(f'The prefix for this server is `{current_prefix}`\nTo change the prefix use `{current_prefix}setprefix [prefix]`.', mention_author=False)



# --- User Settings ---

# Command "settings" - Returns current user progress settings
@bot.command(aliases=('me',))
@commands.bot_has_permissions(send_messages=True, manage_roles=True)
async def settings(ctx):

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        current_settings = await get_settings(ctx)

        if current_settings:
            enchants = global_data.enchants_list
            enchant_setting = current_settings[0]
            enchant_setting = int(enchant_setting)
            enchant_name = enchants[enchant_setting]

            if not enchant_name == 'none':
                if enchant_setting > 7:
                    enchant_name = enchant_name.upper()
                else:
                    enchant_name = enchant_name.title()
                await ctx.reply(
                    f'**{ctx.author.name}**, your target enchant is set to **{enchant_name}**.\n'
                    f'Use `{ctx.prefix}set [enchant]` to change it.',
                    mention_author=False
                )
            else:
                await ctx.reply(
                    f'**{ctx.author.name}**, you don\'t have an enchant set.\n'
                    f'Use `{ctx.prefix}set [enchant]` to change it.',
                    mention_author=False
                )


# Command "setenchant" - Sets your target enchant
@bot.command(aliases=('se','set',))
@commands.bot_has_permissions(send_messages=True, manage_roles=True)
async def setenchant(ctx, *args):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        enchants = global_data.enchants_list
        aliases = global_data.enchants_aliases

        if args:
            target_enchant = ''
            original_args = ''
            for arg in args:
                target_enchant = f'{target_enchant}{arg}'
                if original_args == '':
                    original_args = arg
                else:
                    original_args = f'{original_args} {arg}'

            target_enchant = target_enchant.lower()

            if target_enchant in aliases:
                target_enchant = aliases[target_enchant]

            if target_enchant in enchants:
                enchant_index = enchants.index(target_enchant)
                if not target_enchant == 'none':
                    if enchant_index > 7:
                        target_enchant = target_enchant.upper()
                    else:
                        target_enchant = target_enchant.title()

                    await set_enchant(ctx, enchant_index)
                    await ctx.reply(f'Alright **{ctx.author.name}**, I\'ll mute you when you enchant your gear to **{target_enchant}** or higher.', mention_author=False)
                else:
                    await set_enchant(ctx, 13)
                    await ctx.reply(f'Alright **{ctx.author.name}**, you don\'t have a target enchant anymore.', mention_author=False)
                    return

            else:
                await ctx.reply(f'I don\'t know any enchant called `{original_args}`.', mention_author=False)
                return
        else:
            await ctx.reply(f'The command syntax is `{ctx.prefix}set [enchant]`.', mention_author=False)



# --- Enchant Mute ---
@bot.command(aliases=('refine','transmute','transcend',))
@commands.bot_has_permissions(send_messages=True, manage_roles=True)
async def enchant(ctx, *args):

    def epic_rpg_check(m):
        correct_embed = False
        try:
            ctx_author = str(ctx.author.name).encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
            embed_author = str(m.embeds[0].author).encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
            if (embed_author.find(f'{ctx_author}\'s enchant') > 1) or (embed_author.find(f'{ctx_author}\'s refine') > 1) or (embed_author.find(f'{ctx_author}\'s transmute') > 1) or (embed_author.find(f'{ctx_author}\'s transcend') > 1):
                correct_embed = True
            else:
                correct_embed = False
        except:
            correct_embed = False

        return m.author.id == 555955826880413696 and m.channel == ctx.channel and correct_embed

    invoked = ctx.invoked_with

    prefix = ctx.prefix
    if prefix.lower() == 'rpg 'and len(args) == 1:
        args = [arg.lower() for arg in args]
        arg = args[0]
        if (arg == 'armor') or (arg == 'sword') or (arg == 'test'):
            try:
                bot_enchant = await bot.wait_for('message', check=epic_rpg_check, timeout = 5)
                try:
                    answer = str(bot_enchant.embeds[0].fields[0])
                except:
                    return

                settings = await get_settings(ctx)
                target_enchant = settings[0]
                target_enchant = int(target_enchant)
                enchants = global_data.enchants_list
                enchant_name = enchants[target_enchant]

                if not enchant_name == 'none':
                    if target_enchant > 7:
                        target_enchant_name = enchant_name.upper()
                    else:
                        target_enchant_name = enchant_name.title()

                    current_enchant_start = answer.find('~-~>') + 7
                    current_enchant_end = answer.find('<~-~', current_enchant_start) - 3
                    current_enchant_name = answer[current_enchant_start:current_enchant_end]

                    current_enchant = enchants.index(current_enchant_name.lower())

                    if current_enchant >= target_enchant:
                        user = ctx.author
                        channel = ctx.channel
                        original_permissions = channel.overwrites_for(user)
                        if original_permissions.is_empty(): original_permissions = None

                        overwrite = discord.PermissionOverwrite()
                        overwrite.send_messages = False

                        await channel.set_permissions(user, overwrite=overwrite)
                        await ctx.send(f"{user.mention} Nice! Looks like you enchanted **{current_enchant_name}**. Because you set **{target_enchant_name}** as your target, you are now muted for 5 seconds.")
                        await asyncio.sleep(5)

                        await channel.set_permissions(user, overwrite=original_permissions)
                        await ctx.send(f"Carry on.")
            except asyncio.TimeoutError as error:
                return


# --- Ascended commmands ---
@bot.command()
@commands.bot_has_permissions(send_messages=True, manage_roles=True)
async def ascended(ctx, *args):

    prefix = ctx.prefix
    if prefix.lower() == 'rpg 'and len(args)>=2:
        args = [arg.lower() for arg in args]
        if args[0] in ('enchant','refine','transmute','transcend',):
            x = await enchant(ctx,args[1],)


# --- Main menus ---

# Main menu
@bot.command(aliases=('g','h',))
@commands.bot_has_permissions(send_messages=True, embed_links=True)
async def help(ctx):

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        prefix = await get_prefix(bot, ctx)

        user_settings = (
            f'{emojis.bp} `{prefix}settings` / `{prefix}me` : Check your target enchant\n'
            f'{emojis.bp} `{prefix}set` : Set your target enchant'
        )

        server_settings = (
            f'{emojis.bp} `{prefix}prefix` : Check the bot prefix\n'
            f'{emojis.bp} `{prefix}setprefix` / `{prefix}sp` : Set the bot prefix'
        )

        embed = discord.Embed(
            color = global_data.color,
            title = 'ARCHMAGE',
            description =   f'Well **{ctx.author.name}**, need to do some enchanting?'
        )
        embed.set_footer(text=await global_data.default_footer(prefix))
        embed.add_field(name='USER SETTINGS', value=user_settings, inline=False)
        embed.add_field(name='SERVER SETTINGS', value=server_settings, inline=False)

        await ctx.reply(embed=embed, mention_author=False)



# --- Miscellaneous ---

# Statistics command
@bot.command(aliases=('statistic','statistics,','devstat','ping','about','info','stats'))
@commands.bot_has_permissions(send_messages=True, embed_links=True)
async def devstats(ctx):
    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        """Shows some bot info"""
        user_number = await get_user_number(ctx)
        start_time = datetime.utcnow()
        message = await ctx.send('Testing API latency...')
        end_time = datetime.utcnow()
        elapsed_time = end_time - start_time
        bot_status = (
            f'{emojis.bp} {len(bot.guilds):,} servers\n'
            f'{emojis.bp} {user_number[0]:,} users\n'\
            f'{emojis.bp} Bot latency: {round(bot.latency*1000):,} ms\n'
            f'{emojis.bp} API latency: {round(elapsed_time.total_seconds()*1000):,} ms'
            )
        embed = discord.Embed(color = global_data.color, title = 'ABOUT ARCHMAGE')
        embed.add_field(name='BOT STATS', value=bot_status, inline=False)
        await message.edit(content=None, embed=embed)


# --- Owner Commands ---

# Shutdown command (only I can use it obviously)
@bot.command()
@commands.is_owner()
@commands.bot_has_permissions(send_messages=True)
async def shutdown(ctx):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        await ctx.reply(f'**{ctx.author.name}**, are you **SURE**? `[yes/no]`', mention_author=False)
        answer = await bot.wait_for('message', check=check, timeout=30)
        if answer.content.lower() in ['yes','y']:
            await ctx.send(f'Shutting down.')
            await ctx.bot.logout()
        else:
            await ctx.send(f'Phew, was afraid there for a second.')

bot.run(TOKEN)