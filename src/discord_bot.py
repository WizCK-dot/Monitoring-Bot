import discord
from discord.ext import commands
from src.config import discord_token, discord_post_channels

intents = discord.Intents.default()
intents.guilds = True

def create_discord_bot():
    """
    Creates and configures the Discord bot.
    """
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        post_channel = bot.get_channel(discord_post_channels)
        if post_channel:
            try:
                print('Bot is ready to send messages to Discord!')
            except Exception as e:
                print(f'Failed to send message: {e}')
        else:
            print('Channel not found!')

    return bot

async def start_discord_bot(bot):
    """
    Starts the Discord bot.
    """
    print("Starting Discord bot...")
    try:
        await bot.start(discord_token)
    except Exception as e:
        print(f"Error running Discord bot: {e}")
        raise e 