import logging
import os
from datetime import datetime
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def send_message(message: str, parse_mode: str = "Markdown") -> Optional[str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.debug("Telegram credentials not set; skipping alert.")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        logger.info("Sent Telegram alert (%d chars)", len(message))
        return response.text
    except Exception as exc:
        logger.exception("Failed to send Telegram alert: %s", exc)
        return None

