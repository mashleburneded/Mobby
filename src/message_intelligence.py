"""
Message Intelligence System for Möbius AI Assistant
Provides advanced message analysis, search, and intelligence features
"""
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from ai_providers import generate_text
from config import config

logger = logging.getLogger(__name__)

@dataclass
class MessageSearchResult:
    user: str
    text: str
    timestamp: str
    message_id: int
    relevance_score: float = 0.0

@dataclass
class TopicAnalysis:
    topic: str
    summary: str
    participants: List[str]
    message_count: int
    key_points: List[str]

class MessageIntelligence:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def search_messages_by_keyword(self, decrypted_messages: List[Dict], keyword: str) -> List[MessageSearchResult]:
        """Search messages for a specific keyword"""
        results = []
        keyword_lower = keyword.lower()
        
        for msg in decrypted_messages:
            text = msg.get('text', '')
            if keyword_lower in text.lower():
                # Calculate relevance score based on keyword frequency and position
                keyword_count = text.lower().count(keyword_lower)
                position_bonus = 1.0 if text.lower().startswith(keyword_lower) else 0.5
                relevance_score = keyword_count * position_bonus
                
                results.append(MessageSearchResult(
                    user=msg.get('user', 'Unknown'),
                    text=text,
                    timestamp=msg.get('timestamp', ''),
                    message_id=msg.get('message_id', 0),
                    relevance_score=relevance_score
                ))
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    def find_user_mentions(self, decrypted_messages: List[Dict], username: str) -> List[MessageSearchResult]:
        """Find all messages that mention a specific user"""
        results = []
        mention_patterns = [
            f"@{username}",
            f"@{username.lower()}",
            username,
            username.lower()
        ]
        
        for msg in decrypted_messages:
            text = msg.get('text', '')
            for pattern in mention_patterns:
                if pattern in text.lower():
                    results.append(MessageSearchResult(
                        user=msg.get('user', 'Unknown'),
                        text=text,
                        timestamp=msg.get('timestamp', ''),
                        message_id=msg.get('message_id', 0),
                        relevance_score=1.0
                    ))
                    break
        
        return results
    
    def extract_action_items(self, decrypted_messages: List[Dict]) -> List[str]:
        """Extract action items from messages using pattern matching"""
        action_items = []
        action_patterns = [
            r'(?:TODO|todo|To do|TO DO)[:]\s*(.+)',
            r'(?:ACTION|action|Action)[:]\s*(.+)',
            r'(?:TASK|task|Task)[:]\s*(.+)',
            r'(?:@\w+)\s+(?:should|needs to|must|will)\s+(.+)',
            r'(?:I will|I\'ll|I need to|I have to)\s+(.+)',
            r'(?:We need to|We should|We must)\s+(.+)',
            r'(?:Please|Can you|Could you)\s+(.+)',
            r'(?:Remember to|Don\'t forget to)\s+(.+)'
        ]
        
        for msg in decrypted_messages:
            text = msg.get('text', '')
            user = msg.get('user', 'Unknown')
            
            for pattern in action_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    action_text = match.group(1).strip()
                    if len(action_text) > 5:  # Filter out very short matches
                        action_items.append(f"**{user}**: {action_text}")
        
        return action_items
    
    def extract_unanswered_questions(self, decrypted_messages: List[Dict]) -> List[str]:
        """Extract questions that weren't answered in subsequent messages"""
        questions = []
        question_patterns = [
            r'(.+\?)',  # Simple question mark
            r'(?:What|How|Why|When|Where|Who|Which|Can|Could|Would|Should|Is|Are|Do|Does|Did|Will|Have|Has)\s+(.+\?)',
            r'(?:Anyone know|Does anyone|Can someone)\s+(.+\?)'
        ]
        
        # First, collect all questions with timestamps
        question_data = []
        for msg in decrypted_messages:
            text = msg.get('text', '')
            user = msg.get('user', 'Unknown')
            timestamp = msg.get('timestamp', '')
            
            for pattern in question_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    question_text = match.group(0).strip()
                    if len(question_text) > 10:  # Filter out very short questions
                        question_data.append({
                            'text': question_text,
                            'user': user,
                            'timestamp': timestamp,
                            'answered': False
                        })
        
        # Check if questions were answered by looking at subsequent messages
        for i, question in enumerate(question_data):
            question_time = datetime.fromisoformat(question['timestamp'].replace('Z', '+00:00'))
            
            # Look for answers in the next 30 minutes
            for msg in decrypted_messages:
                msg_time = datetime.fromisoformat(msg.get('timestamp', '').replace('Z', '+00:00'))
                if msg_time > question_time and msg_time < question_time + timedelta(minutes=30):
                    # Simple heuristic: if someone responds to the question author, it might be an answer
                    if (msg.get('user') != question['user'] and 
                        len(msg.get('text', '')) > 20):  # Substantial response
                        question['answered'] = True
                        break
        
        # Return unanswered questions
        for question in question_data:
            if not question['answered']:
                questions.append(f"**{question['user']}**: {question['text']}")
        
        return questions
    
    async def analyze_topic_specific(self, decrypted_messages: List[Dict], topic_keyword: str) -> Optional[TopicAnalysis]:
        """Analyze messages related to a specific topic"""
        relevant_messages = self.search_messages_by_keyword(decrypted_messages, topic_keyword)
        
        if not relevant_messages:
            return None
        
        # Extract unique participants
        participants = list(set([msg.user for msg in relevant_messages]))
        
        # Create transcript for AI analysis
        transcript_parts = []
        for msg in relevant_messages:
            transcript_parts.append(f"[{msg.timestamp}] {msg.user}: {msg.text}")
        transcript = "\n".join(transcript_parts)
        
        # Generate AI summary
        provider = config.get('ACTIVE_AI_PROVIDER')
        api_key = config.get('AI_API_KEYS', {}).get(provider)
        
        if not api_key:
            # Fallback to simple analysis
            return TopicAnalysis(
                topic=topic_keyword,
                summary=f"Found {len(relevant_messages)} messages about '{topic_keyword}' from {len(participants)} participants.",
                participants=participants,
                message_count=len(relevant_messages),
                key_points=[f"Discussion involved {', '.join(participants)}"]
            )
        
        system_prompt = f"""
        Analyze the following conversation transcript that relates to the topic: "{topic_keyword}".
        
        Provide a structured analysis with:
        1. A concise summary of the discussion
        2. Key points or decisions made
        3. Main participants and their contributions
        
        Focus only on content related to "{topic_keyword}".
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transcript:\n\n{transcript}"}
        ]
        
        try:
            ai_summary = await generate_text(provider, api_key, messages)
            
            return TopicAnalysis(
                topic=topic_keyword,
                summary=ai_summary or f"Discussion about {topic_keyword}",
                participants=participants,
                message_count=len(relevant_messages),
                key_points=[]  # Could be extracted from AI response
            )
        except Exception as e:
            logger.error(f"Failed to generate AI topic analysis: {e}")
            return TopicAnalysis(
                topic=topic_keyword,
                summary=f"Found {len(relevant_messages)} messages about '{topic_keyword}' from {len(participants)} participants.",
                participants=participants,
                message_count=len(relevant_messages),
                key_points=[f"Discussion involved {', '.join(participants)}"]
            )
    
    async def generate_weekly_digest(self, daily_summaries: List[str]) -> str:
        """Generate a weekly digest from daily summaries"""
        if not daily_summaries:
            return "No daily summaries available for the weekly digest."
        
        provider = config.get('ACTIVE_AI_PROVIDER')
        api_key = config.get('AI_API_KEYS', {}).get(provider)
        
        if not api_key:
            # Fallback to simple concatenation
            return "## Weekly Digest\n\n" + "\n\n---\n\n".join(daily_summaries)
        
        combined_summaries = "\n\n".join([f"Day {i+1}:\n{summary}" for i, summary in enumerate(daily_summaries)])
        
        system_prompt = """
        Create a comprehensive weekly digest from the provided daily summaries.
        
        Structure your response as:
        1. **Week Overview** - High-level summary of the week's activities
        2. **Key Themes** - Major topics that emerged throughout the week
        3. **Important Decisions** - Any significant decisions or conclusions
        4. **Ongoing Discussions** - Topics that continued across multiple days
        5. **Action Items** - Outstanding tasks or follow-ups needed
        
        Use Markdown formatting and be concise but comprehensive.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Daily summaries for the week:\n\n{combined_summaries}"}
        ]
        
        try:
            weekly_digest = await generate_text(provider, api_key, messages)
            return weekly_digest or "Weekly digest generation failed."
        except Exception as e:
            logger.error(f"Failed to generate weekly digest: {e}")
            return f"## Weekly Digest\n\nError generating AI digest. Raw summaries:\n\n{combined_summaries}"
    
    def get_conversation_stats(self, decrypted_messages: List[Dict]) -> Dict:
        """Get basic statistics about the conversation"""
        if not decrypted_messages:
            return {}
        
        users = {}
        total_messages = len(decrypted_messages)
        total_words = 0
        
        for msg in decrypted_messages:
            user = msg.get('user', 'Unknown')
            text = msg.get('text', '')
            word_count = len(text.split())
            
            if user not in users:
                users[user] = {'messages': 0, 'words': 0}
            
            users[user]['messages'] += 1
            users[user]['words'] += word_count
            total_words += word_count
        
        # Sort users by message count
        sorted_users = sorted(users.items(), key=lambda x: x[1]['messages'], reverse=True)
        
        return {
            'total_messages': total_messages,
            'total_words': total_words,
            'unique_users': len(users),
            'most_active_user': sorted_users[0][0] if sorted_users else 'None',
            'user_stats': dict(sorted_users[:5])  # Top 5 users
        }

# Global instance
message_intelligence = MessageIntelligence()