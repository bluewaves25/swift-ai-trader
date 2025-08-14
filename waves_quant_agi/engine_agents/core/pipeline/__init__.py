# System Coordination Pipeline
# Focused ONLY on system coordination pipeline
# All trading and execution pipeline moved to Strategy Engine Agent

from .execution_pipeline import SystemCoordinationPipeline

__all__ = [
    'SystemCoordinationPipeline'
]