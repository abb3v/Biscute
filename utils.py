import discord

from database import get_debug_channel

async def notify_debug_channel(title, description, color, member: discord.Member):
    debug_channel_id = await get_debug_channel(member.guild.id)
    if debug_channel_id:
        debug_channel = member.guild.get_channel(debug_channel_id)
        if debug_channel:
            embed = discord.Embed(title=title, description=description, color=color)
            embed.add_field(name="Issuer", value=member.mention, inline=False)
            await debug_channel.send(embed=embed)

async def get_text_channel_select(ctx):
    select = discord.ui.Select(placeholder="Choose a channel...", min_values=1, max_values=1)
    for channel in ctx.guild.text_channels:
        select.add_option(label=channel.name, value=str(channel.id))
    return select

async def create_channel_selection_view(ctx, embed, callback):
    select = await get_text_channel_select(ctx)
    select.callback = callback
    view = discord.ui.View()
    view.add_item(select)
    return embed, view