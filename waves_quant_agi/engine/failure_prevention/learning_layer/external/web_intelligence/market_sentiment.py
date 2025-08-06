# failure_prevention/learning_layer/external/web_intelligence/market_sentiment.py
"""
Market Sentiment Monitor - Tracks social sentiment about market conditions and broker issues
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
from ..intelligence_fusion.pattern_synthesizer import IntelligenceData
from ...logs.failure_agent_logger import FailureLogger

class MarketSentimentMonitor:
    """Monitors social media for market sentiment and broker issues"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = FailureLogger("MarketSentimentMonitor")
        
        # Broker-specific monitoring
        self.broker_keywords = [
            'alpaca', 'interactive brokers', 'td ameritrade', 'robinhood',
            'charles schwab', 'fidelity', 'etrade', 'webull', 'thinkorswim'
        ]
        
        # Issue keywords
        self.issue_keywords = [
            'down', 'outage', 'slow', 'error', 'crash', 'frozen',
            'disconnected', 'timeout', 'lag', 'glitch', 'bug'
        ]
        
        # Market stress indicators
        self.stress_keywords = [
            'volatility', 'crash', 'circuit breaker', 'halt', 'suspended',
            'unusual activity', 'market makers', 'liquidity'
        ]
        
    async def gather_intelligence(self) -> List[IntelligenceData]:
        """Gather market sentiment intelligence"""
        intelligence = []
        
        try:
            # Twitter alternative sources (since Twitter API requires auth)
            reddit_intel = await self._monitor_trading_communities()
            intelligence.extend(reddit_intel)
            
            # Financial news sentiment
            news_intel = await self._monitor_financial_news()
            intelligence.extend(news_intel)
            
        except Exception as e:
            self.logger.error(f"Error gathering sentiment intelligence: {e}")
        
        return intelligence
    
    async def _monitor_trading_communities(self) -> List[IntelligenceData]:
        """Monitor Reddit trading communities for sentiment"""
        intelligence = []
        
        try:
            trading_subreddits = [
                'stocks', 'investing', 'SecurityAnalysis', 'ValueInvesting',
                'algotrading', 'financialindependence', 'SecurityAnalysis'
            ]
            
            async with aiohttp.ClientSession() as session:
                for subreddit in trading_subreddits:
                    await asyncio.sleep(2)  # Rate limiting
                    
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                    headers = {'User-Agent': 'MarketSentimentMonitor/1.0'}
                    
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for post in data.get('data', {}).get('children', [])[:20]:
                                post_data = post.get('data', {})
                                
                                # Analyze for broker issues or market stress
                                content = post_data.get('title', '') + ' ' + post_data.get('selftext', '')
                                sentiment_data = self._analyze_sentiment(content)
                                
                                if sentiment_data['relevance'] > 0.3:
                                    intel = IntelligenceData(
                                        source='reddit_sentiment',
                                        title=post_data.get('title', ''),
                                        content=post_data.get('selftext', '')[:500],
                                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                                        timestamp=datetime.fromtimestamp(post_data.get('created_utc', 0)),
                                        relevance_score=sentiment_data['relevance'],
                                        tags=['sentiment', 'community', subreddit] + sentiment_data['detected_issues'],
                                        metadata={
                                            'sentiment_score': sentiment_data['sentiment_score'],
                                            'broker_mentions': sentiment_data['broker_mentions'],
                                            'stress_indicators': sentiment_data['stress_indicators'],
                                            'score': post_data.get('score'),
                                            'num_comments': post_data.get('num_comments')
                                        }
                                    )
                                    intelligence.append(intel)
                                    
        except Exception as e:
            self.logger.error(f"Error monitoring trading communities: {e}")
        
        return intelligence
    
    async def _monitor_financial_news(self) -> List[IntelligenceData]:
        """Monitor financial news for market stress indicators"""
        intelligence = []
        
        try:
            # Free financial news sources
            news_sources = [
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://www.sec.gov/news/pressreleases.rss'
            ]
            
            async with aiohttp.ClientSession() as session:
                for source_url in news_sources:
                    await asyncio.sleep(3)  # Rate limiting
                    
                    try:
                        async with session.get(source_url) as response:
                            if response.status == 200:
                                # Parse RSS feed (simplified)
                                content = await response.text()
                                articles = self._parse_rss_feed(content)
                                
                                for article in articles:
                                    sentiment_data = self._analyze_sentiment(article['title'] + ' ' + article.get('description', ''))
                                    
                                    if sentiment_data['relevance'] > 0.4:  # Higher threshold for news
                                        intel = IntelligenceData(
                                            source='financial_news',
                                            title=article['title'],
                                            content=article.get('description', '')[:500],
                                            url=article.get('link', ''),
                                            timestamp=article.get('pub_date', datetime.now()),
                                            relevance_score=sentiment_data['relevance'],
                                            tags=['news', 'market_stress'] + sentiment_data['detected_issues'],
                                            metadata={
                                                'sentiment_score': sentiment_data['sentiment_score'],
                                                'stress_indicators': sentiment_data['stress_indicators'],
                                                'source_url': source_url
                                            }
                                        )
                                        intelligence.append(intel)
                                        
                    except Exception as e:
                        self.logger.warning(f"Error fetching news from {source_url}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error monitoring financial news: {e}")
        
        return intelligence
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text for market sentiment and broker issues"""
        if not text:
            return {'relevance': 0.0, 'sentiment_score': 0.0, 'broker_mentions': [], 'stress_indicators': [], 'detected_issues': []}
        
        text_lower = text.lower()
        
        # Detect broker mentions
        broker_mentions = []
        for broker in self.broker_keywords:
            if broker.lower() in text_lower:
                broker_mentions.append(broker)
        
        # Detect issue keywords
        issue_count = 0
        detected_issues = []
        for issue in self.issue_keywords:
            if issue in text_lower:
                issue_count += 1
                detected_issues.append(issue)
        
        # Detect market stress indicators
        stress_indicators = []
        stress_count = 0
        for stress in self.stress_keywords:
            if stress in text_lower:
                stress_count += 1
                stress_indicators.append(stress)
        
        # Calculate relevance score
        relevance = 0.0
        if broker_mentions and detected_issues:
            relevance += 0.6  # Broker + issue = high relevance
        elif broker_mentions:
            relevance += 0.3  # Just broker mention
        elif detected_issues:
            relevance += 0.2  # Just issues
        
        if stress_indicators:
            relevance += 0.3  # Market stress indicators
        
        # Calculate sentiment score (negative = bad, positive = good)
        sentiment_score = 0.0
        negative_words = ['down', 'crash', 'error', 'problem', 'issue', 'broken', 'fail']
        positive_words = ['up', 'working', 'fixed', 'resolved', 'stable', 'good']
        
        for word in negative_words:
            if word in text_lower:
                sentiment_score -= 0.1
        
        for word in positive_words:
            if word in text_lower:
                sentiment_score += 0.1
        
        return {
            'relevance': min(relevance, 1.0),
            'sentiment_score': max(-1.0, min(1.0, sentiment_score)),
            'broker_mentions': broker_mentions,
            'stress_indicators': stress_indicators,
            'detected_issues': detected_issues
        }
    
    def _parse_rss_feed(self, rss_content: str) -> List[Dict[str, Any]]:
        """Simple RSS feed parser"""
        articles = []
        
        try:
            # Very basic RSS parsing - in production use feedparser
            import xml.etree.ElementTree as ET
            root = ET.fromstring(rss_content)
            
            for item in root.findall('.//item')[:10]:  # Limit to 10 items
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                article = {
                    'title': title.text if title is not None else '',
                    'description': description.text if description is not None else '',
                    'link': link.text if link is not None else '',
                    'pub_date': datetime.now()  # Simplified - should parse pubDate
                }
                articles.append(article)
                
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed: {e}")
        
        return articles
