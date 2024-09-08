from discord.ext import commands
import discord
from database import get_welcome_channel


class WelcomeListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome_channel_id = await get_welcome_channel(member.guild.id)
        if welcome_channel_id:
            channel = member.guild.get_channel(welcome_channel_id)
            if channel:
                await send_welcome_message(member, channel)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        welcome_channel_id = await get_welcome_channel(member.guild.id)
        if welcome_channel_id:
            channel = member.guild.get_channel(welcome_channel_id)
            if channel:
                await send_leave_message(member, channel)


async def send_welcome_message(member: discord.Member, channel):
    embed = discord.Embed(
        title="<a:welcome1:1279394516721471529><a:welcome2:1279394540079415317>",
        description=f"{member.mention} has joined the server!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Members Count", value=str(len(member.guild.members)), inline=True)
    embed.add_field(name="Account Creation Date", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.set_footer(text=member.guild.name, icon_url=member.guild.me.avatar.url)
    embed.set_image(url="https://github.com/Biscuit-Theme/biscuit/blob/main/assets/extras/rainbow%20line.png?raw=true")

    await channel.send(embed=embed)


async def send_leave_message(member: discord.Member, channel):
    embed = discord.Embed(
        title="Goodbye!",
        description=f"{member.mention} has left the server.",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Members Count", value=str(len(member.guild.members)), inline=True)
    embed.add_field(name="Account Creation Date", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.set_footer(text=member.guild.name, icon_url=member.guild.me.avatar.url)
    embed.set_image(url="https://github.com/Biscuit-Theme/biscuit/blob/main/assets/extras/rainbow%20line.png?raw=true")

    await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(WelcomeListener(bot))
