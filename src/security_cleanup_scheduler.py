# src/security_cleanup_scheduler.py
"""
Security Cleanup Scheduler
Automatically deletes messages older than 24 hours and summaries older than 7 days
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime
from threading import Thread
from message_storage import message_storage

logger = logging.getLogger(__name__)

class SecurityCleanupScheduler:
    """Handles automatic security cleanup of stored messages and summaries"""
    
    def __init__(self):
        self.running = False
        self.cleanup_thread = None
        
    def start_scheduler(self):
        """Start the security cleanup scheduler"""
        if self.running:
            logger.warning("Security cleanup scheduler already running")
            return
            
        self.running = True
        
        # Schedule cleanup every hour
        schedule.every().hour.do(self._run_security_cleanup)
        
        # Schedule daily cleanup at 3 AM
        schedule.every().day.at("03:00").do(self._run_full_cleanup)
        
        # Start scheduler thread
        self.cleanup_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("🔒 Security cleanup scheduler started")
        logger.info("📅 Hourly cleanup: Every hour")
        logger.info("📅 Full cleanup: Daily at 3:00 AM")
    
    def stop_scheduler(self):
        """Stop the security cleanup scheduler"""
        self.running = False
        schedule.clear()
        logger.info("🔒 Security cleanup scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in security cleanup scheduler: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _run_security_cleanup(self):
        """Run security cleanup (messages older than 24 hours)"""
        try:
            logger.info("🔒 Running scheduled security cleanup...")
            message_storage.cleanup_old_messages(hours=24)
            logger.info("✅ Scheduled security cleanup completed")
        except Exception as e:
            logger.error(f"Error in scheduled security cleanup: {e}")
    
    def _run_full_cleanup(self):
        """Run full cleanup (messages + summaries)"""
        try:
            logger.info("🔒 Running scheduled full cleanup...")
            message_storage.auto_security_cleanup()
            logger.info("✅ Scheduled full cleanup completed")
        except Exception as e:
            logger.error(f"Error in scheduled full cleanup: {e}")
    
    def manual_cleanup(self):
        """Manually trigger security cleanup"""
        try:
            logger.info("🔒 Manual security cleanup triggered...")
            message_storage.auto_security_cleanup()
            logger.info("✅ Manual security cleanup completed")
            return True
        except Exception as e:
            logger.error(f"Error in manual security cleanup: {e}")
            return False

# Global instance
security_cleanup_scheduler = SecurityCleanupScheduler()