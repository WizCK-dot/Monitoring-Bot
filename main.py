import asyncio
from telethon import TelegramClient, events
import os
import json
import discord
from discord.ext import commands
import logging
from src.handle_message import handle_message


logging.basicConfig(filename='messages.log', level=logging.INFO, format='%(asctime)s - %(message)s')

with open('settings.json', 'r') as file:
    settings = json.load(file)

##########################################
# USER CONFIGURATION
##########################################

api_id = settings['api_id']
api_hash = settings['api_hash']
phone_number = settings['phone_number']

monitored_channels = settings['monitored_channels']
telegram_post_channels = settings['telegram_post_channels']
monitor_words = settings.get('monitor_words', [])
block_keyword = settings.get('block_keyword', [])
discord_token = settings['discord_token']
discord_post_channels = settings['discord_post_channels']

intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

##########################################
# TELEGRAM CLIENT SETUP
##########################################

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(chats=monitored_channels))
async def new_message_handler(event):
    """
    Handles new messages from monitored channels.
    Reposts the message if it contains any of the target words.
    """
    await handle_message(event, client, bot)

async def main():
    """
    Main function to concurrently start the Telegram client and Discord bot.
    """
    print("Starting Telegram client...")
    try:
        await client.start(phone=phone_number)
        print("Userbot is running and monitoring channels...")
    except Exception as e:
        print(f"Error starting Telegram client: {e}")
        return

    print("Starting Discord bot...")
    try:
        await asyncio.gather(
            client.run_until_disconnected(),
            bot.start(discord_token)
        )
    except Exception as e:
        print(f"Error running Telegram or Discord tasks: {e}")

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

if __name__ == "__main__":
    print("Script started...")
    asyncio.run(main())
