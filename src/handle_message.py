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
        
        message_text = event.message.message or ""
        print(f"Original message text: {message_text}")
        logging.info(f"Message logged: {message_text}")
        
        if len(message_text) > 700 or count_emoticons(message_text) > 8:
            print("Message is too long or contains too many emoticons, ignoring.")
            return
        sender = await event.get_sender()
        sender_name = sender.first_name if sender else "Unknown"
        sender_id = sender.id if sender else 0
        sender_username = sender.username

        message_id = event.message.id
        chat_id = event.chat_id
        chat_title = event.chat.title or "Unknown Chat"

        chat_username = event.chat.username
        message_link = (f"https://t.me/{chat_username}/{message_id}" if chat_username
                        else f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")
        print(f"Message sent by: {sender_name}, ID: {sender_id}, Username: {sender_username}")

        if any(keyword.lower() in message_text.lower() for keyword in block_keyword):
            print("Blocked keyword detected. Message will not be reposted.")
            return

        if any(word.lower() in message_text.lower() for word in monitor_words):
            print("Target word found in the message.")
            
            highlighted_text = highlight_words_in_text(message_text, monitor_words)

            ########################################
            # CREATE A "DISPLAY NAME" WITH LINK OR ID
            ########################################
            if sender_username:
                display_name = f"[{sender_name}](https://t.me/{sender_username})"
            else:
                display_name = f"{sender_name} (ID: {sender_id})"

            highlighted_text = highlight_words_in_text(message_text, monitor_words)

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
                embed = discord.Embed(
                    title="A new post has been posted on Telegram",
                    description=final_text,
                    color=discord.Color.blue()
                )

                embed.set_footer(text="Reposted via @Wizard")

                try:
                    if media:
                        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            file = discord.File(media, filename=os.path.basename(media))
                            embed.set_image(url=f"attachment://{os.path.basename(media)}")
                            await channel.send(content="@here",file=file, embed=embed)
                        else:
                            await channel.send(content="Here's the reposted media:", file=discord.File(media))
                            await channel.send(embed=embed)
                    else:
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
            
            if tasks:
                await asyncio.gather(*tasks)
                print("All Telegram repost tasks completed.")
            
            if media:
                os.remove(media)
                print(f"Deleted temporary media file: {media}")
        else:
            print("No target words found in the message, not reposting.")
    
    except Exception as e:
        print(f"Error in message handler: {e}")
