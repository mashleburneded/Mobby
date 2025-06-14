# src/gemini_api_wrapper.py - Graceful Gemini API handling
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GeminiAPIWrapper:
    """Wrapper for Gemini API with graceful error handling"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.is_available = False
        self.error_message = None
        self._test_connection()
    
    def _test_connection(self):
        """Test if Gemini API is available"""
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Test")
            self.is_available = True
            logger.info("✅ Gemini API is available")
        except Exception as e:
            self.is_available = False
            self.error_message = str(e)
            if "suspended" in str(e).lower():
                logger.warning("⚠️ Gemini API key is suspended - using fallback")
            else:
                logger.warning(f"⚠️ Gemini API unavailable: {e}")
    
    async def generate_content(self, prompt: str) -> Optional[str]:
        """Generate content with fallback"""
        if not self.is_available:
            return self._get_fallback_response(prompt)
        
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Provide fallback response when Gemini is unavailable"""
        return f"I understand your request about: {prompt[:100]}... However, I'm currently experiencing technical difficulties with my advanced AI models. Please try again later or rephrase your question."

# Global instance
gemini_wrapper = None

def initialize_gemini_wrapper(api_key: str) -> GeminiAPIWrapper:
    """Initialize Gemini wrapper"""
    global gemini_wrapper
    gemini_wrapper = GeminiAPIWrapper(api_key)
    return gemini_wrapper

def get_gemini_wrapper() -> Optional[GeminiAPIWrapper]:
    """Get Gemini wrapper instance"""
    return gemini_wrapper
