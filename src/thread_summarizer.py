# src/thread_summarizer.py
"""
Thread Summarization for Möbius AI Assistant
Handles summarization of threaded conversations
"""
import logging
from typing import List, Dict, Optional, Set
from ai_providers import get_ai_response

logger = logging.getLogger(__name__)

class ThreadSummarizer:
    """Handles thread-based conversation summarization"""
    
    def __init__(self):
        self.thread_cache = {}  # Cache thread relationships
    
    def extract_thread_messages(self, all_messages: List[Dict], root_message_id: int) -> List[Dict]:
        """Extract all messages in a thread starting from root message"""
        thread_messages = []
        processed_ids = set()
        
        # Find the root message
        root_message = None
        for msg in all_messages:
            if msg.get('message_id') == root_message_id:
                root_message = msg
                break
        
        if not root_message:
            return []
        
        # Add root message
        thread_messages.append(root_message)
        processed_ids.add(root_message_id)
        
        # Find all replies to this thread
        self._find_thread_replies(all_messages, root_message_id, thread_messages, processed_ids)
        
        # Sort by timestamp
        thread_messages.sort(key=lambda x: x.get('timestamp', ''))
        
        return thread_messages
    
    def _find_thread_replies(self, all_messages: List[Dict], parent_id: int, 
                           thread_messages: List[Dict], processed_ids: Set[int]):
        """Recursively find all replies in a thread"""
        for msg in all_messages:
            reply_to_id = msg.get('reply_to_message_id')
            msg_id = msg.get('message_id')
            
            if reply_to_id == parent_id and msg_id not in processed_ids:
                thread_messages.append(msg)
                processed_ids.add(msg_id)
                
                # Recursively find replies to this message
                self._find_thread_replies(all_messages, msg_id, thread_messages, processed_ids)
    
    def format_thread_transcript(self, thread_messages: List[Dict]) -> str:
        """Format thread messages into a readable transcript"""
        if not thread_messages:
            return "No messages in thread."
        
        transcript_parts = []
        
        for i, msg in enumerate(thread_messages):
            user = msg.get('user', 'Unknown')
            text = msg.get('text', '')
            timestamp = msg.get('timestamp', '')
            reply_to_id = msg.get('reply_to_message_id')
            
            # Format timestamp
            try:
                from datetime import datetime
                if timestamp:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M')
                else:
                    time_str = '??:??'
            except:
                time_str = '??:??'
            
            # Add thread indicators
            if i == 0:
                # Root message
                transcript_parts.append(f"🧵 **THREAD START**")
                transcript_parts.append(f"[{time_str}] {user}: {text}")
            else:
                # Reply message
                indent = "  " if reply_to_id else ""
                transcript_parts.append(f"{indent}↳ [{time_str}] {user}: {text}")
        
        transcript_parts.append(f"🧵 **THREAD END** ({len(thread_messages)} messages)")
        
        return "\n".join(transcript_parts)
    
    async def generate_thread_summary(self, thread_messages: List[Dict]) -> Optional[str]:
        """Generate AI summary of a thread conversation"""
        if not thread_messages:
            return "No messages found in this thread."
        
        if len(thread_messages) == 1:
            return "Thread contains only one message - no summary needed."
        
        transcript = self.format_thread_transcript(thread_messages)
        
        # Create specialized prompt for thread summarization
        prompt = f"""You are analyzing a threaded conversation from a Telegram group chat. Please provide a focused summary of this specific thread.

**Instructions:**
1. **Thread Overview**: Provide a brief overview of what this thread discussion was about
2. **Key Points**: List the main points discussed in chronological order
3. **Participants**: Mention who were the main contributors to this thread
4. **Resolution**: Note if any conclusion, decision, or resolution was reached
5. **Action Items**: List any specific tasks or follow-ups mentioned in this thread

**Thread Conversation:**
{transcript}

Please focus only on this specific thread and provide a concise but comprehensive summary."""

        try:
            summary = await get_ai_response(prompt)
            
            if not summary or len(summary.strip()) < 20:
                return "Unable to generate thread summary - please check AI provider configuration."
            
            # Format the response
            thread_count = len(thread_messages)
            participants = list(set(msg.get('user', 'Unknown') for msg in thread_messages))
            
            formatted_summary = f"🧵 **Thread Summary** ({thread_count} messages)\n\n"
            formatted_summary += f"👥 **Participants:** {', '.join(participants)}\n\n"
            formatted_summary += summary
            
            return formatted_summary
            
        except Exception as e:
            logger.error(f"Failed to generate thread summary: {e}")
            return f"❌ Error generating thread summary: {str(e)}"
    
    def find_thread_root(self, all_messages: List[Dict], message_id: int) -> Optional[int]:
        """Find the root message of a thread given any message in the thread"""
        # Find the message
        target_message = None
        for msg in all_messages:
            if msg.get('message_id') == message_id:
                target_message = msg
                break
        
        if not target_message:
            return None
        
        # If this message is not a reply, it's the root
        reply_to_id = target_message.get('reply_to_message_id')
        if not reply_to_id:
            return message_id
        
        # Recursively find the root
        return self.find_thread_root(all_messages, reply_to_id)
    
    def get_thread_stats(self, thread_messages: List[Dict]) -> Dict:
        """Get statistics about a thread"""
        if not thread_messages:
            return {}
        
        participants = {}
        total_chars = 0
        
        for msg in thread_messages:
            user = msg.get('user', 'Unknown')
            text = msg.get('text', '')
            
            if user not in participants:
                participants[user] = {'messages': 0, 'characters': 0}
            
            participants[user]['messages'] += 1
            participants[user]['characters'] += len(text)
            total_chars += len(text)
        
        # Calculate thread duration
        try:
            from datetime import datetime
            first_time = datetime.fromisoformat(thread_messages[0]['timestamp'].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(thread_messages[-1]['timestamp'].replace('Z', '+00:00'))
            duration = last_time - first_time
            duration_str = str(duration).split('.')[0]  # Remove microseconds
        except:
            duration_str = "Unknown"
        
        return {
            'message_count': len(thread_messages),
            'participant_count': len(participants),
            'participants': participants,
            'total_characters': total_chars,
            'duration': duration_str,
            'start_time': thread_messages[0].get('timestamp', 'Unknown'),
            'end_time': thread_messages[-1].get('timestamp', 'Unknown')
        }

# Global thread summarizer instance
thread_summarizer = ThreadSummarizer()

async def summarize_thread_by_message_id(all_messages: List[Dict], message_id: int) -> Optional[str]:
    """Summarize a thread given any message ID in the thread"""
    # Find thread root
    root_id = thread_summarizer.find_thread_root(all_messages, message_id)
    if not root_id:
        return "Could not find thread root for this message."
    
    # Extract thread messages
    thread_messages = thread_summarizer.extract_thread_messages(all_messages, root_id)
    if not thread_messages:
        return "No thread messages found."
    
    # Generate summary
    return await thread_summarizer.generate_thread_summary(thread_messages)

async def get_thread_info(all_messages: List[Dict], message_id: int) -> Optional[str]:
    """Get detailed thread information"""
    # Find thread root
    root_id = thread_summarizer.find_thread_root(all_messages, message_id)
    if not root_id:
        return "Could not find thread for this message."
    
    # Extract thread messages
    thread_messages = thread_summarizer.extract_thread_messages(all_messages, root_id)
    if not thread_messages:
        return "No thread messages found."
    
    # Get stats
    stats = thread_summarizer.get_thread_stats(thread_messages)
    
    # Format info
    info = f"🧵 **Thread Information**\n\n"
    info += f"📊 **Stats:**\n"
    info += f"• Messages: {stats['message_count']}\n"
    info += f"• Participants: {stats['participant_count']}\n"
    info += f"• Duration: {stats['duration']}\n"
    info += f"• Total characters: {stats['total_characters']}\n\n"
    
    info += f"👥 **Participants:**\n"
    for user, data in stats['participants'].items():
        info += f"• {user}: {data['messages']} messages ({data['characters']} chars)\n"
    
    info += f"\n⏰ **Timeline:**\n"
    info += f"• Started: {stats['start_time']}\n"
    info += f"• Ended: {stats['end_time']}\n"
    
    return info