# Mavely Affiliate Link Generation and Posting Automation Bot

This is a Telegram bot that monitors specified channels, processes messages to convert specific links to Mavely format, and reposts the updated messages (with or without media) to other channels.

## Features

- Monitors multiple Telegram channels for new messages.
- Detects and converts specific URLs to a predefined format.
- Handles messages with or without media attachments.
- Reposts messages to multiple target channels.
- Ensures media files are deleted safely after processing.

## Requirements

- Python 3.8+
- A Telegram API ID and hash (get them from [my.telegram.org](https://my.telegram.org/)).
- The following libraries:
  - `telethon`
  - `aiofiles`
  - `tempfile`
  - `selenium`
  - `undetected-chromedriver`

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt

2. Run the script:

   ```bash
   python bot.py

## How It Works

   - Monitor Channels: The bot listens for new messages in the specified Telegram channels.
   - Process Links: It scans each message and updates specific links to a predefined format.
   - Handle Media: If a message contains media (e.g., images or videos), it processes them as well.
   - Repost: After processing, the bot sends the updated message to the target channels.
   - Clean Up: Any temporary media files used during processing are deleted to free up space.