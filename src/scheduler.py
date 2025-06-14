# src/scheduler.py
"""
Scheduler for Möbius AI Assistant
Handles automatic daily summaries and other scheduled tasks
"""
import logging
import asyncio
from datetime import datetime, time, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from config import config

logger = logging.getLogger(__name__)

class MobiusScheduler:
    """Scheduler for automated tasks"""
    
    def __init__(self, bot_application):
        self.scheduler = AsyncIOScheduler()
        self.bot_application = bot_application
        self.is_running = False
        
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Möbius scheduler started")
            
            # Schedule daily summary
            self._schedule_daily_summary()
            
            # Schedule weekly digest
            self._schedule_weekly_digest()
            
            # Schedule daily cleanup
            self._schedule_daily_cleanup()
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Möbius scheduler stopped")
    
    def _schedule_daily_summary(self):
        """Schedule automatic daily summaries"""
        summary_time = config.get('SUMMARY_TIME', '22:00')  # Default 10 PM
        timezone_str = config.get('TIMEZONE', 'UTC')
        
        try:
            # Parse time
            hour, minute = map(int, summary_time.split(':'))
            
            # Get timezone
            tz = pytz.timezone(timezone_str)
            
            # Schedule the job
            self.scheduler.add_job(
                self._send_daily_summary,
                CronTrigger(hour=hour, minute=minute, timezone=tz),
                id='daily_summary',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"Daily summary scheduled for {summary_time} {timezone_str}")
            
        except Exception as e:
            logger.error(f"Failed to schedule daily summary: {e}")
    
    def _schedule_weekly_digest(self):
        """Schedule weekly digest (Fridays at 6 PM)"""
        timezone_str = config.get('TIMEZONE', 'UTC')
        
        try:
            tz = pytz.timezone(timezone_str)
            
            self.scheduler.add_job(
                self._send_weekly_digest,
                CronTrigger(day_of_week='fri', hour=18, minute=0, timezone=tz),
                id='weekly_digest',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"Weekly digest scheduled for Fridays 18:00 {timezone_str}")
            
        except Exception as e:
            logger.error(f"Failed to schedule weekly digest: {e}")
    
    def _schedule_daily_cleanup(self):
        """Schedule daily cleanup (midnight)"""
        timezone_str = config.get('TIMEZONE', 'UTC')
        
        try:
            tz = pytz.timezone(timezone_str)
            
            self.scheduler.add_job(
                self._daily_cleanup,
                CronTrigger(hour=0, minute=0, timezone=tz),
                id='daily_cleanup',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"Daily cleanup scheduled for 00:00 {timezone_str}")
            
        except Exception as e:
            logger.error(f"Failed to schedule daily cleanup: {e}")
    
    async def _send_daily_summary(self):
        """Send automatic daily summary"""
        try:
            logger.info("Generating automatic daily summary...")
            
            # Get bot data
            bot_data = self.bot_application.bot_data
            message_store = bot_data.get('message_store', {})
            encryption_manager = bot_data.get('encryption_manager')
            
            if not message_store:
                logger.info("No messages to summarize today")
                return
            
            # Decrypt messages
            decrypted_messages = []
            for msg_id, msg_data in message_store.items():
                try:
                    decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                    decrypted_messages.append({
                        'user': msg_data['user'],
                        'text': decrypted_text,
                        'timestamp': msg_data['timestamp'],
                        'status': msg_data.get('status', 'new')
                    })
                except Exception as e:
                    logger.error(f"Failed to decrypt message {msg_id}: {e}")
            
            if not decrypted_messages:
                logger.info("No valid messages to summarize")
                return
            
            # Generate summary
            from summarizer import generate_daily_summary
            summary = await generate_daily_summary(decrypted_messages)
            
            if summary:
                # Send to target chat
                chat_id = int(config.get('TELEGRAM_CHAT_ID'))
                
                # Add automatic summary header
                auto_summary = f"🤖 **Automatic Daily Summary**\n\n{summary}\n\n"
                auto_summary += "_This summary was generated automatically. Use /summarynow for a fresh summary._"
                
                # Split long messages
                if len(auto_summary) > 4000:
                    parts = [auto_summary[i:i+4000] for i in range(0, len(auto_summary), 4000)]
                    for i, part in enumerate(parts):
                        await self.bot_application.bot.send_message(
                            chat_id=chat_id,
                            text=f"📝 **Daily Summary (Part {i+1}/{len(parts)})**\n\n{part}",
                            parse_mode='Markdown'
                        )
                else:
                    await self.bot_application.bot.send_message(
                        chat_id=chat_id,
                        text=auto_summary,
                        parse_mode='Markdown'
                    )
                
                # Store summary for weekly digest
                await self._store_daily_summary(summary)
                
                logger.info("Automatic daily summary sent successfully")
            else:
                logger.error("Failed to generate daily summary")
                
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
    
    async def _send_weekly_digest(self):
        """Send weekly digest"""
        try:
            logger.info("Generating weekly digest...")
            
            # Get stored daily summaries
            daily_summaries = await self._get_weekly_summaries()
            
            if not daily_summaries:
                logger.info("No daily summaries available for weekly digest")
                return
            
            # Generate weekly digest
            from summarizer import generate_weekly_digest
            digest = await generate_weekly_digest(daily_summaries)
            
            if digest:
                chat_id = int(config.get('TELEGRAM_CHAT_ID'))
                
                # Add automatic digest header
                auto_digest = f"🤖 **Automatic Weekly Digest**\n\n{digest}\n\n"
                auto_digest += "_This digest was generated automatically from daily summaries._"
                
                # Split long messages
                if len(auto_digest) > 4000:
                    parts = [auto_digest[i:i+4000] for i in range(0, len(auto_digest), 4000)]
                    for i, part in enumerate(parts):
                        await self.bot_application.bot.send_message(
                            chat_id=chat_id,
                            text=f"📊 **Weekly Digest (Part {i+1}/{len(parts)})**\n\n{part}",
                            parse_mode='Markdown'
                        )
                else:
                    await self.bot_application.bot.send_message(
                        chat_id=chat_id,
                        text=auto_digest,
                        parse_mode='Markdown'
                    )
                
                logger.info("Weekly digest sent successfully")
            else:
                logger.error("Failed to generate weekly digest")
                
        except Exception as e:
            logger.error(f"Error sending weekly digest: {e}")
    
    async def _daily_cleanup(self):
        """Perform daily cleanup"""
        try:
            logger.info("Performing daily cleanup...")
            
            # Clear message store
            bot_data = self.bot_application.bot_data
            if 'message_store' in bot_data:
                message_count = len(bot_data['message_store'])
                bot_data['message_store'].clear()
                logger.info(f"Cleared {message_count} messages from memory")
            
            # Clean up old summary files (keep last 30 days)
            await self._cleanup_old_summaries()
            
            logger.info("Daily cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during daily cleanup: {e}")
    
    async def _store_daily_summary(self, summary: str):
        """Store daily summary for weekly digest"""
        try:
            import os
            from datetime import datetime
            
            # Create summaries directory
            summaries_dir = "data/summaries"
            os.makedirs(summaries_dir, exist_ok=True)
            
            # Save summary with date
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f"{summaries_dir}/summary_{today}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            logger.info(f"Daily summary stored: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to store daily summary: {e}")
    
    async def _get_weekly_summaries(self) -> list:
        """Get daily summaries from the last 7 days"""
        try:
            import os
            from datetime import datetime, timedelta
            
            summaries = []
            summaries_dir = "data/summaries"
            
            if not os.path.exists(summaries_dir):
                return summaries
            
            # Get last 7 days
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                filename = f"{summaries_dir}/summary_{date_str}.txt"
                
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        summary = f.read()
                        summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get weekly summaries: {e}")
            return []
    
    async def _cleanup_old_summaries(self):
        """Clean up summaries older than 30 days"""
        try:
            import os
            from datetime import datetime, timedelta
            
            summaries_dir = "data/summaries"
            if not os.path.exists(summaries_dir):
                return
            
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for filename in os.listdir(summaries_dir):
                if filename.startswith('summary_') and filename.endswith('.txt'):
                    try:
                        # Extract date from filename
                        date_str = filename[8:18]  # summary_YYYY-MM-DD.txt
                        file_date = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        if file_date < cutoff_date:
                            file_path = os.path.join(summaries_dir, filename)
                            os.remove(file_path)
                            logger.info(f"Removed old summary: {filename}")
                            
                    except Exception as e:
                        logger.error(f"Error processing summary file {filename}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old summaries: {e}")
    
    def reschedule_daily_summary(self, new_time: str, timezone_str: str = None):
        """Reschedule daily summary with new time"""
        try:
            # Remove existing job
            if self.scheduler.get_job('daily_summary'):
                self.scheduler.remove_job('daily_summary')
            
            # Update config
            config.set('SUMMARY_TIME', new_time)
            if timezone_str:
                config.set('TIMEZONE', timezone_str)
            
            # Reschedule
            self._schedule_daily_summary()
            
            logger.info(f"Daily summary rescheduled to {new_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reschedule daily summary: {e}")
            return False

# Global scheduler instance
mobius_scheduler = None

def get_scheduler(bot_application=None):
    """Get or create scheduler instance"""
    global mobius_scheduler
    if mobius_scheduler is None and bot_application:
        mobius_scheduler = MobiusScheduler(bot_application)
    return mobius_scheduler