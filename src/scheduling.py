# src/scheduling.py
import logging
import re
from user_db import get_user_property, set_user_property, get_user_id_from_username

logger = logging.getLogger(__name__)

def set_calendly_for_user(user_id: int, calendly_link: str) -> str:
    """Validates and saves a user's Calendly link."""
    if "calendly.com/" not in calendly_link or not re.match(r'^https?://', calendly_link):
        return "Invalid format. Please provide your full Calendly link (e.g., `https://calendly.com/your-name`)."
    try:
        set_user_property(user_id, 'calendly_link', calendly_link)
        return "✅ Your Calendly link has been saved successfully!"
    except Exception as e:
        logger.error(f"Failed to save Calendly link for user {user_id}: {e}")
        return "An error occurred while saving your link."

def get_schedule_link_for_user(username: str) -> str:
    """Retrieves a user's Calendly link by their Telegram @username."""
    clean_username = username.lstrip('@')
    user_id = get_user_id_from_username(clean_username)
    if not user_id:
        return f"I don't have a record of the user @{clean_username}. They may need to send a message in this group first so I can see their ID."
    
    link = get_user_property(user_id, 'calendly_link')
    if not link:
        return f"User @{clean_username} has not set their Calendly link. They can set it by DMing me: `/set_calendly <link>`"
    
    return f"🗓️ Here is the scheduling link for @{clean_username}:\n{link}"