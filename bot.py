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
    surrounding it with ** to make it bold in Markdown (works for both Discord and Telegram).
    """
    pattern = r'(' + '|'.join(re.escape(word) for word in words) + r')'
    
    def bold_replacement(match):
        return f"**{match.group(1)}**"

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
        sender_id = sender.id if sender else 0
        sender_username = sender.username  # May be None if no username set
        print(f"Message sent by: {sender_name}, ID: {sender_id}, Username: {sender_username}")

        # Check if any of the target words are in the message (case-insensitive)
        if any(word.lower() in message_text.lower() for word in monitor_words):
            print("Target word found in the message.")
            
            # Highlight target words
            highlighted_text = highlight_words_in_text(message_text, monitor_words)

            ########################################
            # CREATE A "DISPLAY NAME" WITH LINK OR ID
            ########################################
            # If sender_username is not None, we can create a Telegram link to that user
            if sender_username:
                display_name = f"[{sender_name}](https://t.me/{sender_username})"
            else:
                # Fallback to numeric ID if there's no username
                display_name = f"{sender_name} (ID: {sender_id})"
            
            # Add a bit of structure to the final text
            final_text = f"**{display_name}** said:\n\n{highlighted_text}"
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
                
                # You can add the ID or a clickable link as part of the embed fields
                if sender_username:
                    # If the user has a username, you can store that link as a field
                    embed.add_field(
                        name="User",
                        value=f"[{sender_name}](https://t.me/{sender_username})",
                        inline=False
                    )
                else:
                    # Fallback: Show numeric ID
                    embed.add_field(
                        name="User",
                        value=f"{sender_name} (ID: {sender_id})",
                        inline=False
                    )

                # Optionally, add a footer or more info
                embed.set_footer(text="Reposted via Telethon & Discord.py")

                try:
                    if media:
                        # If it's an image, you could set it as embed image
                        # or just send as a file along with the embed
                        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            file = discord.File(media, filename=os.path.basename(media))
                            embed.set_image(url=f"attachment://{os.path.basename(media)}")
                            await channel.send(file=file, embed=embed)
                        else:
                            # If it's not an image, just attach it separately
                            await channel.send(content="Here's the reposted media:", file=discord.File(media))
                            # Then also send the embed
                            await channel.send(embed=embed)
                    else:
                        # No media, send just the embed
                        await channel.send(embed=embed)

                    print('Message sent to Discord successfully!')
                except Exception as e:
                    print(f'Failed to send message to Discord: {e}')
            else:
                print('Discord channel not found!')
            
            ####################################
            # SEND TO TELEGRAM
            ####################################
            tasks = []
            for post_channel in telegram_post_channels:
                try:
                    if media:
                        # Repost with media (image, doc, etc.) + caption in Markdown
                        tasks.append(
                            client.send_file(
                                post_channel,
                                file=media,
                                caption=final_text,
                                parse_mode='Markdown'
                            )
                        )
                        print(f"Task added to post message with media to Telegram channel {post_channel}")
                    else:
                        # Repost text-only message using Markdown
                        tasks.append(
                            client.send_message(
                                post_channel,
                                final_text,
                                parse_mode='Markdown'
                            )
                        )
                        print(f"Task added to post text-only message to Telegram channel {post_channel}")
                except Exception as e:
                    print(f"Failed to create post task for {post_channel}: {e}")
            
            # Execute all tasks concurrently
            if tasks:
                await asyncio.gather(*tasks)
                print("All Telegram repost tasks completed.")
            
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
            print('Bot is ready to send messages to Discord!')
        except Exception as e:
            print(f'Failed to send message: {e}')
    else:
        print('Channel not found!')

if __name__ == "__main__":
    print("Script started...")
    client.loop.run_until_complete(main())
