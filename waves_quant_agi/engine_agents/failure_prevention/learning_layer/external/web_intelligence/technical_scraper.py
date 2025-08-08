# failure_prevention/learning_layer/external/web_intelligence/technical_scraper.py
"""
Technical Intelligence Scraper - Gathers technical issues from developer communities
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from ..intelligence_fusion.pattern_synthesizer import IntelligenceData
from ...logs.failure_agent_logger import FailureAgentLogger

class TechnicalScraper:
    """Scrapes technical forums and repositories for relevant issues"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureAgentLogger("TechnicalScraper")
        
        # Search terms for trading system issues
        self.search_terms = [
            "trading bot memory leak",
            "asyncio trading system",
            "broker api disconnect",
            "python trading lag",
            "market data freeze",
            "order execution failure",
            "websocket trading disconnect"
        ]
        
        # Rate limiting
        self.rate_limit_delay = config.get('rate_limit_delay', 2.0)
        self.max_results_per_search = config.get('max_results', 10)
        
    async def gather_intelligence(self) -> List[IntelligenceData]:
        """Gather technical intelligence from various sources"""
        intelligence = []
        
        try:
            # GitHub Issues
            github_intel = await self._scrape_github_issues()
            intelligence.extend(github_intel)
            
            # Stack Overflow
            stackoverflow_intel = await self._scrape_stackoverflow()
            intelligence.extend(stackoverflow_intel)
            
            # Reddit (trading dev communities)
            reddit_intel = await self._scrape_reddit()
            intelligence.extend(reddit_intel)
            
        except Exception as e:
            self.logger.error(f"Error gathering technical intelligence: {e}")
        
        return intelligence
    
    async def _scrape_github_issues(self) -> List[IntelligenceData]:
        """Scrape GitHub issues related to trading systems"""
        intelligence = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for term in self.search_terms:
                    await asyncio.sleep(self.rate_limit_delay)
                    
                    # GitHub API search
                    url = f"https://api.github.com/search/issues"
                    params = {
                        'q': f"{term} language:python",
                        'sort': 'updated',
                        'per_page': self.max_results_per_search
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get('items', []):
                                intel = IntelligenceData(
                                    source='github',
                                    title=item.get('title', ''),
                                    content=item.get('body', '')[:1000],  # Limit content
                                    url=item.get('html_url', ''),
                                    timestamp=datetime.fromisoformat(item.get('updated_at', '').replace('Z', '+00:00')),
                                    relevance_score=self._calculate_relevance(item.get('title', '') + ' ' + item.get('body', '')),
                                    tags=['github', 'technical', 'issue'],
                                    metadata={
                                        'state': item.get('state'),
                                        'comments': item.get('comments'),
                                        'repository': item.get('repository_url', '').split('/')[-1] if item.get('repository_url') else None
                                    }
                                )
                                
                                if intel.relevance_score > 0.3:  # Only include relevant issues
                                    intelligence.append(intel)
                        
                        elif response.status == 403:  # Rate limited
                            self.logger.warning("GitHub API rate limited")
                            await asyncio.sleep(60)
                            
        except Exception as e:
            self.logger.error(f"Error scraping GitHub: {e}")
        
        return intelligence
    
    async def _scrape_stackoverflow(self) -> List[IntelligenceData]:
        """Scrape Stack Overflow for trading system issues"""
        intelligence = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for term in self.search_terms:
                    await asyncio.sleep(self.rate_limit_delay)
                    
                    # Stack Overflow API
                    url = "https://api.stackexchange.com/2.3/search/advanced"
                    params = {
                        'order': 'desc',
                        'sort': 'activity',
                        'q': term,
                        'site': 'stackoverflow',
                        'pagesize': self.max_results_per_search
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get('items', []):
                                intel = IntelligenceData(
                                    source='stackoverflow',
                                    title=item.get('title', ''),
                                    content=self._clean_html(item.get('body', ''))[:1000],
                                    url=item.get('link', ''),
                                    timestamp=datetime.fromtimestamp(item.get('last_activity_date', 0)),
                                    relevance_score=self._calculate_relevance(item.get('title', '')),
                                    tags=['stackoverflow', 'technical', 'q&a'],
                                    metadata={
                                        'score': item.get('score'),
                                        'answer_count': item.get('answer_count'),
                                        'view_count': item.get('view_count'),
                                        'is_answered': item.get('is_answered', False)
                                    }
                                )
                                
                                if intel.relevance_score > 0.3:
                                    intelligence.append(intel)
                                    
        except Exception as e:
            self.logger.error(f"Error scraping Stack Overflow: {e}")
        
        return intelligence
    
    async def _scrape_reddit(self) -> List[IntelligenceData]:
        """Scrape Reddit trading development communities"""
        intelligence = []
        
        try:
            # Reddit communities to monitor
            subreddits = ['algotrading', 'python', 'quantfinance', 'SecurityAnalysis']
            
            async with aiohttp.ClientSession() as session:
                for subreddit in subreddits:
                    await asyncio.sleep(self.rate_limit_delay)
                    
                    # Reddit JSON API (no auth required for public posts)
                    url = f"https://www.reddit.com/r/{subreddit}/new.json"
                    params = {'limit': self.max_results_per_search}
                    
                    headers = {'User-Agent': 'TradingSystemMonitor/1.0'}
                    
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for post in data.get('data', {}).get('children', []):
                                post_data = post.get('data', {})
                                
                                # Check if post is relevant to trading systems
                                title_content = post_data.get('title', '') + ' ' + post_data.get('selftext', '')
                                relevance = self._calculate_relevance(title_content)
                                
                                if relevance > 0.2:  # Lower threshold for Reddit
                                    intel = IntelligenceData(
                                        source='reddit',
                                        title=post_data.get('title', ''),
                                        content=post_data.get('selftext', '')[:1000],
                                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                                        timestamp=datetime.fromtimestamp(post_data.get('created_utc', 0)),
                                        relevance_score=relevance,
                                        tags=['reddit', 'community', subreddit],
                                        metadata={
                                            'score': post_data.get('score'),
                                            'num_comments': post_data.get('num_comments'),
                                            'upvote_ratio': post_data.get('upvote_ratio'),
                                            'subreddit': subreddit
                                        }
                                    )
                                    intelligence.append(intel)
                                    
        except Exception as e:
            self.logger.error(f"Error scraping Reddit: {e}")
        
        return intelligence
    
    def _calculate_relevance(self, text: str) -> float:
        """Calculate relevance score for text content"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # High-value keywords
        high_value_keywords = [
            'trading', 'broker', 'api', 'disconnect', 'timeout',
            'memory leak', 'asyncio', 'websocket', 'order execution',
            'market data', 'lag', 'freeze', 'crash', 'error'
        ]
        
        # Medium-value keywords
        medium_value_keywords = [
            'python', 'async', 'threading', 'multiprocessing',
            'network', 'connection', 'database', 'redis', 'queue'
        ]
        
        score = 0.0
        
        # Count high-value keywords
        for keyword in high_value_keywords:
            if keyword in text_lower:
                score += 0.3
        
        # Count medium-value keywords
        for keyword in medium_value_keywords:
            if keyword in text_lower:
                score += 0.1
        
        # Boost score for trading-specific content
        if any(term in text_lower for term in ['trading bot', 'algo trading', 'quantitative']):
            score += 0.4
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text"""
        if not html_text:
            return ""
        
        try:
            # Remove HTML tags
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text()
        except:
            # Fallback: simple regex cleaning
            return re.sub(r'<[^>]+>', '', html_text)