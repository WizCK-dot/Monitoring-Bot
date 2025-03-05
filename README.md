# Telegram-Discord Monitoring Bot

A Python-based bot that monitors specified Telegram channels for messages containing certain keywords and reposts them to Discord channels. The bot can also handle messages with media attachments, highlighting target words in both platforms.

---

## Features

- Monitors messages from specific Telegram channels.
- Reposts messages containing target keywords to specified Discord channels.
- Highlights target words in the reposted messages.
- Handles media (images, documents, etc.) and reposts them appropriately.
- Configurable via a JSON settings file.

---

## Prerequisites

- Python 3.7+
- Telegram API credentials
- Discord bot token
- Installed Python libraries:
  - `telethon`
  - `discord.py`

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/WizCK-dot/telegram-discord-monitor.git
   cd telegram-discord-monitor
   ```

2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `settings.json` file in the project root directory with the following structure:

   ```json
   {
     "api_id": "your_telegram_api_id",
     "api_hash": "your_telegram_api_hash",
     "phone_number": "your_telegram_phone_number",
     "monitored_channels": ["channel1", "channel2"],
     "telegram_post_channels": ["channel3", "channel4"],
     "monitor_words": ["keyword1", "keyword2"],
     "discord_token": "your_discord_bot_token",
     "discord_post_channels": "your_discord_channel_id"
   }
   ```

   - Replace `your_telegram_api_id`, `your_telegram_api_hash`, and `your_telegram_phone_number` with your Telegram credentials.
   - Add the Telegram channels you want to monitor and post to.
   - Replace `your_discord_bot_token` with your Discord bot token and `your_discord_channel_id` with the target Discord channel ID.

4. Run the script:

   ```bash
   python bot.py
   ```

---

## Configuration

### `settings.json` File

| Key                  | Description                                            |
|----------------------|--------------------------------------------------------|
| `api_id`             | Telegram API ID (obtained from Telegram).             |
| `api_hash`           | Telegram API hash (obtained from Telegram).           |
| `phone_number`       | Your Telegram account's phone number.                 |
| `monitored_channels` | List of Telegram channels to monitor.                 |
| `telegram_post_channels` | List of Telegram channels to post messages to.        |
| `monitor_words`      | List of target keywords to monitor in messages.       |
| `discord_token`      | Token for your Discord bot.                           |
| `discord_post_channels` | ID of the Discord channel where messages are reposted. |

---

## How It Works

1. The bot monitors messages in the specified Telegram channels.
2. When a message contains one of the specified keywords:
   - It highlights the keywords.
   - It reposts the message to the configured Discord channel as an embed.
   - If media is attached, it reposts the media along with the message.
3. The bot handles any media (e.g., images, documents) and reposts them appropriately to both Telegram and Discord.

---

## Logging and Debugging

- The bot prints logs to the console for each monitored and reposted message.
- Errors are also logged to the console.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue if you have suggestions or find any bugs.

---

## Disclaimer

This bot is intended for educational purposes. Use responsibly and ensure compliance with the policies of Telegram and Discord.
