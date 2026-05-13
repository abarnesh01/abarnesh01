import asyncio
import os
from telegram import Bot
from telegram.request import HTTPXRequest
from loguru import logger
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class TelegramAlertBot:
    """
    Asynchronous Telegram bot for dispatching security alerts.
    Supports retries and snapshot uploads.
    """
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        
        if self.enabled:
            # High-performance request handler
            request = HTTPXRequest(connection_pool_size=8)
            self.bot = Bot(token=self.token, request=request)
            logger.info("Telegram Alert Bot initialized.")
        else:
            logger.warning("Telegram credentials missing. Alerts disabled.")

    async def send_text(self, message: str):
        """Sends a text-based alert."""
        if not self.enabled: return
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
            logger.success("Telegram text alert sent.")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def send_snapshot(self, photo_path: str, caption: str):
        """Sends a snapshot with a caption."""
        if not self.enabled: return
        
        if not os.path.exists(photo_path):
            logger.error(f"Snapshot path does not exist: {photo_path}")
            return

        try:
            with open(photo_path, 'rb') as photo:
                await self.bot.send_photo(
                    chat_id=self.chat_id, 
                    photo=photo, 
                    caption=caption,
                    parse_mode='Markdown'
                )
            logger.success(f"Telegram snapshot alert sent: {photo_path}")
        except Exception as e:
            logger.error(f"Failed to send Telegram snapshot: {e}")

    def dispatch_alert(self, message: str, snapshot_path: Optional[str] = None):
        """Non-blocking wrapper for async alert dispatch."""
        if not self.enabled: return
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            if snapshot_path:
                loop.create_task(self.send_snapshot(snapshot_path, message))
            else:
                loop.create_task(self.send_text(message))
        else:
            # For standalone testing
            if snapshot_path:
                asyncio.run(self.send_snapshot(snapshot_path, message))
            else:
                asyncio.run(self.send_text(message))
