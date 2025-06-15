#!/usr/bin/env python3
"""
Möbius AI Assistant - Production Startup Script
Starts the bot with all fixes and improvements
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mobius.log')
    ]
)

# Reduce noise from external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def main():
    """Main startup function"""
    try:
        logger.info("🚀 Starting Möbius AI Assistant...")
        
        # Import and run the main bot
        from main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Bot crashed: {e}")
        raise

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN", "GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please check your .env file")
        sys.exit(1)
    
    logger.info("✅ Environment variables loaded")
    
    # Run the bot
    asyncio.run(main())