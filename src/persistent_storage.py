# src/persistent_storage.py
import os
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)
SUMMARY_DIR = 'data/daily_summaries'

def save_summary(summary_text: str):
    """Saves the daily summary text to a date-stamped file."""
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    file_path = os.path.join(SUMMARY_DIR, f"{date.today().isoformat()}.txt")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        logger.info(f"Successfully saved daily summary to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save daily summary: {e}")

def get_summaries_for_week() -> list[str]:
    """Retrieves the last 7 days of summaries."""
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    summaries = []
    for i in range(7):
        file_path = os.path.join(SUMMARY_DIR, f"{(date.today() - timedelta(days=i)).isoformat()}.txt")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    summaries.append(f.read())
            except Exception as e:
                logger.warning(f"Could not read summary file {file_path}: {e}")
    logger.info(f"Retrieved {len(summaries)} summaries for the weekly digest.")
    return summaries