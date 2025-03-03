import logging
import discord
from .utils import count_emoticons, highlight_words_in_text, cleanup_media, retry_async
import asyncio

class MessageHandler:
    def __init__(self, telegram_client, discord_client, config):
        self.telegram_client = telegram_client
        self.discord_client = discord_client
        self.config = config

    def format_message(self, sender_name, sender_id, sender_username, 
                      chat_title, message_link, message_text):
        display_name = (f"[{sender_name}](https://t.me/{sender_username})"
                       if sender_username else f"{sender_name} (ID: {sender_id})")
        
        highlighted_text = highlight_words_in_text(
            message_text, 
            self.config['monitor_words']
        )

        return (
            f"📢 **New Job post Found!** 📢\n\n"
            f"**Sender**: {display_name}\n"
            f"**Channel**: [{chat_title}]({message_link})\n\n"
            f"--------------------------------------\n\n"
            f"{highlighted_text}\n\n"
            f"--------------------------------------\n\n"
            f"🔗 [Click here to view the original message]({message_link})"
        )

    async def should_process_message(self, message_text):
        message_lower = message_text.lower()

        block_keywords = {kw.lower() for kw in self.config['block_keyword']}
        monitor_words = {mw.lower() for mw in self.config['monitor_words']}

        if (
            len(message_text) > 700
            or count_emoticons(message_text) > 8
            or any(kw in message_lower for kw in block_keywords)
        ):
            return False

        return any(mw in message_lower for mw in monitor_words)

    async def handle_message(self, event):
        try:
            message_text = event.message.message or ""
            logging.info(f"Message logged: {message_text}")

            if not await self.should_process_message(message_text):
                return

            sender = await event.get_sender()
            message_info = await self._get_message_info(event, sender)
            
            final_text = self.format_message(**message_info)
            
            media = await self._handle_media(event)
            
            await self._send_to_platforms(final_text, media)
            
            cleanup_media(media)

        except Exception as e:
            logging.error(f"Error in message handler: {e}", exc_info=True) 

    async def _get_message_info(self, event, sender):
        """Extract and return message information"""
        sender_name = sender.first_name if sender else "Unknown"
        sender_id = sender.id if sender else 0
        sender_username = sender.username

        message_id = event.message.id
        chat_id = event.chat_id
        chat_title = event.chat.title or "Unknown Chat"
        chat_username = event.chat.username

        message_link = (f"https://t.me/{chat_username}/{message_id}" 
                       if chat_username else 
                       f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")

        return {
            'sender_name': sender_name,
            'sender_id': sender_id,
            'sender_username': sender_username,
            'chat_title': chat_title,
            'message_link': message_link,
            'message_text': event.message.message or ""
        }

    async def _handle_media(self, event):
        """Download and handle media attachments"""
        if not event.message.media:
            return None
        
        try:
            return await event.download_media()
        except Exception as e:
            logging.error(f"Failed to download media: {e}")
            return None

    @retry_async(retries=3, delay=1)
    async def _send_to_discord(self, channel_id, final_text, media=None):
        """Send message to Discord with retry logic"""
        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            raise ValueError(f"Discord channel {channel_id} not found")

        embed = discord.Embed(
            title="A new post has been posted on Telegram",
            description=final_text,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Reposted via @Wizard")

        if media:
            if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file = discord.File(media, filename=media)
                embed.set_image(url=f"attachment://{media}")
                await channel.send(content="@here", file=file, embed=embed)
            else:
                await channel.send(content="Here's the reposted media:", 
                                 file=discord.File(media))
                await channel.send(embed=embed)
        else:
            await channel.send(content="@here", embed=embed)

    @retry_async(retries=3, delay=1)
    async def _send_to_telegram(self, channel, final_text, media=None):
        """Send message to Telegram with retry logic"""
        if media:
            await self.telegram_client.send_file(
                channel,
                file=media,
                caption=final_text,
                parse_mode='Markdown'
            )
        else:
            await self.telegram_client.send_message(
                channel,
                final_text,
                parse_mode='Markdown'
            )

    async def _send_to_platforms(self, final_text, media):
        """Send messages to both Discord and Telegram"""
        tasks = []

        tasks.append(self._send_to_discord(
            self.config['discord_post_channels'],
            final_text,
            media
        ))

        for channel in self.config['telegram_post_channels']:
            tasks.append(self._send_to_telegram(
                channel,
                final_text,
                media
            ))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Task {i} failed: {result}") 