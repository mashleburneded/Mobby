# src/enhanced_summarizer.py
"""
Enhanced Summarizer with Token Limit Handling and Pagination
Handles large message volumes without hitting LLM token limits
"""

import logging
import asyncio
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from config import config
from ai_providers import get_ai_response

logger = logging.getLogger(__name__)

@dataclass
class SummaryPage:
    page_number: int
    total_pages: int
    content: str
    message_count: int
    time_range: str

class EnhancedSummarizer:
    """Enhanced summarizer with token limit handling and pagination"""
    
    def __init__(self, max_tokens_per_request: int = 100000):  # Leave buffer for 125k limit
        self.max_tokens_per_request = max_tokens_per_request
        self.estimated_tokens_per_message = 50  # Conservative estimate
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    def chunk_messages(self, messages: List[Dict], max_tokens: int) -> List[List[Dict]]:
        """Split messages into chunks that fit within token limits"""
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        # Reserve tokens for prompt and response
        available_tokens = max_tokens - 2000  # Reserve 2k tokens for prompt/response
        
        for message in messages:
            message_text = message.get('text', '')
            message_tokens = self.estimate_tokens(message_text)
            
            # If adding this message would exceed limit, start new chunk
            if current_tokens + message_tokens > available_tokens and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [message]
                current_tokens = message_tokens
            else:
                current_chunk.append(message)
                current_tokens += message_tokens
        
        # Add the last chunk if it has messages
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def format_transcript(self, messages: List[Dict]) -> str:
        """Format messages into a readable transcript"""
        if not messages:
            return "No messages to format."
        
        transcript_parts = []
        for msg in sorted(messages, key=lambda x: x.get('timestamp', 0)):
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
    
    def get_time_range(self, messages: List[Dict]) -> str:
        """Get time range for a chunk of messages"""
        if not messages:
            return "No time range"
        
        timestamps = [msg.get('timestamp', 0) for msg in messages if msg.get('timestamp')]
        if not timestamps:
            return "Unknown time range"
        
        start_time = datetime.fromtimestamp(min(timestamps))
        end_time = datetime.fromtimestamp(max(timestamps))
        
        if start_time.date() == end_time.date():
            return f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}"
        else:
            return f"{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"
    
    async def generate_chunk_summary(self, messages: List[Dict], chunk_number: int, total_chunks: int) -> str:
        """Generate summary for a single chunk of messages"""
        if not messages:
            return "No messages in this chunk."
        
        try:
            transcript = self.format_transcript(messages)
            time_range = self.get_time_range(messages)
            
            # Create focused prompt for chunk summarization
            prompt = f"""
You are creating a concise summary of a chat conversation chunk.

**Chunk {chunk_number} of {total_chunks}**
**Time Range:** {time_range}
**Messages:** {len(messages)}

Analyze this conversation chunk and provide a structured summary:

**Key Topics:** Main discussion points
**Participants:** Active users in this timeframe  
**Important Points:** Significant information or decisions
**Questions:** Any important questions raised

Keep it concise and focus on the most important information. Use bullet points for clarity.

**Conversation Transcript:**
{transcript}

Provide only the final summary without any meta-commentary, analysis steps, or thinking process. Do not include phrases like "thinking about", "analyzing", or "processing".
"""
            
            # Process in background
            logger.info(f"🧠 Processing chunk {chunk_number}/{total_chunks} ({len(messages)} messages)")
            
            # Get AI response
            response = await get_ai_response(prompt)
            
            if response and isinstance(response, dict) and response.get('success'):
                return response.get('message', f"Summary for chunk {chunk_number} completed.")
            elif isinstance(response, str):
                return response
            else:
                return f"**Chunk {chunk_number} Summary**\n\nProcessed {len(messages)} messages from {time_range}.\nSummary generation encountered an issue."
        
        except Exception as e:
            logger.error(f"Error generating chunk summary: {e}")
            return f"**Chunk {chunk_number} Summary**\n\nError processing {len(messages)} messages from {time_range}."
    
    async def generate_paginated_summary(self, messages: List[Dict]) -> List[SummaryPage]:
        """Generate paginated summaries for large message volumes"""
        if not messages:
            return [SummaryPage(1, 1, "No conversations to summarize.", 0, "No time range")]
        
        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', 0))
        
        # Check if we need to paginate
        total_tokens = sum(self.estimate_tokens(msg.get('text', '')) for msg in sorted_messages)
        
        if total_tokens <= self.max_tokens_per_request:
            # Single page summary
            logger.info(f"📊 Generating single summary for {len(sorted_messages)} messages")
            summary_content = await self.generate_single_summary(sorted_messages)
            time_range = self.get_time_range(sorted_messages)
            
            return [SummaryPage(1, 1, summary_content, len(sorted_messages), time_range)]
        
        # Multi-page summary needed
        logger.info(f"📚 Large conversation detected ({total_tokens} tokens). Creating paginated summary...")
        
        # Split into chunks
        chunks = self.chunk_messages(sorted_messages, self.max_tokens_per_request)
        total_pages = len(chunks)
        
        logger.info(f"📄 Creating {total_pages} summary pages")
        
        # Generate summaries for each chunk
        summary_pages = []
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"📝 Processing page {i}/{total_pages}...")
            
            chunk_summary = await self.generate_chunk_summary(chunk, i, total_pages)
            time_range = self.get_time_range(chunk)
            
            summary_page = SummaryPage(
                page_number=i,
                total_pages=total_pages,
                content=chunk_summary,
                message_count=len(chunk),
                time_range=time_range
            )
            
            summary_pages.append(summary_page)
        
        # Generate overview page if multiple pages
        if total_pages > 1:
            overview_content = await self.generate_overview_summary(summary_pages, sorted_messages)
            overview_page = SummaryPage(
                page_number=0,  # Overview page
                total_pages=total_pages,
                content=overview_content,
                message_count=len(sorted_messages),
                time_range=self.get_time_range(sorted_messages)
            )
            summary_pages.insert(0, overview_page)
        
        return summary_pages
    
    async def generate_single_summary(self, messages: List[Dict]) -> str:
        """Generate a single comprehensive summary"""
        transcript = self.format_transcript(messages)
        
        prompt = f"""
You are creating a comprehensive daily summary of group chat conversations.

Analyze the chat transcript and provide a well-structured summary:

**Main Topics Discussed:** Key topics and themes
**Key Participants:** Users central to discussions  
**Important Decisions:** Significant decisions, announcements, or action items
**Questions & Answers:** Important questions raised and their answers
**Notable Events:** Interesting or significant events

Keep it concise, professional, and easy to read. Use emojis sparingly for visual appeal.

**Conversation Transcript:**
{transcript}

Provide only the final summary without any analysis steps, thinking process, or meta-commentary. Do not include phrases like "thinking about", "analyzing", or "processing".
"""
        
        response = await get_ai_response(prompt)
        
        if response and isinstance(response, dict) and response.get('success'):
            return response.get('message', "Summary completed successfully.")
        elif isinstance(response, str):
            return response
        else:
            return f"**Conversation Summary**\n\nProcessed {len(messages)} messages.\nSummary generation completed with basic analysis."
    
    async def generate_overview_summary(self, summary_pages: List[SummaryPage], all_messages: List[Dict]) -> str:
        """Generate an overview summary from multiple pages"""
        try:
            # Combine key points from all pages
            all_summaries = "\n\n".join([f"**Page {page.page_number}:** {page.content[:200]}..." 
                                       for page in summary_pages if page.page_number > 0])
            
            prompt = f"""
Create a high-level overview of this multi-part conversation summary.

**Total Messages:** {len(all_messages)}
**Time Range:** {self.get_time_range(all_messages)}
**Summary Pages:** {len(summary_pages)}

**Individual Page Summaries:**
{all_summaries}

Provide a concise overview highlighting:
- Overall themes and topics
- Key participants across all timeframes
- Most important decisions or events
- Major questions or discussions

Keep it brief but comprehensive.
"""
            
            response = await get_ai_response(prompt)
            
            if response and response.get('success'):
                return f"**📋 Conversation Overview**\n\n{response.get('message', 'Overview completed.')}"
            else:
                return f"**📋 Conversation Overview**\n\nLarge conversation spanning {len(summary_pages)} pages with {len(all_messages)} total messages."
        
        except Exception as e:
            logger.error(f"Error generating overview summary: {e}")
            return f"**📋 Conversation Overview**\n\nMulti-page summary with {len(all_messages)} messages across {len(summary_pages)} sections."

# Enhanced summary function for backward compatibility
async def generate_daily_summary(decrypted_messages: List[Dict]) -> Optional[str]:
    """Enhanced daily summary with automatic pagination handling"""
    if not decrypted_messages:
        return "No conversations to summarize today."
    
    try:
        summarizer = EnhancedSummarizer()
        summary_pages = await summarizer.generate_paginated_summary(decrypted_messages)
        
        if not summary_pages:
            return "No summary could be generated."
        
        # If single page, return content directly
        if len(summary_pages) == 1:
            return summary_pages[0].content
        
        # If multiple pages, return overview + navigation info
        overview_page = summary_pages[0]  # Overview is always first
        
        navigation_info = f"\n\n📚 **Multi-Page Summary Available**\n"
        navigation_info += f"Total Pages: {overview_page.total_pages}\n"
        navigation_info += f"Total Messages: {overview_page.message_count}\n"
        navigation_info += f"Time Range: {overview_page.time_range}\n\n"
        navigation_info += "💡 Use `/summary page <number>` to view specific pages"
        
        return overview_page.content + navigation_info
    
    except Exception as e:
        logger.error(f"Error in enhanced daily summary: {e}")
        return "Summary generation encountered an error. Please try again."

# Global instance
enhanced_summarizer = EnhancedSummarizer()