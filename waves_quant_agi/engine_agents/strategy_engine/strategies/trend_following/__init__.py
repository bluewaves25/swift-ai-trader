#!/usr/bin/env python3
"""
Trend Following Strategies Module
Contains all trend following strategy implementations.
"""

from .moving_average_crossover import MovingAverageCrossoverStrategy
from .breakout_strategy import BreakoutStrategy
from .momentum_rider import MomentumRiderStrategy

__all__ = [
    'MovingAverageCrossoverStrategy',
    'BreakoutStrategy', 
    'MomentumRiderStrategy'
]
