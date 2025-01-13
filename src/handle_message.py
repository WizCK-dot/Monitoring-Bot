import re
import asyncio
import os
import json
import discord
import logging
from discord.ext import commands
from src.utils import count_emoticons, highlight_words_in_text

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
block_keyword = settings.get('block_keyword', [])

##########################################
# MESSAGE HANDLING
##########################################

async def handle_message(event, client, bot):
    """
    Processes incoming messages to find specific words.
    If any target word is found, reposts the message with styling (Discord embed, Telegram Markdown).
    """
    try:
        print("Handling message...")
        
        # Get original text
        message_text = event.message.message or ""
        print(f"Original message text: {message_text}")
        # Save the message in the log
        logging.info(f"Message logged: {message_text}")
        
        if len(message_text) > 700 or count_emoticons(message_text) > 8:
            print("Message is too long or contains too many emoticons, ignoring.")
            return  # Ignore the message
        # Get the sender's information
        sender = await event.get_sender()
        sender_name = sender.first_name if sender else "Unknown"
        sender_id = sender.id if sender else 0
        sender_username = sender.username  # May be None if no username set

        # Get message ID and chat details
        message_id = event.message.id
        chat_id = event.chat_id
        chat_title = event.chat.title or "Unknown Chat"

        # Determine the channel username for the message link
        chat_username = event.chat.username  # None for private chats
        message_link = (f"https://t.me/{chat_username}/{message_id}" if chat_username
                        else f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")
        print(f"Message sent by: {sender_name}, ID: {sender_id}, Username: {sender_username}")

        # Check if any words are in the block list
        if any(keyword.lower() in message_text.lower() for keyword in block_keyword):
            print("Blocked keyword detected. Message will not be reposted.")
            return

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

            # Highlight target words
            highlighted_text = highlight_words_in_text(message_text, monitor_words)

            # Add structure to the final text
            final_text = (
                f"📢 **New Job post Found!** 📢\n\n"
                f"**Sender**: {display_name}\n"
                f"**Channel**: [{chat_title}]({message_link})\n\n"
                f"--------------------------------------\n\n"
                f"{highlighted_text}\n\n"
                f"--------------------------------------\n\n"
                f"🔗 [Click here to view the original message]({message_link})"
            )

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
                    title="A new post has been posted on Telegram",
                    description=final_text,
                    color=discord.Color.blue()
                )

                # Optionally, add a footer or more info
                embed.set_footer(text="Reposted via @Wizard")

                try:
                    if media:
                        # If it's an image, you could set it as embed image
                        # or just send as a file along with the embed
                        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            file = discord.File(media, filename=os.path.basename(media))
                            embed.set_image(url=f"attachment://{os.path.basename(media)}")
                            await channel.send(content="@here",file=file, embed=embed)
                        else:
                            # If it's not an image, just attach it separately
                            await channel.send(content="Here's the reposted media:", file=discord.File(media))
                            # Then also send the embed
                            await channel.send(embed=embed)
                    else:
                        # No media, send just the embed
                        await channel.send(content="@here", embed=embed)

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
