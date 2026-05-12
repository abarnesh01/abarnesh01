"""
SafeWatch — Telegram Bot
Async Telegram bot for sending threat alerts with python-telegram-bot v20+.
"""

import asyncio
import io
import os
import time
from datetime import datetime
from typing import Any, Optional

from loguru import logger

try:
    from telegram import Bot
    from telegram.error import TelegramError, RetryAfter, TimedOut
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed — Telegram alerts disabled")


class SafeWatchTelegramBot:
    """Async Telegram bot for SafeWatch alert dispatch."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._enabled = config.get("enabled", True) and TELEGRAM_AVAILABLE
        self._bot_token = os.environ.get(
            "TELEGRAM_BOT_TOKEN",
            config.get("bot_token", "").replace("${TELEGRAM_BOT_TOKEN}", ""),
        )
        self._agents: dict[str, dict[str, Any]] = {}
        self._max_retries = config.get("max_retries", 3)
        self._send_snapshot = config.get("send_snapshot", True)
        self._bot: Optional[Any] = None

        # Parse agent configs
        agents_cfg = config.get("agents", {})
        for agent_id, agent_data in agents_cfg.items():
            chat_id_raw = agent_data.get("chat_id", "")
            # Resolve env variables
            if chat_id_raw.startswith("${") and chat_id_raw.endswith("}"):
                env_key = chat_id_raw[2:-1]
                chat_id_raw = os.environ.get(env_key, "")
            self._agents[agent_id] = {
                "chat_id": chat_id_raw,
                "name": agent_data.get("name", agent_id),
                "cameras": agent_data.get("cameras", []),
            }

        if self._enabled and self._bot_token:
            try:
                self._bot = Bot(token=self._bot_token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self._enabled = False
        else:
            logger.warning("Telegram bot disabled (no token or not enabled)")

    def __repr__(self) -> str:
        status = "enabled" if self._enabled else "disabled"
        return f"SafeWatchTelegramBot(status={status}, agents={len(self._agents)})"

    def _get_agents_for_camera(self, camera_id: str) -> list[str]:
        """Get agent IDs that cover a specific camera."""
        matching = []
        for agent_id, agent_data in self._agents.items():
            if camera_id in agent_data.get("cameras", []):
                matching.append(agent_id)
        if not matching:
            matching = list(self._agents.keys())
        return matching

    async def send_threat_alert(
        self,
        threat_event: dict[str, Any],
        camera_id: str,
        camera_name: str,
        snapshot_bytes: Optional[bytes] = None,
        agent_id: Optional[str] = None,
    ) -> bool:
        """Send a threat alert to the appropriate Telegram agent(s)."""
        if not self._enabled or self._bot is None:
            logger.debug("Telegram disabled, skipping alert")
            return False

        agents_to_notify = [agent_id] if agent_id else self._get_agents_for_camera(camera_id)

        threat_type = threat_event.get("threat_type", "unknown").upper()
        confidence = threat_event.get("confidence", 0.0)
        severity = threat_event.get("severity", "MEDIUM")
        persons = threat_event.get("persons_involved", 0)
        description = threat_event.get("description", "")
        ts = threat_event.get("timestamp", time.time())
        dt_str = datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")

        message = (
            f"🚨 *SAFEWATCH ALERT*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Threat:* {threat_type}\n"
            f"📍 *Camera:* {camera_name} ({camera_id})\n"
            f"🕐 *Time:* {dt_str}\n"
            f"📊 *Confidence:* {confidence:.0%}\n"
            f"🔴 *Severity:* {severity}\n"
            f"👥 *Persons Involved:* {persons}\n"
            f"📝 *Details:* {description}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        success = False
        for aid in agents_to_notify:
            agent = self._agents.get(aid)
            if not agent or not agent.get("chat_id"):
                logger.warning(f"Agent {aid} has no chat_id configured")
                continue

            chat_id = agent["chat_id"]
            sent = await self._send_with_retry(chat_id, message, snapshot_bytes)
            if sent:
                success = True
                logger.info(f"Alert sent to agent {aid} ({agent['name']})")
            else:
                logger.error(f"Failed to send alert to agent {aid}")

        return success

    async def send_system_alert(
        self,
        message: str,
        all_agents: bool = True,
    ) -> bool:
        """Send a system-level alert to agents."""
        if not self._enabled or self._bot is None:
            return False

        formatted = f"ℹ️ *SafeWatch System*\n━━━━━━━━━━━━━━━━━━\n{message}"

        agents = list(self._agents.keys()) if all_agents else list(self._agents.keys())[:1]
        success = False

        for aid in agents:
            agent = self._agents.get(aid)
            if not agent or not agent.get("chat_id"):
                continue
            sent = await self._send_with_retry(agent["chat_id"], formatted, None)
            if sent:
                success = True

        return success

    async def send_daily_summary(
        self,
        stats: dict[str, Any],
        agent_id: Optional[str] = None,
    ) -> bool:
        """Send end-of-day summary report."""
        if not self._enabled or self._bot is None:
            return False

        total = stats.get("total_incidents", 0)
        by_type = stats.get("by_type", {})
        by_severity = stats.get("by_severity", {})
        date = stats.get("date", datetime.now().strftime("%Y-%m-%d"))

        type_lines = "\n".join(f"  • {t}: {c}" for t, c in by_type.items()) or "  None"
        sev_lines = "\n".join(f"  • {s}: {c}" for s, c in by_severity.items()) or "  None"

        message = (
            f"📊 *SafeWatch Daily Summary*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 *Date:* {date}\n"
            f"📈 *Total Incidents:* {total}\n\n"
            f"*By Type:*\n{type_lines}\n\n"
            f"*By Severity:*\n{sev_lines}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )

        agents = [agent_id] if agent_id else list(self._agents.keys())
        success = False

        for aid in agents:
            agent = self._agents.get(aid)
            if not agent or not agent.get("chat_id"):
                continue
            sent = await self._send_with_retry(agent["chat_id"], message, None)
            if sent:
                success = True

        return success

    async def _send_with_retry(
        self,
        chat_id: str,
        message: str,
        photo_bytes: Optional[bytes] = None,
    ) -> bool:
        """Send message with exponential backoff retry."""
        for attempt in range(self._max_retries):
            try:
                if photo_bytes and self._send_snapshot:
                    photo_io = io.BytesIO(photo_bytes)
                    photo_io.name = "alert.jpg"
                    await self._bot.send_photo(
                        chat_id=chat_id,
                        photo=photo_io,
                        caption=message,
                        parse_mode="Markdown",
                    )
                else:
                    await self._bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="Markdown",
                    )
                return True

            except RetryAfter as e:
                wait = e.retry_after
                logger.warning(f"Telegram rate limit, waiting {wait}s")
                await asyncio.sleep(wait)

            except TimedOut:
                wait = (attempt + 1) * 2
                logger.warning(f"Telegram timeout, retry {attempt + 1}/{self._max_retries} in {wait}s")
                await asyncio.sleep(wait)

            except TelegramError as e:
                logger.error(f"Telegram error: {e}")
                if attempt < self._max_retries - 1:
                    await asyncio.sleep((attempt + 1) * 2)
                else:
                    return False

            except Exception as e:
                logger.error(f"Unexpected error sending Telegram message: {e}")
                return False

        return False

    async def test_connection(self) -> bool:
        """Test bot token and connection."""
        if not self._enabled or self._bot is None:
            logger.warning("Telegram bot not enabled for testing")
            return False

        try:
            me = await self._bot.get_me()
            logger.info(f"Telegram bot connected: @{me.username} ({me.first_name})")
            return True
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False

    def run_async(self, coro):
        """Helper to run async methods from sync code."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(coro)
                return True
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
