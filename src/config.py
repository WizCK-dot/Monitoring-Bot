import json
import logging

logging.basicConfig(
    filename='messages.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

with open('settings.json', 'r') as file:
    settings = json.load(file)

api_id = settings['api_id']
api_hash = settings['api_hash']
phone_number = settings['phone_number']
monitored_channels = settings['monitored_channels']
telegram_post_channels = settings['telegram_post_channels']
monitor_words = settings.get('monitor_words', [])
block_keyword = settings.get('block_keyword', [])
discord_token = settings['discord_token']
discord_post_channels = settings['discord_post_channels'] 