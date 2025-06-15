# src/summarizer.py
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from config import config
from ai_providers import get_ai_response

logger = logging.getLogger(__name__)

def format_transcript(decrypted_messages: List[Dict]) -> str:
    """Format decrypted messages into a readable transcript"""
    if not decrypted_messages:
        return "No messages to format."
    
    transcript_parts = []
    for msg in sorted(decrypted_messages, key=lambda x: x.get('timestamp', 0)):
        timestamp = datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%H:%M')
        username = msg.get('username', 'Unknown')
        text = msg.get('text', '')
        
        # Handle different message types
        if msg.get('is_edit'):
            transcript_parts.append(f"[{timestamp}] {username} (edited): {text}")
        elif msg.get('is_deleted'):
            transcript_parts.append(f"[{timestamp}] {username} (deleted message)")
        else:
            transcript_parts.append(f"[{timestamp}] {username}: {text}")
    
    return "\n".join(transcript_parts)

async def generate_daily_summary(decrypted_messages: List[Dict], user_id: int = None) -> Optional[str]:
    """Generate daily summary using AI with background processing"""
    if not decrypted_messages:
        return "No conversations to summarize today."
    
    try:
        # Process in background - user doesn't see this
        logger.info("🤔 Analyzing conversation patterns and extracting key themes...")
        
        # Format the transcript
        transcript = format_transcript(decrypted_messages)
        
        if len(transcript.strip()) < 50:  # Very short conversations
            return "📝 **Daily Summary**\n\nConversation was too brief to generate meaningful insights."
        
        # Create comprehensive summary prompt
        summary_prompt = f"""
Analyze this Telegram conversation and create a comprehensive daily summary:

CONVERSATION TRANSCRIPT:
{transcript}

Please provide a structured summary with:

1. **Key Topics Discussed** - Main themes and subjects
2. **Important Decisions** - Any decisions made or planned
3. **Action Items** - Tasks or follow-ups mentioned
4. **Notable Insights** - Interesting observations or learnings
5. **Questions Raised** - Unanswered questions or concerns
6. **Sentiment Analysis** - Overall mood and tone

Format as a clean, professional summary suitable for a daily digest.
Use emojis sparingly and focus on actionable insights.
Keep it concise but comprehensive.
"""
        
        # Get AI response
        summary = await get_ai_response(summary_prompt, user_id)
        
        if summary:
            # Add header and timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            formatted_summary = f"📋 **Daily Summary** - {current_time}\n\n{summary}"
            
            logger.info("✅ Daily summary generated successfully")
            return formatted_summary
        else:
            logger.warning("❌ AI failed to generate summary")
            return "📝 **Daily Summary**\n\n❌ Unable to generate summary at this time."
            
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        return f"📝 **Daily Summary**\n\n❌ Error: {str(e)}"

async def generate_weekly_digest(message_store: Dict, user_id: int = None) -> str:
    """Generate a comprehensive weekly digest"""
    try:
        logger.info("📊 Generating weekly digest...")
        
        # Collect messages from the past week
        week_ago = datetime.now() - timedelta(days=7)
        week_messages = []
        
        for chat_id, messages in message_store.items():
            for msg in messages:
                if msg.get('timestamp', 0) > week_ago.timestamp():
                    week_messages.append(msg)
        
        if not week_messages:
            return "📊 **Weekly Digest**\n\nNo significant activity this week."
        
        # Sort by timestamp
        week_messages.sort(key=lambda x: x.get('timestamp', 0))
        
        # Create weekly analysis prompt
        transcript = format_transcript(week_messages)
        
        weekly_prompt = f"""
Analyze this week's Telegram conversations and create a comprehensive weekly digest:

WEEK'S CONVERSATIONS:
{transcript}

Please provide:

1. **Week Overview** - High-level summary of the week's discussions
2. **Key Achievements** - What was accomplished or decided
3. **Trending Topics** - Most discussed subjects
4. **Recurring Themes** - Patterns in conversations
5. **Outstanding Items** - Unresolved issues or pending tasks
6. **Weekly Insights** - Key learnings or observations
7. **Looking Ahead** - Implications for next week

Format as a professional weekly report.
Focus on trends, patterns, and actionable insights.
"""
        
        digest = await get_ai_response(weekly_prompt, user_id)
        
        if digest:
            week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            week_end = datetime.now().strftime("%Y-%m-%d")
            
            formatted_digest = f"📊 **Weekly Digest** ({week_start} to {week_end})\n\n{digest}"
            
            logger.info("✅ Weekly digest generated successfully")
            return formatted_digest
        else:
            return "📊 **Weekly Digest**\n\n❌ Unable to generate digest at this time."
            
    except Exception as e:
        logger.error(f"Failed to generate weekly digest: {e}")
        return f"📊 **Weekly Digest**\n\n❌ Error generating digest: {str(e)}"

async def generate_smart_summary(messages: List[Dict], summary_type: str = "daily", user_id: int = None) -> str:
    """Generate smart summaries based on type and context"""
    try:
        if not messages:
            return f"📝 **{summary_type.title()} Summary**\n\nNo conversations to analyze."
        
        # Determine summary approach based on type
        if summary_type == "daily":
            return await generate_daily_summary(messages, user_id)
        elif summary_type == "weekly":
            # For weekly, we need the full message store
            return "📊 **Weekly Summary**\n\nWeekly summaries require full conversation history."
        elif summary_type == "topic":
            return await generate_topic_summary(messages, user_id)
        elif summary_type == "action":
            return await generate_action_summary(messages, user_id)
        else:
            return await generate_daily_summary(messages, user_id)
            
    except Exception as e:
        logger.error(f"Error generating {summary_type} summary: {e}")
        return f"📝 **{summary_type.title()} Summary**\n\n❌ Error: {str(e)}"

async def generate_topic_summary(messages: List[Dict], user_id: int = None) -> str:
    """Generate topic-focused summary"""
    try:
        transcript = format_transcript(messages)
        
        topic_prompt = f"""
Analyze this conversation and identify the main topics discussed:

CONVERSATION:
{transcript}

Please provide:
1. **Main Topics** - List the 3-5 most discussed topics
2. **Topic Details** - Brief summary of each topic
3. **Key Points** - Important points made about each topic
4. **Conclusions** - Any conclusions or decisions reached

Focus on topical organization and thematic analysis.
"""
        
        summary = await get_ai_response(topic_prompt, user_id)
        
        if summary:
            return f"🎯 **Topic Summary**\n\n{summary}"
        else:
            return "🎯 **Topic Summary**\n\n❌ Unable to generate topic summary."
            
    except Exception as e:
        logger.error(f"Error generating topic summary: {e}")
        return f"🎯 **Topic Summary**\n\n❌ Error: {str(e)}"

async def generate_action_summary(messages: List[Dict], user_id: int = None) -> str:
    """Generate action-focused summary"""
    try:
        transcript = format_transcript(messages)
        
        action_prompt = f"""
Analyze this conversation and extract actionable items:

CONVERSATION:
{transcript}

Please identify:
1. **Action Items** - Specific tasks mentioned
2. **Decisions Made** - Concrete decisions reached
3. **Follow-ups Required** - Items needing follow-up
4. **Deadlines** - Any time-sensitive items
5. **Responsibilities** - Who is responsible for what

Focus on actionable outcomes and next steps.
"""
        
        summary = await get_ai_response(action_prompt, user_id)
        
        if summary:
            return f"✅ **Action Summary**\n\n{summary}"
        else:
            return "✅ **Action Summary**\n\n❌ Unable to generate action summary."
            
    except Exception as e:
        logger.error(f"Error generating action summary: {e}")
        return f"✅ **Action Summary**\n\n❌ Error: {str(e)}"

def get_summary_stats(messages: List[Dict]) -> Dict[str, Any]:
    """Get statistical information about the conversation"""
    try:
        if not messages:
            return {}
        
        # Basic stats
        total_messages = len(messages)
        unique_users = len(set(msg.get('username', 'Unknown') for msg in messages))
        
        # Time span
        timestamps = [msg.get('timestamp', 0) for msg in messages if msg.get('timestamp')]
        if timestamps:
            start_time = min(timestamps)
            end_time = max(timestamps)
            duration = end_time - start_time
        else:
            duration = 0
        
        # Message types
        edited_count = sum(1 for msg in messages if msg.get('is_edit'))
        deleted_count = sum(1 for msg in messages if msg.get('is_deleted'))
        
        # Word count
        total_words = sum(len(msg.get('text', '').split()) for msg in messages)
        
        return {
            'total_messages': total_messages,
            'unique_users': unique_users,
            'duration_hours': duration / 3600 if duration > 0 else 0,
            'edited_messages': edited_count,
            'deleted_messages': deleted_count,
            'total_words': total_words,
            'avg_words_per_message': total_words / total_messages if total_messages > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating summary stats: {e}")
        return {}

# Enhanced summarizer class for advanced functionality
class EnhancedSummarizer:
    """Enhanced summarizer with advanced features"""
    
    def __init__(self):
        self.cache = {}
        self.last_summary_time = {}
    
    async def generate_contextual_summary(self, messages: List[Dict], context: str = None, user_id: int = None) -> str:
        """Generate summary with additional context"""
        try:
            transcript = format_transcript(messages)
            
            context_prompt = f"""
Analyze this conversation with the following context:

CONTEXT: {context or "General conversation analysis"}

CONVERSATION:
{transcript}

Provide a summary that takes into account the given context.
Focus on how the conversation relates to the context provided.
"""
            
            summary = await get_ai_response(context_prompt, user_id)
            
            if summary:
                return f"📋 **Contextual Summary**\n\n{summary}"
            else:
                return "📋 **Contextual Summary**\n\n❌ Unable to generate contextual summary."
                
        except Exception as e:
            logger.error(f"Error generating contextual summary: {e}")
            return f"📋 **Contextual Summary**\n\n❌ Error: {str(e)}"
    
    async def generate_sentiment_analysis(self, messages: List[Dict], user_id: int = None) -> str:
        """Generate sentiment analysis of the conversation"""
        try:
            transcript = format_transcript(messages)
            
            sentiment_prompt = f"""
Analyze the sentiment and emotional tone of this conversation:

CONVERSATION:
{transcript}

Please provide:
1. **Overall Sentiment** - Positive, negative, or neutral
2. **Emotional Tone** - Dominant emotions present
3. **Sentiment Trends** - How sentiment changed over time
4. **Key Emotional Moments** - Significant emotional peaks
5. **Participant Moods** - Individual sentiment analysis

Focus on emotional intelligence and psychological insights.
"""
            
            analysis = await get_ai_response(sentiment_prompt, user_id)
            
            if analysis:
                return f"😊 **Sentiment Analysis**\n\n{analysis}"
            else:
                return "😊 **Sentiment Analysis**\n\n❌ Unable to generate sentiment analysis."
                
        except Exception as e:
            logger.error(f"Error generating sentiment analysis: {e}")
            return f"😊 **Sentiment Analysis**\n\n❌ Error: {str(e)}"

# Global enhanced summarizer instance
enhanced_summarizer = EnhancedSummarizer()