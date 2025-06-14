#!/usr/bin/env python3
"""
IMPROVED SUMMARIZER
==================
Enhanced summarizer with processing time estimates and DM delivery.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class ImprovedSummarizer:
    """Enhanced summarizer with better user experience"""
    
    def __init__(self):
        self.processing_times = {}
        self.summary_cache = {}
    
    async def generate_summary_with_eta(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                      messages: List[Dict], summary_type: str = "daily") -> str:
        """Generate summary with processing time estimation"""
        start_time = time.time()
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Estimate processing time based on message count
        message_count = len(messages)
        estimated_time = self.estimate_processing_time(message_count)
        
        # Send initial processing message
        processing_msg = await update.message.reply_text(
            f"🔄 **Generating {summary_type} summary...**\n\n"
            f"📊 Processing {message_count} messages\n"
            f"⏱️ Estimated time: {estimated_time} seconds\n"
            f"📱 Summary will be sent to your DM"
        )
        
        try:
            # Generate the actual summary
            summary = await self.generate_summary(messages, summary_type)
            
            # Calculate actual processing time
            actual_time = time.time() - start_time
            self.update_processing_time_stats(message_count, actual_time)
            
            # Send summary to user's DM
            await self.send_summary_to_dm(context, user_id, summary, summary_type, actual_time)
            
            # Update processing message
            await processing_msg.edit_text(
                f"✅ **Summary Complete!**\n\n"
                f"📊 Processed {message_count} messages\n"
                f"⏱️ Processing time: {actual_time:.1f} seconds\n"
                f"📱 Summary sent to your DM"
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            await processing_msg.edit_text(
                f"❌ **Summary Failed**\n\n"
                f"Error: {str(e)}\n"
                f"Please try again or contact support."
            )
            raise
    
    def estimate_processing_time(self, message_count: int) -> int:
        """Estimate processing time based on message count and historical data"""
        # Base time calculation
        base_time = max(5, message_count * 0.1)  # Minimum 5 seconds
        
        # Adjust based on historical data
        if hasattr(self, 'avg_processing_time'):
            base_time = max(base_time, self.avg_processing_time)
        
        return int(base_time)
    
    def update_processing_time_stats(self, message_count: int, actual_time: float):
        """Update processing time statistics for better estimates"""
        if not hasattr(self, 'processing_history'):
            self.processing_history = []
        
        self.processing_history.append({
            'message_count': message_count,
            'processing_time': actual_time,
            'timestamp': datetime.now()
        })
        
        # Keep only last 50 entries
        if len(self.processing_history) > 50:
            self.processing_history = self.processing_history[-50:]
        
        # Calculate average processing time
        if self.processing_history:
            self.avg_processing_time = sum(h['processing_time'] for h in self.processing_history) / len(self.processing_history)
    
    async def send_summary_to_dm(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, 
                               summary: str, summary_type: str, processing_time: float):
        """Send summary to user's DM"""
        try:
            # Clean summary to remove any <think> tags or processing artifacts
            clean_summary = self.clean_summary_output(summary)
            
            # Format the final summary message
            dm_message = (
                f"📊 **{summary_type.title()} Summary**\n\n"
                f"{clean_summary}\n\n"
                f"⏱️ Generated in {processing_time:.1f} seconds\n"
                f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=dm_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error sending summary to DM: {e}")
            # Fallback: try to send without markdown
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Summary:\n\n{self.clean_summary_output(summary)}"
                )
            except Exception as e2:
                logger.error(f"Failed to send summary even without markdown: {e2}")
                raise
    
    def clean_summary_output(self, summary: str) -> str:
        """Clean summary output by removing processing artifacts"""
        # Remove <think> tags and their content
        import re
        
        # Remove <think>...</think> blocks
        summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL)
        
        # Remove any remaining processing indicators
        summary = re.sub(r'(Processing\.\.\.|Analyzing\.\.\.|Thinking\.\.\.)', '', summary)
        
        # Clean up extra whitespace
        summary = re.sub(r'\n\s*\n\s*\n', '\n\n', summary)
        summary = summary.strip()
        
        return summary
    
    async def generate_summary(self, messages: List[Dict], summary_type: str) -> str:
        """Generate the actual summary using AI"""
        try:
            # Import AI provider here to avoid circular imports
            from ai_providers_enhanced import ai_manager
            
            # Prepare messages for summarization
            message_text = self.prepare_messages_for_summary(messages)
            
            # Create summary prompt
            prompt = self.create_summary_prompt(message_text, summary_type)
            
            # Generate summary using AI
            summary = await ai_manager.query_with_fallback(prompt, user_id=0)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in AI summary generation: {e}")
            # Fallback to basic summary
            return self.generate_basic_summary(messages, summary_type)
    
    def prepare_messages_for_summary(self, messages: List[Dict]) -> str:
        """Prepare messages for summarization"""
        formatted_messages = []
        
        for msg in messages[-100:]:  # Limit to last 100 messages
            timestamp = msg.get('timestamp', 'Unknown time')
            username = msg.get('username', 'Unknown user')
            text = msg.get('text', '')
            
            if text and len(text.strip()) > 0:
                formatted_messages.append(f"{timestamp} {username}: {text}")
        
        return '\n'.join(formatted_messages)
    
    def create_summary_prompt(self, message_text: str, summary_type: str) -> str:
        """Create prompt for AI summarization"""
        return f"""
Please create a comprehensive {summary_type} summary of the following group chat conversation. 

Structure your response exactly as follows:

📊 Summary

Main Topics Discussed:
- [List the main topics that were discussed]

Key Participants:
- [List the most active participants]

Important Decisions:
- [List any decisions made or conclusions reached]

Questions & Answers:
- [Summarize any Q&A that occurred]

Notable Events:
- [Any significant events, announcements, or developments]

Conversation transcript:
{message_text}

Keep the summary concise, professional, and easy to read. Use bullet points and clear sections. Do not include any analysis steps or thinking process in your response.
"""
    
    def generate_basic_summary(self, messages: List[Dict], summary_type: str) -> str:
        """Generate basic summary without AI as fallback"""
        if not messages:
            return f"No messages found for {summary_type} summary."
        
        # Basic statistics
        total_messages = len(messages)
        unique_users = len(set(msg.get('username', 'Unknown') for msg in messages))
        
        # Most active users
        user_counts = {}
        for msg in messages:
            username = msg.get('username', 'Unknown')
            user_counts[username] = user_counts.get(username, 0) + 1
        
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        summary = f"""📊 {summary_type.title()} Summary

Main Topics Discussed:
- General conversation and discussion

Key Participants:
{chr(10).join(f"- {user} ({count} messages)" for user, count in top_users)}

Important Decisions:
- None noted in basic summary

Questions & Answers:
- Various discussions occurred

Notable Events:
- {total_messages} total messages from {unique_users} participants

📈 Activity: {total_messages} messages from {unique_users} unique users"""
        
        return summary

# Global instance
improved_summarizer = ImprovedSummarizer()

async def generate_improved_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  messages: List[Dict], summary_type: str = "daily") -> str:
    """Main function to generate improved summary"""
    return await improved_summarizer.generate_summary_with_eta(update, context, messages, summary_type)