import asyncio
from telethon import TelegramClient, events
from src.handle_message import handle_message
from src.config import (
    api_id,
    api_hash,
    phone_number,
    monitored_channels
)

def create_telegram_client():
    """
    Creates and returns a Telegram client.
    """
    client = TelegramClient('session_name', api_id, api_hash)

    @client.on(events.NewMessage(chats=monitored_channels))
    async def new_message_handler(event):
        """
        Handles new messages from monitored channels.
        Reposts the message if it contains any of the target words.
        """
        await handle_message(event, client)

    return client

async def start_telegram_client(client):
    """
    Starts the Telegram client.
    """
    print("Starting Telegram client...")
    try:
        await client.start(phone=phone_number)
        print("Userbot is running and monitoring channels...")
    except Exception as e:
        print(f"Error starting Telegram client: {e}")
        raise e 