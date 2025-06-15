#!/usr/bin/env python3
"""
MCP Web Research Server - Enhanced web browsing and research capabilities
Provides real-time web data, news aggregation, and research tools
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import re
import os
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with proper configuration
mcp = FastMCP(
    name="Web Research Server",
    instructions="Enhanced web browsing, news aggregation, and research capabilities"
)

class WebResearcher:
    """Enhanced web research and browsing capabilities"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Crypto news sources
        self.news_sources = {
            "cointelegraph": {
                "url": "https://cointelegraph.com",
                "rss": "https://cointelegraph.com/rss",
                "selector": ".post-card-inline__title"
            },
            "coindesk": {
                "url": "https://www.coindesk.com",
                "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "selector": ".headline"
            },
            "decrypt": {
                "url": "https://decrypt.co",
                "rss": "https://decrypt.co/feed",
                "selector": ".article-title"
            },
            "theblock": {
                "url": "https://www.theblock.co",
                "rss": "https://www.theblock.co/rss.xml",
                "selector": ".article-title"
            }
        }
        
        # DeFi data sources
        self.defi_sources = {
            "defillama": "https://defillama.com",
            "dune": "https://dune.com",
            "debank": "https://debank.com",
            "zapper": "https://zapper.fi"
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def extract_text_content(self, html: str, max_length: int = 5000) -> str:
        """Extract clean text content from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:max_length] if len(text) > max_length else text
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""

# Global researcher instance
web_researcher = WebResearcher()

@mcp.tool()
async def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Perform web search for crypto-related queries
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        Dict with search results
    """
    try:
        session = await web_researcher.get_session()
        
        # Use DuckDuckGo for search (no API key required)
        search_url = "https://html.duckduckgo.com/html/"
        params = {"q": f"{query} cryptocurrency crypto"}
        
        async with session.get(search_url, params=params) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                result_elements = soup.find_all('div', class_='result')[:max_results]
                
                for element in result_elements:
                    title_elem = element.find('a', class_='result__a')
                    snippet_elem = element.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "relevance_score": calculate_relevance_score(title + " " + snippet, query)
                        })
                
                # Sort by relevance
                results.sort(key=lambda x: x["relevance_score"], reverse=True)
                
                return {
                    "success": True,
                    "data": {
                        "query": query,
                        "results": results,
                        "total_found": len(results)
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "DuckDuckGo Search"
                }
            else:
                return {
                    "success": False,
                    "error": f"Search request failed with status {response.status}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error performing web search: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def fetch_page_content(url: str, extract_text: bool = True) -> Dict[str, Any]:
    """
    Fetch and analyze content from a specific webpage
    
    Args:
        url: URL to fetch
        extract_text: Whether to extract clean text content
    
    Returns:
        Dict with page content and analysis
    """
    try:
        session = await web_researcher.get_session()
        
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                
                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract metadata
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else "No title"
                
                meta_description = soup.find('meta', attrs={'name': 'description'})
                description = meta_description.get('content', '') if meta_description else ""
                
                # Extract text content if requested
                text_content = ""
                if extract_text:
                    text_content = web_researcher.extract_text_content(html)
                
                # Analyze content for crypto relevance
                crypto_keywords = ["bitcoin", "ethereum", "crypto", "blockchain", "defi", "nft", "web3", "dao"]
                crypto_mentions = sum(1 for keyword in crypto_keywords if keyword.lower() in text_content.lower())
                
                return {
                    "success": True,
                    "data": {
                        "url": url,
                        "title": title_text,
                        "description": description,
                        "text_content": text_content[:2000] if text_content else "",  # Limit content
                        "content_length": len(text_content),
                        "crypto_relevance": {
                            "mentions": crypto_mentions,
                            "relevance_score": min(crypto_mentions / 10 * 100, 100)
                        },
                        "last_modified": response.headers.get('Last-Modified', ''),
                        "content_type": response.headers.get('Content-Type', '')
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "Direct Page Fetch"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to fetch page: HTTP {response.status}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error fetching page content: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def get_crypto_news(sources: List[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Aggregate latest crypto news from multiple sources
    
    Args:
        sources: List of news sources (default: all available)
        limit: Maximum number of articles per source
    
    Returns:
        Dict with aggregated news data
    """
    if not sources:
        sources = list(web_researcher.news_sources.keys())
    
    try:
        session = await web_researcher.get_session()
        all_articles = []
        
        for source in sources:
            if source not in web_researcher.news_sources:
                continue
                
            try:
                source_config = web_researcher.news_sources[source]
                
                # Fetch homepage for latest articles
                async with session.get(source_config["url"]) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract article titles and links
                        articles = []
                        article_elements = soup.select(source_config["selector"])[:limit]
                        
                        for element in article_elements:
                            title = element.get_text(strip=True)
                            link = element.get('href', '') or element.find('a', href=True)
                            
                            if link and hasattr(link, 'get'):
                                link = link.get('href', '')
                            
                            # Make absolute URL
                            if link and not link.startswith('http'):
                                link = urljoin(source_config["url"], link)
                            
                            if title and link:
                                articles.append({
                                    "title": title,
                                    "url": link,
                                    "source": source,
                                    "published": datetime.now().isoformat(),  # Approximate
                                    "relevance_score": calculate_relevance_score(title, "crypto blockchain defi")
                                })
                        
                        all_articles.extend(articles)
                        
            except Exception as e:
                logger.warning(f"Failed to fetch news from {source}: {e}")
                continue
        
        # Sort by relevance and recency
        all_articles.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "articles": all_articles[:limit * 2],  # Return top articles across all sources
                "sources_checked": sources,
                "total_articles": len(all_articles)
            },
            "timestamp": datetime.now().isoformat(),
            "source": "Multi-source News Aggregation"
        }
        
    except Exception as e:
        logger.error(f"Error aggregating crypto news: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def research_defi_protocol(protocol_name: str) -> Dict[str, Any]:
    """
    Research a specific DeFi protocol across multiple sources
    
    Args:
        protocol_name: Name of the DeFi protocol to research
    
    Returns:
        Dict with comprehensive protocol research
    """
    try:
        session = await web_researcher.get_session()
        research_data = {}
        
        # Search for protocol information
        search_results = await web_search(f"{protocol_name} DeFi protocol", max_results=3)
        research_data["search_results"] = search_results.get("data", {})
        
        # Check DeFiLlama for protocol data
        try:
            defillama_url = f"https://defillama.com/protocol/{protocol_name.lower()}"
            page_content = await fetch_page_content(defillama_url)
            research_data["defillama_data"] = page_content.get("data", {})
        except Exception as e:
            logger.warning(f"Failed to fetch DeFiLlama data: {e}")
        
        # Aggregate findings
        key_findings = []
        if search_results.get("success"):
            for result in search_results["data"]["results"][:2]:
                key_findings.append({
                    "source": result["url"],
                    "finding": result["snippet"]
                })
        
        return {
            "success": True,
            "data": {
                "protocol_name": protocol_name,
                "research_summary": research_data,
                "key_findings": key_findings,
                "research_quality": "high" if len(key_findings) >= 2 else "medium"
            },
            "timestamp": datetime.now().isoformat(),
            "source": "Multi-source DeFi Research"
        }
        
    except Exception as e:
        logger.error(f"Error researching DeFi protocol: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def monitor_social_sentiment(topics: List[str] = None) -> Dict[str, Any]:
    """
    Monitor social sentiment for crypto topics
    
    Args:
        topics: List of topics to monitor (default: major cryptos)
    
    Returns:
        Dict with social sentiment analysis
    """
    if not topics:
        topics = ["bitcoin", "ethereum", "defi", "nft"]
    
    try:
        sentiment_data = {}
        
        for topic in topics:
            # Search for recent discussions
            search_results = await web_search(f"{topic} reddit twitter discussion", max_results=3)
            
            if search_results.get("success"):
                results = search_results["data"]["results"]
                
                # Analyze sentiment from titles and snippets
                positive_keywords = ["bullish", "moon", "pump", "gains", "positive", "good", "great", "amazing"]
                negative_keywords = ["bearish", "dump", "crash", "loss", "negative", "bad", "terrible", "scam"]
                
                sentiment_score = 0
                total_mentions = 0
                
                for result in results:
                    text = (result["title"] + " " + result["snippet"]).lower()
                    positive_count = sum(1 for word in positive_keywords if word in text)
                    negative_count = sum(1 for word in negative_keywords if word in text)
                    
                    sentiment_score += positive_count - negative_count
                    total_mentions += positive_count + negative_count
                
                # Normalize sentiment score
                normalized_score = 0.5  # Neutral
                if total_mentions > 0:
                    normalized_score = max(0, min(1, (sentiment_score / total_mentions + 1) / 2))
                
                sentiment_data[topic] = {
                    "sentiment_score": normalized_score,
                    "sentiment_label": get_sentiment_label(normalized_score),
                    "mentions_analyzed": total_mentions,
                    "confidence": min(total_mentions / 10, 1.0)
                }
        
        return {
            "success": True,
            "data": {
                "topics_analyzed": topics,
                "sentiment_analysis": sentiment_data,
                "overall_market_sentiment": calculate_overall_sentiment(sentiment_data)
            },
            "timestamp": datetime.now().isoformat(),
            "source": "Social Media Sentiment Analysis"
        }
        
    except Exception as e:
        logger.error(f"Error monitoring social sentiment: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def calculate_relevance_score(text: str, query: str) -> float:
    """Calculate relevance score between text and query"""
    text_lower = text.lower()
    query_words = query.lower().split()
    
    score = 0
    for word in query_words:
        if word in text_lower:
            score += 1
    
    return score / len(query_words) if query_words else 0

def get_sentiment_label(score: float) -> str:
    """Convert sentiment score to label"""
    if score >= 0.7:
        return "Very Bullish"
    elif score >= 0.6:
        return "Bullish"
    elif score >= 0.4:
        return "Neutral"
    elif score >= 0.3:
        return "Bearish"
    else:
        return "Very Bearish"

def calculate_overall_sentiment(sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall market sentiment from individual topics"""
    if not sentiment_data:
        return {"score": 0.5, "label": "Neutral", "confidence": 0}
    
    total_score = 0
    total_confidence = 0
    
    for topic_data in sentiment_data.values():
        score = topic_data["sentiment_score"]
        confidence = topic_data["confidence"]
        total_score += score * confidence
        total_confidence += confidence
    
    overall_score = total_score / total_confidence if total_confidence > 0 else 0.5
    
    return {
        "score": overall_score,
        "label": get_sentiment_label(overall_score),
        "confidence": min(total_confidence / len(sentiment_data), 1.0)
    }

# Health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for server monitoring"""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "server": "Web Research Server",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

# Server info endpoint
@mcp.custom_route("/info", methods=["GET"])
async def server_info(request):
    """Server information endpoint"""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "name": "Web Research Server",
        "description": "Enhanced web browsing, news aggregation, and research capabilities",
        "version": "1.0.0",
        "news_sources": list(web_researcher.news_sources.keys()),
        "tools": [
            "web_search",
            "fetch_page_content",
            "get_crypto_news",
            "research_defi_protocol",
            "monitor_social_sentiment"
        ],
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

# Cleanup function (called manually if needed)
async def cleanup():
    """Cleanup resources on server shutdown"""
    await web_researcher.close()
    logger.info("Web Research Server shutdown complete")

async def main():
    """Main function to start the server"""
    try:
        port = int(os.getenv("PORT", 8002))
        host = os.getenv("HOST", "0.0.0.0")
        
        logger.info(f"🚀 Starting Web Research Server on {host}:{port}")
        logger.info(f"📰 News sources: {', '.join(web_researcher.news_sources.keys())}")
        logger.info("🔧 Available tools: web_search, fetch_page_content, get_crypto_news, research_defi_protocol, monitor_social_sentiment")
        
        # Run the server with HTTP transport
        await mcp.run_http_async(transport="streamable-http", host=host, port=port)
        
    except Exception as e:
        logger.error(f"❌ Failed to start Web Research Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())