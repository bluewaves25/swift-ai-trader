# failure_prevention/__init__.py
"""
Failure Prevention Agent - Autonomous Trading System Guardian
=============================================================

A self-contained, scalable failure prevention system that monitors,
protects, and learns from both internal system behavior and external
intelligence sources to prevent trading system failures.
"""

# CLEAN IMPORTS - ONLY ENHANCED AGENT
# All other imports removed to prevent broken logger cascade issues
from .enhanced_failure_prevention_agent_v2 import EnhancedFailurePreventionAgentV2

__all__ = ['EnhancedFailurePreventionAgentV2']