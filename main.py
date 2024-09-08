import toml
import os
import logging
from config import config, load_config

from discord.ext import commands
import discord
from pycord.multicog import Bot

from database import init_db, check_server_setup, create_pool

# Configure logging with timestamp and level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)
intents = discord.Intents.all()
bot = Bot(intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    await create_pool()
    await init_db()
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="over newcomers"
    ))

    logging.info(f'Logged in as {bot.user}')

    # Attempt to sync commands, log warning if unsuccessful
    try:
        await bot.sync_commands()
    except discord.errors.Forbidden:
        logging.warning("Failed to sync commands. Bot may lack necessary permissions.")

"""
This function loads Cogs from their respective folders.
The "Header", typically containing the SlashCommandGroup must be loaded first.
"""

def load_cogs():
    for root, dirs, files in os.walk('cogs'):
        subdir_name = os.path.basename(root)
        matching_cog = subdir_name + '.py'

        # Prioritize loading the matching cog if it exists
        if matching_cog in files:
            cog_path = os.path.join(root, matching_cog).replace('/', '.')[:-3]
            try:
                bot.load_extension(cog_path)
                logging.info(f"Loaded cog: {cog_path}")
            except Exception as e:
                logging.error(f"Failed to load cog {cog_path}: {e}")
            files.remove(matching_cog)  # Remove it so it's not loaded again later

        # Load the remaining cogs in the subdirectory
        for filename in files:
            if filename.endswith('.py') and not filename.startswith('_'):
                cog_path = os.path.join(root, filename).replace('/', '.')[:-3]
                try:
                    bot.load_extension(cog_path)
                    logging.info(f"Loaded cog: {cog_path}")
                except Exception as e:
                    logging.error(f"Failed to load cog {cog_path}: {e}")

load_cogs()

# Check if the server is set up; if not, trigger settings
async def check_setup(ctx):
    if not await check_server_setup(ctx.guild.id):
        setup_cog = bot.get_cog('Setup')
        if setup_cog:
            await setup_cog.setup_server(ctx)
        else:
            logging.error("Setup cog not found. Server settings cannot be completed.")
        return False
    return True

# Global check to ensure server settings before processing commands
@bot.check
async def globally_check(ctx):
    return await check_setup(ctx)

# Basic error handler for application command errors
@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        logging.error(f"An error occurred: {error}")
if __name__ == '__main__':
    try:
        if config['token'] == "env":
            token = os.getenv("TOKEN")
            logging.info(f"Token loaded from environment variable $TOKEN")
        else:
            token = config['token']
            logging.info(f"Token loaded from config file")
        bot.run(token)
    except discord.errors.LoginFailure:
        logging.critical("Invalid bot token. Check your config.toml.")
    except Exception as e:
        logging.critical(f"Fatal error occurred: {e}")