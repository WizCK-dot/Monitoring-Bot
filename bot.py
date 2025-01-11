import re
import asyncio
from telethon import TelegramClient, events
import os
import json
import discord
from discord.ext import commands

# Load settings from the JSON configuration file
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
discord_token = settings['discord_token']
discord_post_channels = settings['discord_post_channels']

intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

##########################################
# HELPER FUNCTION
##########################################

def highlight_words_in_text(text, words):
    """
    Highlights each monitored word in the given text (case-insensitive),
    surrounding it with ** to make it bold in Markdown (both Discord and Telegram).
    """
    # Create a pattern that matches any of the words regardless of case,
    # using word boundaries (\b) to avoid partial matches.
    pattern = r'(' + '|'.join(re.escape(word) for word in words) + r')'
    
    # This function will replace each found match with the bold version
    def bold_replacement(match):
        return f"**{match.group(1)}**"

    # Use re.IGNORECASE to do a case-insensitive search
    highlighted_text = re.sub(pattern, bold_replacement, text, flags=re.IGNORECASE)
    return highlighted_text

##########################################
# MESSAGE HANDLING
##########################################

async def handle_message(event, client):
    """
    Processes incoming messages to find specific words.
    If any target word is found, reposts the message with styling (Discord embed, Telegram Markdown).
    """
    try:
        print("Handling message...")
        
        # Get original text
        message_text = event.message.message or ""
        print(f"Original message text: {message_text}")
        
        # Get the sender's information
        sender = await event.get_sender()
        sender_name = sender.first_name if sender else "Unknown"
        print(f"Message sent by: {sender_name}")

        # Check if any of the target words are in the message (case-insensitive)
        if any(word.lower() in message_text.lower() for word in monitor_words):
            print("Target word found in the message.")
            
            # Highlight target words in bold
            highlighted_text = highlight_words_in_text(message_text, monitor_words)
            
            # Create a final text that includes the sender name
            final_text = f"**{sender_name}** said:\n\n{highlighted_text}"
            print(f"Styled message text: {final_text}")
            
            # Handle media if present
            media = None
            if event.message.media:
                print("Media detected, downloading...")
                media = await event.download_media()
                print(f"Media downloaded: {media}")

            ####################################
            # SEND TO DISCORD
            ####################################
            channel = bot.get_channel(discord_post_channels)
            if channel:
                # Create a Discord embed to make it "beautiful"
                embed = discord.Embed(
                    title="New Monitored Message",
                    description=highlighted_text,
                    color=discord.Color.blue()
                )
                embed.set_author(name=sender_name)
                
                # Optionally, add a footer or more info
                embed.set_footer(text="Reposted via @wizard")

                try:
                    if media:
                        # If you have an image, you could set it as embed thumbnail or image
                        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            file = discord.File(media, filename=os.path.basename(media))
                            embed.set_image(url=f"attachment://{os.path.basename(media)}")
                            await channel.send(file=file, embed=embed)
                        else:
                            # If it's not an image, just attach as a file
                            file = discord.File(media, filename=os.path.basename(media))
                            await channel.send(embed=embed, file=file)
                    else:
                        # Text-only embed
                        await channel.send(embed=embed)
                    
                    print('Message sent to Discord successfully!')
                except Exception as e:
                    print(f'Failed to send message to Discord: {e}')
            else:
                print('Discord channel not found!')
            
            ####################################
            # SEND TO TELEGRAM
            ####################################
            # Create tasks for posting messages to multiple Telegram channels
            tasks = []
            for post_channel in telegram_post_channels:
                try:
                    if media:
                        # Repost with media and styled text in Markdown
                        tasks.append(
                            client.send_file(
                                post_channel,
                                media,
                                caption=final_text,
                                parse_mode='markdown'
                            )
                        )
                        print(f"Task added to post message (with media) to {post_channel}")
                    else:
                        # Repost text-only message with Markdown
                        tasks.append(
                            client.send_message(
                                post_channel,
                                final_text,
                                parse_mode='markdown'
                            )
                        )
                        print(f"Task added to post text-only message to {post_channel}")
                except Exception as e:
                    print(f"Failed to create post task for {post_channel}: {e}")
            
            # Execute all tasks concurrently
            if tasks:
                await asyncio.gather(*tasks)
            
            # Cleanup temporary media file
            if media:
                os.remove(media)
                print(f"Deleted temporary media file: {media}")
        else:
            print("No target words found in the message, not reposting.")
    
    except Exception as e:
        print(f"Error in message handler: {e}")

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
    await handle_message(event, client)

async def main():
    """
    Main function to start the Telegram client.
    """
    print("Starting Telegram client...")
    try:
        await client.start(phone=phone_number)
        print("Userbot is running and monitoring channels...")
        print("Starting Discord bot...")
        try:
            await bot.start(discord_token)
        except Exception as e:
            print(f"Error starting Discord bot: {e}")
    except Exception as e:
        print(f"Error starting Telegram client: {e}")
        return

    await client.run_until_disconnected()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    post_channel = bot.get_channel(discord_post_channels)
    if post_channel:
        try:
            await post_channel.send('Hello, this is a message from the bot!')
            print('Message sent successfully!')
        except Exception as e:
            print(f'Failed to send message: {e}')
    else:
        print('Channel not found!')
    

if __name__ == "__main__":
    print("Script started...")
    client.loop.run_until_complete(main())
