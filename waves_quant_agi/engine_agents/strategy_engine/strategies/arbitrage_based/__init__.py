#!/usr/bin/env python3
"""
Arbitrage Based Strategies Module
Contains all arbitrage-based strategy implementations.
"""

from .triangular_arbitrage import TriangularArbitrage
from .latency_arbitrage import LatencyArbitrage
from .funding_rate_arbitrage import FundingRateArbitrage

__all__ = [
    'TriangularArbitrage',
    'LatencyArbitrage',
    'FundingRateArbitrage'
]
