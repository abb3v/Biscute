import discord
from discord import SlashCommandGroup
from discord.ext.commands import Cog

from database import get_debug_channel

class Settings(Cog):
    def __init__(self, bot):
        self.bot = bot

    settings = SlashCommandGroup("settings", "Group of commands to manage settings")


def setup(bot):
    bot.add_cog(Settings(bot))