import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from loguru import logger
from typing import Optional, List
import os

class TelegramAlertBot:
    """Async Telegram bot for dispatching security alerts with images."""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot: Optional[Bot] = None
        
        if token and chat_id:
            try:
                self.bot = Bot(token=token)
                logger.info("Telegram Bot initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram Bot: {e}")

    async def send_alert(self, 
                         message: str, 
                         image_path: Optional[str] = None, 
                         severity: str = "INFO"):
        """Sends a text message and optional image to the configured chat."""
        if not self.bot:
            logger.warning("Telegram Bot not configured. Skipping alert.")
            return

        formatted_msg = f"<b>[SafeWatch {severity}]</b>\n{message}"
        
        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo,
                        caption=formatted_msg,
                        parse_mode=ParseMode.HTML
                    )
            else:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=formatted_msg,
                    parse_mode=ParseMode.HTML
                )
            logger.info("Telegram alert sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    def dispatch_sync(self, message: str, image_path: Optional[str] = None, severity: str = "INFO"):
        """Helper to call async send_alert from synchronous code."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.send_alert(message, image_path, severity))
            else:
                loop.run_until_complete(self.send_alert(message, image_path, severity))
        except RuntimeError:
            # Fallback for threads without an event loop
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(self.send_alert(message, image_path, severity))
            new_loop.close()
