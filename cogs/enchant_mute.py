# main.py
"""Contains the enchant mute event"""

import asyncio
import re

import discord
from discord.ext import commands

import database
from resources import emojis, exceptions, settings


class EnchantMuteCog(commands.Cog):
    """Cog with events and help and about commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id == settings.EPIC_RPG_ID and message.embeds:
            try:
                message_author = (
                    str(message.embeds[0].author.name)
                    .encode('unicode-escape',errors='ignore')
                    .decode('ASCII').replace('\\','')
                )
                message_field = str(message.embeds[0].fields[0].name)
                icon_url = message.embeds[0].author.icon_url
            except:
                return
            enchant_actions = ['enchant', 'refine', 'transmute', 'transcend']
            enchants_lower = [enchant.lower() for enchant in settings.ENCHANTS]
            if (
                any(action in message_author.lower() for action in enchant_actions)
                and
                any(enchant in message_field.lower() for enchant in enchants_lower)
            ):
                user_id = user_name = user = None
                try:
                    user_id = int(re.search("avatars\/(.+?)\/", icon_url).group(1))
                except:
                    try:
                        user_name = re.search("^(.+?)'s", message_author).group(1)
                    except Exception as error:
                        await message.add_reaction(emojis.WARNING)
                        await database.log_error(error)
                        return
                try:
                    enchant = re.search('~-~> \*\*(.+?)\*\* <~-~', message_field).group(1)
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await database.log_error(error)
                    return
                if user_id is not None:
                    user = await message.guild.fetch_member(user_id)
                else:
                    for member in message.guild.members:
                        member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                        if member_name == user_name:
                            user = member
                            break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await database.log_error(f'User not determinable in enchant message: {message}')
                    return
                try:
                    user_settings: database.User = await database.get_user(user.id)
                except exceptions.NoDataFoundError:
                    await message.channel.send(
                        f'Hey, **{user.name}**, I can help you with your enchanting if you like!\n'
                        f'Use `/set enchant` to set the enchant you are going for and I will mute you once you reach '
                        f'the set enchant (or a higher one, of course).'
                    )
                    await database.update_user(user.id, target_enchant=settings.ENCHANTS.index('None'))
                    return
                enchant_index = enchants_lower.index(enchant.lower())
                if enchant_index >= user_settings.target_enchant:
                    target_enchant_name = settings.ENCHANTS[user_settings.target_enchant]
                    channel = message.channel
                    channel_was_synced = channel.permissions_synced
                    original_permissions = channel.overwrites_for(user)
                    if original_permissions.is_empty(): original_permissions = None
                    overwrite = discord.PermissionOverwrite(send_messages=False)
                    try:
                        await channel.set_permissions(user, overwrite=overwrite)
                        await channel.send(
                            f'{user.mention} Nice! Looks like you enchanted **{enchant}**.\n'
                            f'Because you set **{target_enchant_name}** as your target, you are now muted for 5 seconds.'
                        )
                        await asyncio.sleep(5)
                        if channel_was_synced:
                            await channel.edit(sync_permissions=True)
                        else:
                            await channel.set_permissions(user, overwrite=original_permissions)
                        await channel.send("Carry on.")
                    except:
                        await channel.send(
                            f'{emojis.WARNING} Whoops, looks like I\'m lacking the permission to change channel permissions.\n'
                            f'Please check my permissions in this channel.'
                        )


# Initialization
def setup(bot):
    bot.add_cog(EnchantMuteCog(bot))