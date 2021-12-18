# settings.py
"""Contains setting commands"""

import discord
from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext import commands

import database
from resources import settings


class SettingsCog(commands.Cog):
    """Cog with setting commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    setting = SlashCommandGroup(
        "set",
        "Various settings",
    )

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
        await ctx.respond(answer)


# Initialization
def setup(bot):
    bot.add_cog(SettingsCog(bot))