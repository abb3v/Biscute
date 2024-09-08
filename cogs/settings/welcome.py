from discord import slash_command, Color, ApplicationContext
from discord.ext import commands
import discord

from pycord.multicog import subcommand
from database import set_welcome_channel, get_welcome_channel
from cogs.welcome.welcome import send_welcome_message
from utils import notify_debug_channel, create_channel_selection_view


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _handle_welcome_channel_selection(self, interaction, ctx: ApplicationContext):
        selected_channel_id = int(interaction.data['values'][0])
        channel = ctx.guild.get_channel(selected_channel_id)
        await set_welcome_channel(ctx.guild.id, selected_channel_id)

        prompt_embed = discord.Embed(
            title="Welcome Channel Set",
            description=f"The welcome channel has been set to {channel.mention}. Would you like to send a test message?",
            color=discord.Color.green()
        )

        test_button = discord.ui.Button(label="Send Test Message", style=discord.ButtonStyle.primary)
        no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.danger)

        async def test_callback(interaction):
            await send_welcome_message(interaction.user, channel)
            await interaction.response.edit_message(content="Test message sent.", embed=None, view=None)

        async def no_callback(interaction):
            await interaction.response.edit_message(content="Operation completed.", embed=None, view=None)

        test_button.callback = test_callback
        no_button.callback = no_callback

        test_view = discord.ui.View()
        test_view.add_item(test_button)
        test_view.add_item(no_button)

        await notify_debug_channel("Welcome Channel Changed", f"The welcome channel has been changed to {channel.mention}.", Color.orange(), ctx.user)

        await interaction.response.edit_message(embed=prompt_embed, view=test_view)

    @subcommand("settings")
    @slash_command(name="welcome", description="Set the welcome channel.")
    @commands.has_permissions(administrator=True)
    async def settings_welcome(self, ctx):
        welcome_channel_id = await get_welcome_channel(ctx.guild.id)
        if welcome_channel_id:
            welcome_channel = ctx.guild.get_channel(welcome_channel_id)
            embed = discord.Embed(
                title="Welcome Channel Already Set",
                description=f"The welcome channel is currently set to {welcome_channel.mention}. Would you like to change it?",
                color=discord.Color.blue()
            )

            change_button = discord.ui.Button(label="Change", style=discord.ButtonStyle.primary)
            cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)

            async def change_callback(interaction):
                if not interaction.user.guild_permissions.administrator:
                    return await interaction.response.edit_message(content="You must be an admin to press this button.",
                                                                   view=None)

                callback = lambda i: self._handle_welcome_channel_selection(i, ctx)
                updated_embed, select_view = await create_channel_selection_view(ctx, embed, callback)

                await interaction.response.edit_message(embed=updated_embed, view=select_view)

            async def cancel_callback(interaction):
                await interaction.response.edit_message(content="Operation cancelled.", embed=None, view=None)

            change_button.callback = change_callback
            cancel_button.callback = cancel_callback

            view = discord.ui.View()
            view.add_item(change_button)
            view.add_item(cancel_button)

            await ctx.respond(embed=embed, view=view, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Select Welcome Channel",
                description="Please select the channel where welcome messages should be sent.",
                color=discord.Color.blue()
            )

            callback = lambda i: self._handle_welcome_channel_selection(i, ctx)
            embed, view = await create_channel_selection_view(ctx, embed, callback)

            await ctx.respond(embed=embed, view=view, ephemeral=False)

def setup(bot):
    bot.add_cog(Welcome(bot))
