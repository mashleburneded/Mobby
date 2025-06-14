# src/clean_summarizer.py
"""
Clean Summarizer that removes thinking process and provides clean output
"""

import re
import logging
from typing import List, Dict, Optional
from datetime import datetime
from ai_providers_enhanced import get_ai_response

logger = logging.getLogger(__name__)

class CleanSummarizer:
    """Summarizer that produces clean output without thinking artifacts"""
    
    def __init__(self):
        self.thinking_patterns = [
            r'<think>.*?</think>',
            r'<thinking>.*?</thinking>',
            r'Let me.*?analyze.*?\n',
            r'I need to.*?\n',
            r'Looking at.*?\n',
            r'Based on.*?analysis.*?\n',
            r'From.*?conversation.*?\n',
            r'Analyzing.*?\n',
            r'First.*?let me.*?\n',
            r'I\'ll.*?examine.*?\n',
            r'Upon.*?review.*?\n'
        ]
        
        self.summary_template = """
📊 **Daily Group Chat Summary**

**Main Topics Discussed:**
{main_topics}

**Key Participants:**
{key_participants}

**Important Decisions:**
{important_decisions}

**Questions & Answers:**
{questions_answers}

**Notable Events:**
{notable_events}
"""
    
    def clean_ai_response(self, response: str) -> str:
        """Remove thinking artifacts from AI response"""
        if not response:
            return ""
        
        # Remove thinking tags and content
        for pattern in self.thinking_patterns:
            response = re.sub(pattern, '', response, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove analysis prefixes
        lines = response.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            r'^(Looking at|Analyzing|Based on|From the|Upon|First|I\'ll|I need to|Let me)',
            r'^(The conversation|This conversation|In this conversation)',
            r'^(After reviewing|After analyzing|After examining)'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append(line)
                continue
            
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip:
                cleaned_lines.append(line)
        
        # Join and clean up extra whitespace
        cleaned = '\n'.join(cleaned_lines)
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Remove excessive newlines
        cleaned = cleaned.strip()
        
        return cleaned
    
    async def generate_summary(self, messages: List[Dict]) -> str:
        """Generate a clean summary from messages"""
        try:
            if not messages:
                return self._create_empty_summary()
            
            # Prepare conversation data
            conversation_text = self._prepare_conversation_text(messages)
            
            if not conversation_text.strip():
                return self._create_empty_summary()
            
            # Create summary prompt
            prompt = self._create_summary_prompt(conversation_text)
            
            # Get AI response
            response = await get_ai_response(prompt, 0)
            
            if not response:
                return self._create_fallback_summary(messages)
            
            # Clean the response
            cleaned_response = self.clean_ai_response(response)
            
            # Validate and format
            if self._is_valid_summary(cleaned_response):
                return cleaned_response
            else:
                return self._create_fallback_summary(messages)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._create_error_summary()
    
    def _prepare_conversation_text(self, messages: List[Dict]) -> str:
        """Prepare conversation text for summarization"""
        conversation_lines = []
        
        # Get last 50 messages to avoid token limits
        recent_messages = messages[-50:] if len(messages) > 50 else messages
        
        for msg in recent_messages:
            try:
                username = msg.get('username', 'Unknown')
                text = msg.get('text', '')
                timestamp = msg.get('timestamp', 0)
                
                if text and len(text.strip()) > 0:
                    time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                    conversation_lines.append(f"{time_str} {username}: {text}")
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue
        
        return '\n'.join(conversation_lines)
    
    def _create_summary_prompt(self, conversation_text: str) -> str:
        """Create a prompt for summary generation"""
        return f"""
Generate a professional daily summary of this group chat conversation. Follow this EXACT structure and format:

📊 **Daily Group Chat Summary**

**Main Topics Discussed:**
- [List 3-5 key topics that were actually discussed, or write "No significant topics discussed"]

**Key Participants:**
- [List the most active participants by username, or write "Various participants"]

**Important Decisions:**
- [List any decisions that were made, or write "None noted"]

**Questions & Answers:**
- [List key questions and their answers, or write "None noted"]

**Notable Events:**
- [List any significant events or announcements, or write "None noted"]

CRITICAL INSTRUCTIONS:
1. Provide ONLY the final summary in the exact format above
2. Do NOT include any thinking process, analysis, or meta-commentary
3. Do NOT start with phrases like "Looking at", "Based on", "Analyzing"
4. Be concise and factual
5. If a section has no content, write "None noted" or similar
6. Use bullet points with dashes (-)

Conversation data:
{conversation_text}
"""
    
    def _is_valid_summary(self, summary: str) -> bool:
        """Check if summary is valid and properly formatted"""
        if not summary or len(summary.strip()) < 50:
            return False
        
        # Check for required sections
        required_sections = [
            "Daily Group Chat Summary",
            "Main Topics Discussed",
            "Key Participants",
            "Important Decisions",
            "Questions & Answers",
            "Notable Events"
        ]
        
        for section in required_sections:
            if section not in summary:
                return False
        
        # Check it doesn't contain thinking artifacts
        thinking_indicators = [
            "<think>", "</think>", "Looking at", "Analyzing", "Based on the conversation"
        ]
        
        for indicator in thinking_indicators:
            if indicator in summary:
                return False
        
        return True
    
    def _create_empty_summary(self) -> str:
        """Create summary for when no messages are available"""
        return self.summary_template.format(
            main_topics="- No significant conversations recorded",
            key_participants="- No active participants",
            important_decisions="- None noted",
            questions_answers="- None noted",
            notable_events="- None noted"
        )
    
    def _create_fallback_summary(self, messages: List[Dict]) -> str:
        """Create a basic summary when AI fails"""
        try:
            # Count participants
            participants = set()
            message_count = 0
            
            for msg in messages[-20:]:  # Last 20 messages
                username = msg.get('username', 'Unknown')
                if username != 'Unknown':
                    participants.add(username)
                message_count += 1
            
            participant_list = list(participants)[:5]  # Top 5
            
            return self.summary_template.format(
                main_topics="- General conversation and discussion",
                key_participants=f"- {', '.join(participant_list)}" if participant_list else "- Various participants",
                important_decisions="- None noted",
                questions_answers="- None noted",
                notable_events=f"- {message_count} messages exchanged"
            )
            
        except Exception as e:
            logger.error(f"Error creating fallback summary: {e}")
            return self._create_error_summary()
    
    def _create_error_summary(self) -> str:
        """Create summary when there's an error"""
        return self.summary_template.format(
            main_topics="- Summary generation encountered an error",
            key_participants="- Unable to determine",
            important_decisions="- None noted",
            questions_answers="- None noted",
            notable_events="- Please try again later"
        )

# Global instance
clean_summarizer = CleanSummarizer()

async def generate_clean_summary(messages: List[Dict]) -> str:
    """Generate a clean summary without thinking artifacts"""
    return await clean_summarizer.generate_summary(messages)

def clean_ai_output(text: str) -> str:
    """Clean any AI output to remove thinking artifacts"""
    return clean_summarizer.clean_ai_response(text)