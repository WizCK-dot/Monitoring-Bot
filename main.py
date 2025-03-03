import asyncio
import os

from src.telegram_client import create_telegram_client, start_telegram_client
from src.discord_bot import create_discord_bot, start_discord_bot

async def main():
    """
    Main function to concurrently start the Telegram client and Discord bot.
    """
    telegram_client = create_telegram_client()
    await start_telegram_client(telegram_client)

    discord_bot = create_discord_bot()
    await asyncio.gather(
        telegram_client.run_until_disconnected(),
        start_discord_bot(discord_bot)
    )

if __name__ == "__main__":
    print("Script started...")
    asyncio.run(main())
