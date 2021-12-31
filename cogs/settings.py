# settings.py
"""Contains setting commands"""

import asyncio
import discord
from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext import commands

import database
from resources import emojis, settings


class SettingsCog(commands.Cog):
    """Cog with setting commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    setting = SlashCommandGroup(
        "set",
        "Various settings",
    )

    async def check_channel_permissions(self, ctx: discord.ApplicationContext) -> str:
        """Checks if Archmage has the proper permissions to do the enchant mute in this channel

        Returns
        -------
        List with all missing permissions: list(str)
        """
        channel_permissions = ctx.channel.permissions_for(ctx.guild.me)
        missing_perms = []
        if not channel_permissions.view_channel:
            missing_perms.append('View Channel')
        else:
            if not channel_permissions.send_messages:
                missing_perms.append('Send Messages')
            if not channel_permissions.manage_permissions:
                missing_perms.append('Manage Permissions')
            if not channel_permissions.add_reactions:
                missing_perms.append('Add Reactions')
        return missing_perms

    @slash_command(name='settings')
    async def settings_command(self, ctx: discord.ApplicationContext) -> None:
        """Shows the current settings"""
        try:
            user_settings: database.User = await database.get_user(ctx.author.id)
        except:
            await ctx.respond(
                'You are not registered with this bot yet. Please use `/set enchant` to set an enchant first.',
                ephemeral=True
            )
            return
        target_enchant = settings.ENCHANTS[user_settings.target_enchant]
        if user_settings.target_enchant == 13:
            answer = (
                f'**{ctx.author.name}**, you don\'t have a target enchant set.\n'
                f'Use `/set enchant` to set one.'
            )
        else:
            answer = (
                f'**{ctx.author.name}**, your target enchant is set to **{target_enchant}**.\n'
                f'Use `/set enchant` to change it.'
            )
        missing_perms = await self.check_channel_permissions(ctx)
        if missing_perms:
            answer = (
                f'{answer}\n\n'
                f'{emojis.WARNING} **Important**: I am not able to mute you in this channel because I lack the following permissions:'
            )
            for missing_perm in missing_perms:
                answer = f'{answer}\n{emojis.BP} {missing_perm}'
        await ctx.respond(answer)

    @setting.command(name='enchant')
    async def set_enchant(
        self,
        ctx: discord.ApplicationContext,
        enchant: Option(str, 'Enchant you are going for', choices=settings.ENCHANTS),
    ) -> None:
        """Sets the enchant you are going for. You will be muted if you get the selected or a higher enchant."""
        enchant_index = settings.ENCHANTS.index(enchant)
        await database.update_user(ctx.author.id, target_enchant=enchant_index)
        if enchant_index < 13:
            answer = (
                f'Alright **{ctx.author.name}**, '
                f'I\'ll mute you when you enchant your gear to **{enchant}** or higher.'
            )
        else:
            answer = f'Alright **{ctx.author.name}**, you don\'t have an enchant set anymore.'
        missing_perms = await self.check_channel_permissions(ctx)
        if missing_perms:
            answer = (
                f'{answer}\n\n'
                f'{emojis.WARNING} **Important**: I am not able to mute you in this channel because I lack the following permissions:'
            )
            for missing_perm in missing_perms:
                answer = f'{answer}\n{emojis.BP} {missing_perm}'
        await ctx.respond(answer)


# Initialization
def setup(bot):
    bot.add_cog(SettingsCog(bot))