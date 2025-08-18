#!/usr/bin/env python3
"""
Strategies Module - Consolidated Strategy Implementations
Contains all strategy types, HFT modules, and strategy composers in one logical place.
"""

# Import all strategy types
from .trend_following import *
from .arbitrage_based import *
from .market_making import *
from .htf import *
from .news_driven import *
from .statistical_arbitrage import *

# Import HFT modules
from .hft import *

# Import strategy composers
from .composers import *

__all__ = [
    # Strategy types
    'trend_following',
    'arbitrage_based', 
    'market_making',
    'htf',
    'news_driven',
    'statistical_arbitrage',
    
    # HFT modules
    'hft',
    
    # Strategy composers
    'composers'
]
