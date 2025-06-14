#!/usr/bin/env python3
"""
Real MCP Web Research Server - Production-grade web research and data collection
Fully compliant with Model Context Protocol standards
"""

import asyncio
import logging
import json
import sys
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
app = FastMCP("Mobius Web Research Server")

class RealWebResearchProvider:
    """Production-grade web research provider"""
    
    def __init__(self):
        self.session = None
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.last_request_time = 0
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # News API sources
        self.news_sources = {
            'crypto': [
                'https://cointelegraph.com',
                'https://coindesk.com',
                'https://decrypt.co',
                'https://theblock.co'
            ],
            'general': [
                'https://news.ycombinator.com',
                'https://techcrunch.com',
                'https://reuters.com'
            ]
        }
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {'User-Agent': self.user_agent}
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
        return self.session
    
    async def rate_limit(self):
        """Implement rate limiting"""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = datetime.now().timestamp()
    
    async def fetch_page(self, url: str) -> Dict[str, Any]:
        """Fetch and parse a web page"""
        await self.rate_limit()
        session = await self.get_session()
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return {
                        "success": True,
                        "content": content,
                        "status": response.status,
                        "url": str(response.url)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "status": response.status
                    }
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return {"success": False, "error": str(e)}
    
    def extract_text_content(self, html: str) -> str:
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
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_links(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Extract links from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith(('http://', 'https://')):
                    continue
                
                if text and len(text) > 5:  # Filter out very short link texts
                    links.append({
                        "url": href,
                        "text": text[:200],  # Limit text length
                        "domain": urlparse(href).netloc
                    })
            
            return links[:50]  # Limit to 50 links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global provider instance
provider = RealWebResearchProvider()

@app.tool()
async def web_search(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Perform web search using DuckDuckGo (no API key required)
    
    Args:
        query: Search query
        limit: Number of results to return
    
    Returns:
        Search results with titles, URLs, and snippets
    """
    try:
        # Use DuckDuckGo instant answer API
        search_url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        session = await provider.get_session()
        
        try:
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    return {"success": False, "error": f"Search API returned {response.status}"}
        except Exception as e:
            return {"success": False, "error": f"Search request failed: {str(e)}"}
        
        # Extract results
        results = []
        
        # Get instant answer if available
        if data.get('Abstract'):
            results.append({
                "title": data.get('Heading', 'Instant Answer'),
                "url": data.get('AbstractURL', ''),
                "snippet": data.get('Abstract', ''),
                "type": "instant_answer"
            })
        
        # Get related topics
        for topic in data.get('RelatedTopics', [])[:limit-1]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    "title": topic.get('Text', '')[:100],
                    "url": topic.get('FirstURL', ''),
                    "snippet": topic.get('Text', ''),
                    "type": "related_topic"
                })
        
        # If no results from DuckDuckGo, try a simple web scraping approach
        if not results:
            # Search on a few crypto news sites for crypto-related queries
            if any(term in query.lower() for term in ['crypto', 'bitcoin', 'ethereum', 'defi', 'blockchain']):
                crypto_results = await search_crypto_news(query, limit)
                results.extend(crypto_results)
        
        return {
            "success": True,
            "data": {
                "query": query,
                "result_count": len(results),
                "results": results
            },
            "source": "DuckDuckGo API + Web Scraping",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error performing web search: {e}")
        return {"success": False, "error": str(e)}

async def search_crypto_news(query: str, limit: int) -> List[Dict[str, Any]]:
    """Search crypto news sites for relevant content"""
    results = []
    
    try:
        # Search CoinTelegraph
        ct_url = "https://cointelegraph.com"
        page_data = await provider.fetch_page(ct_url)
        
        if page_data["success"]:
            soup = BeautifulSoup(page_data["content"], 'html.parser')
            
            # Find article links
            for article in soup.find_all('a', href=True)[:limit]:
                href = article['href']
                text = article.get_text(strip=True)
                
                if (text and len(text) > 20 and 
                    any(term.lower() in text.lower() for term in query.split())):
                    
                    if href.startswith('/'):
                        href = urljoin(ct_url, href)
                    
                    results.append({
                        "title": text[:150],
                        "url": href,
                        "snippet": f"Article from CoinTelegraph: {text[:200]}",
                        "type": "news_article",
                        "source": "CoinTelegraph"
                    })
                    
                    if len(results) >= limit:
                        break
        
    except Exception as e:
        logger.warning(f"Error searching crypto news: {e}")
    
    return results

@app.tool()
async def extract_webpage_content(url: str) -> Dict[str, Any]:
    """
    Extract and analyze content from a specific webpage
    
    Args:
        url: URL to extract content from
    
    Returns:
        Extracted content including text, links, and metadata
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {"success": False, "error": "Invalid URL format"}
        
        # Fetch the page
        page_data = await provider.fetch_page(url)
        
        if not page_data["success"]:
            return {"success": False, "error": page_data["error"]}
        
        html_content = page_data["content"]
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else "No title"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract main content
        text_content = provider.extract_text_content(html_content)
        
        # Extract links
        links = provider.extract_links(html_content, url)
        
        # Extract images
        images = []
        for img in soup.find_all('img', src=True)[:20]:  # Limit to 20 images
            src = img['src']
            alt = img.get('alt', '')
            
            # Convert relative URLs to absolute
            if src.startswith('/'):
                src = urljoin(url, src)
            
            if src.startswith(('http://', 'https://')):
                images.append({
                    "url": src,
                    "alt_text": alt,
                    "title": img.get('title', '')
                })
        
        # Basic content analysis
        word_count = len(text_content.split())
        
        # Extract headings
        headings = []
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    "level": i,
                    "text": heading.get_text(strip=True)
                })
        
        return {
            "success": True,
            "data": {
                "url": url,
                "title": title_text,
                "description": description,
                "word_count": word_count,
                "text_content": text_content[:5000],  # Limit to 5000 chars
                "headings": headings[:20],  # Limit to 20 headings
                "links": links,
                "images": images,
                "domain": parsed_url.netloc,
                "extracted_at": datetime.now().isoformat()
            },
            "source": "Web Scraping",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error extracting webpage content: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def monitor_news_sources(category: str = "crypto", limit: int = 20) -> Dict[str, Any]:
    """
    Monitor news sources for latest articles
    
    Args:
        category: News category (crypto, general)
        limit: Number of articles to return
    
    Returns:
        Latest news articles from monitored sources
    """
    try:
        sources = provider.news_sources.get(category, provider.news_sources['crypto'])
        all_articles = []
        
        for source_url in sources:
            try:
                page_data = await provider.fetch_page(source_url)
                
                if not page_data["success"]:
                    continue
                
                soup = BeautifulSoup(page_data["content"], 'html.parser')
                domain = urlparse(source_url).netloc
                
                # Extract articles based on common patterns
                articles = []
                
                # Look for article links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text(strip=True)
                    
                    # Filter for article-like links
                    if (text and len(text) > 30 and len(text) < 200 and
                        not any(skip in href.lower() for skip in ['javascript:', 'mailto:', '#'])):
                        
                        # Convert relative URLs
                        if href.startswith('/'):
                            href = urljoin(source_url, href)
                        
                        # Check if it looks like an article URL
                        if (href.startswith(('http://', 'https://')) and
                            any(pattern in href for pattern in ['/news/', '/article/', '/post/', '/blog/', str(datetime.now().year)])):
                            
                            articles.append({
                                "title": text,
                                "url": href,
                                "source": domain,
                                "category": category,
                                "discovered_at": datetime.now().isoformat()
                            })
                
                # Add unique articles (avoid duplicates)
                seen_titles = {article["title"] for article in all_articles}
                for article in articles:
                    if article["title"] not in seen_titles:
                        all_articles.append(article)
                        seen_titles.add(article["title"])
                        
                        if len(all_articles) >= limit:
                            break
                
                if len(all_articles) >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"Error monitoring {source_url}: {e}")
                continue
        
        return {
            "success": True,
            "data": {
                "category": category,
                "sources_monitored": len(sources),
                "article_count": len(all_articles),
                "articles": all_articles[:limit]
            },
            "source": "News Source Monitoring",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error monitoring news sources: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def analyze_website_structure(url: str) -> Dict[str, Any]:
    """
    Analyze the structure and technology stack of a website
    
    Args:
        url: Website URL to analyze
    
    Returns:
        Website structure analysis and technology detection
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {"success": False, "error": "Invalid URL format"}
        
        # Fetch the page
        page_data = await provider.fetch_page(url)
        
        if not page_data["success"]:
            return {"success": False, "error": page_data["error"]}
        
        html_content = page_data["content"]
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Analyze structure
        analysis = {
            "url": url,
            "domain": parsed_url.netloc,
            "title": soup.find('title').get_text(strip=True) if soup.find('title') else "No title",
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Count HTML elements
        element_counts = {}
        for tag in ['div', 'span', 'p', 'a', 'img', 'script', 'link', 'meta']:
            element_counts[tag] = len(soup.find_all(tag))
        
        analysis["element_counts"] = element_counts
        
        # Detect technologies
        technologies = []
        
        # Check for common frameworks/libraries
        if soup.find('script', src=re.compile(r'react', re.I)):
            technologies.append("React")
        if soup.find('script', src=re.compile(r'vue', re.I)):
            technologies.append("Vue.js")
        if soup.find('script', src=re.compile(r'angular', re.I)):
            technologies.append("Angular")
        if soup.find('script', src=re.compile(r'jquery', re.I)):
            technologies.append("jQuery")
        if soup.find('link', href=re.compile(r'bootstrap', re.I)):
            technologies.append("Bootstrap")
        
        # Check meta tags for generators
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator:
            technologies.append(f"Generated by: {generator.get('content', '')}")
        
        analysis["detected_technologies"] = technologies
        
        # Analyze page structure
        structure = {
            "has_navigation": bool(soup.find(['nav', 'ul', 'ol'])),
            "has_header": bool(soup.find(['header', 'h1'])),
            "has_footer": bool(soup.find('footer')),
            "has_sidebar": bool(soup.find(['aside', 'div'], class_=re.compile(r'sidebar', re.I))),
            "form_count": len(soup.find_all('form')),
            "external_link_count": len([a for a in soup.find_all('a', href=True) 
                                      if urlparse(a['href']).netloc and 
                                      urlparse(a['href']).netloc != parsed_url.netloc])
        }
        
        analysis["page_structure"] = structure
        
        # Extract social media links
        social_links = []
        social_patterns = {
            'twitter': r'twitter\.com',
            'facebook': r'facebook\.com',
            'linkedin': r'linkedin\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com',
            'github': r'github\.com',
            'telegram': r't\.me'
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href, re.I):
                    social_links.append({
                        "platform": platform,
                        "url": href
                    })
                    break
        
        analysis["social_media_links"] = social_links
        
        return {
            "success": True,
            "data": analysis,
            "source": "Website Structure Analysis",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing website structure: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def research_topic(topic: str, depth: str = "basic") -> Dict[str, Any]:
    """
    Perform comprehensive research on a topic
    
    Args:
        topic: Research topic
        depth: Research depth (basic, detailed, comprehensive)
    
    Returns:
        Comprehensive research results
    """
    try:
        research_results = {
            "topic": topic,
            "depth": depth,
            "research_started": datetime.now().isoformat(),
            "sources": []
        }
        
        # Step 1: Web search
        search_results = await web_search(topic, limit=10)
        if search_results["success"]:
            research_results["search_results"] = search_results["data"]
        
        # Step 2: Extract content from top results
        content_extractions = []
        if search_results["success"]:
            for result in search_results["data"]["results"][:3]:  # Top 3 results
                if result.get("url"):
                    content = await extract_webpage_content(result["url"])
                    if content["success"]:
                        content_extractions.append({
                            "source_url": result["url"],
                            "source_title": result.get("title", ""),
                            "content_summary": content["data"]["text_content"][:1000],
                            "word_count": content["data"]["word_count"]
                        })
        
        research_results["content_extractions"] = content_extractions
        
        # Step 3: If crypto-related, get additional crypto news
        if any(term in topic.lower() for term in ['crypto', 'bitcoin', 'ethereum', 'defi', 'blockchain']):
            crypto_news = await monitor_news_sources("crypto", limit=5)
            if crypto_news["success"]:
                research_results["related_news"] = crypto_news["data"]["articles"]
        
        # Step 4: Generate research summary
        total_sources = len(content_extractions)
        total_words = sum(extract.get("word_count", 0) for extract in content_extractions)
        
        research_results["summary"] = {
            "sources_analyzed": total_sources,
            "total_words_processed": total_words,
            "research_quality": "high" if total_sources >= 3 else "medium" if total_sources >= 1 else "low",
            "completion_time": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": research_results,
            "source": "Comprehensive Web Research",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error researching topic: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Real MCP Web Research Server")
    parser.add_argument("--port", type=int, default=8013, help="Port to run the server on")
    args = parser.parse_args()
    
    # Server startup
    logger.info("🚀 Real MCP Web Research Server starting up...")
    logger.info("🔍 Available tools: web_search, extract_webpage_content, monitor_news_sources, analyze_website_structure, research_topic")
    
    # Run the server using FastMCP's built-in runner
    logger.info(f"🌐 Starting REAL MCP Web Research Server on port {args.port}")
    
    try:
        # Use uvicorn with FastMCP's streamable HTTP app
        import uvicorn
        http_app = app.streamable_http_app()
        uvicorn.run(http_app, host="0.0.0.0", port=args.port, log_level="info")
    except KeyboardInterrupt:
        logger.info("🛑 Real MCP Web Research Server shutting down...")
    finally:
        # Cleanup
        import asyncio
        asyncio.run(provider.close())