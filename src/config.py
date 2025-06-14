# src/config.py
import os
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
CONFIG_FILE = 'data/config.json'

class Config:
    def __init__(self):
        self._config = {
            'TELEGRAM_BOT_TOKEN': os.getenv("TELEGRAM_BOT_TOKEN", ""),
            'TELEGRAM_CHAT_ID': os.getenv("TELEGRAM_CHAT_ID", ""),
            'BOT_MASTER_ENCRYPTION_KEY': os.getenv("BOT_MASTER_ENCRYPTION_KEY", ""),
            'GROQ_API_KEY': os.getenv("GROQ_API_KEY", ""),
            'OPENAI_API_KEY': os.getenv("OPENAI_API_KEY", ""),
            'GEMINI_API_KEY': os.getenv("GEMINI_API_KEY", ""),
            'ANTHROPIC_API_KEY': os.getenv("ANTHROPIC_API_KEY", ""),
            'OPENROUTER_API_KEY': os.getenv("OPENROUTER_API_KEY", ""),
            'REQUESTY_API_KEY': os.getenv("REQUESTY_API_KEY", ""),
            'AI_PROVIDER': os.getenv("AI_PROVIDER", "groq"),
            'WHOP_API_KEY': os.getenv("WHOP_API_KEY", ""),
            'WHOP_BEARER_TOKEN': os.getenv("WHOP_BEARER_TOKEN", ""),
            'WHOP_PREMIUM_RETAIL_PLAN_ID': os.getenv("WHOP_PREMIUM_RETAIL_PLAN_ID", ""),
            'WHOP_PREMIUM_CORPORATE_PLAN_ID': os.getenv("WHOP_PREMIUM_CORPORATE_PLAN_ID", ""),
            'ARKHAM_WEBHOOK_URL': os.getenv("ARKHAM_WEBHOOK_URL", ""),
            'ETHEREUM_RPC_URL': os.getenv("ETHEREUM_RPC_URL", ""),
            'CRYPTO_API_KEYS': {
                'arkham': os.getenv("ARKHAM_API_KEY", ""),
                'nansen': os.getenv("NANSEN_API_KEY", "")
            },
            'TIMEZONE': "UTC",
            'SUMMARY_TIME': "23:00",
            'PAUSED': False
        }
        
        # Only check required variables if not in test mode
        if not os.getenv('MOBIUS_TEST_MODE'):
            required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'BOT_MASTER_ENCRYPTION_KEY']
            missing_vars = [var for var in required_vars if not self._config[var]]
            if missing_vars:
                logger.warning(f"Missing required environment variables: {missing_vars}")
                # Don't raise error in development, just warn
        
        self._load_persistent_config()

    def _load_persistent_config(self):
        """Load persistent configuration from file"""
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
            
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    persistent_config = json.load(f)
                    for key, value in persistent_config.items():
                        if isinstance(value, dict) and isinstance(self._config.get(key), dict):
                            self._config[key].update(value)
                        else:
                            self._config[key] = value
                    logger.info("Loaded config overrides from %s", CONFIG_FILE)
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            logger.info(f"Config file not found or is corrupt: {e}. Using defaults.")

    def save_persistent_config(self):
        """Save current configuration to file"""
        try:
            if not os.path.exists('data'):
                os.makedirs('data')
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info("Saved config to %s", CONFIG_FILE)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        try:
            # Handle null bytes and invalid keys
            if key is None:
                return default
            
            # Convert to string and remove null bytes
            if isinstance(key, str):
                key = key.replace('\x00', '')
            
            value = self._config.get(key, default)
            
            # Clean null bytes from string values
            if isinstance(value, str):
                value = value.replace('\x00', '')
            
            return value
        except Exception as e:
            logger.error(f"Error getting config key '{key}': {e}")
            return default

    def set(self, key, value):
        """Set configuration value"""
        self._config[key] = value

    def update(self, updates):
        """Update multiple configuration values"""
        self._config.update(updates)
    
    def get_env(self, key: str, default=None):
        """Get environment variable"""
        return os.getenv(key, default)
    
    def _mask_sensitive_value(self, value: str) -> str:
        """Mask sensitive values for logging"""
        if not value or len(value) < 8:
            return "***"
        return f"{value[:4]}***{value[-4:]}"

# Global config instance
config = Config()
