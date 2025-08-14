# System Coordination Learning Layer
# Focused ONLY on system coordination learning and research
# All trading and strategy learning moved to Strategy Engine Agent

from .research_engine import SystemCoordinationResearchEngine
from .training_module import SystemCoordinationTrainingModule
from .retraining_loop import SystemCoordinationRetrainingLoop

__all__ = [
    'SystemCoordinationResearchEngine',
    'SystemCoordinationTrainingModule', 
    'SystemCoordinationRetrainingLoop'
]