import discord
from discord.ext import commands
from pycord.multicog import subcommand
from database import set_server_setup, get_debug_channel

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. Get a Select menu with available text channels
    async def _get_text_channel_select(self, ctx):
        select = discord.ui.Select(placeholder="Choose a channel...", min_values=1, max_values=1)
        for channel in ctx.guild.text_channels:
            select.add_option(label=channel.name, value=str(channel.id))
        return select

    # 2. Handle the selection of the debug channel
    async def _handle_debug_channel_selection(self, interaction, ctx):
        selected_channel_id = int(interaction.data['values'][0])
        await set_server_setup(ctx.guild.id, selected_channel_id)

        channel = ctx.guild.get_channel(selected_channel_id)
        debug_embed = discord.Embed(
            title="Debug Channel Set",
            description=f"The debug channel has been set to {channel.mention}.",
            color=discord.Color.blue()
        )
        await channel.send(embed=debug_embed)
        await interaction.response.edit_message(content=f"Selected channel: {channel.mention}", view=None)

    # 3. Create a View with a channel selection menu
    async def _create_channel_selection_view(self, ctx, embed, callback):
        select = await self._get_text_channel_select(ctx)
        select.callback = callback
        view = discord.ui.View()
        view.add_item(select)
        return embed, view

    # 4. The main setup process
    async def setup_server(self, ctx):
        embed = discord.Embed(
            title="Setup Required",
            description="""
                Thanks for using **Biscoito**.

                Before you can use this bot, you must accept our **[Licensing Agreement](https://github.com/Biscuit-Theme/biscuit/blob/main/LICENSE.md)** and proceed with the **Setup**.
            """,
            color=discord.Color.from_rgb(227, 156, 69)
        )

        async def setup_button_callback(interaction):
            if not interaction.user.guild_permissions.administrator:
                return await interaction.response.send_message("You must be an admin to press this button.", ephemeral=True)

            channel_embed = discord.Embed(
                title="Select a Debug Channel",
                description="This channel will be used for debug messages, etc.",
                color=discord.Color.gold()
            )

            callback = lambda i: self._handle_debug_channel_selection(i, ctx)
            channel_embed, select_view = await self._create_channel_selection_view(ctx, channel_embed, callback)
            await interaction.response.edit_message(embed=channel_embed, view=select_view)

        setup_button = discord.ui.Button(label="Setup", style=discord.ButtonStyle.primary)
        setup_button.callback = setup_button_callback

        discord_button = discord.ui.Button(label="Discord", style=discord.ButtonStyle.url, url="https://discord.gg/biscuit")

        view = discord.ui.View()
        view.add_item(setup_button)
        view.add_item(discord_button)

        await ctx.respond(embed=embed, view=view, ephemeral=True)

        # 5. Slash command to initiate the setup process
    @subcommand("settings")
    @commands.slash_command(name="setup", description="Run the settings procedure again")
    @commands.has_permissions(administrator=True)
    async def settings_setup(self, ctx):
        await self.setup_server(ctx)

    # 6. Error handling for missing permissions
    @settings_setup.error
    async def settings_setup_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.respond("You must be an admin to use this command.", ephemeral=True)

def setup(bot):
    bot.add_cog(Setup(bot))