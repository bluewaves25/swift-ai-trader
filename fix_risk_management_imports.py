#!/usr/bin/env python3
"""
Script to fix import issues in the risk_management module.
Replaces incorrect imports from market_conditions with correct risk_management imports.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix logger imports
        content = re.sub(
            r'from \.\.market_conditions\.logs\.failure_agent_logger import FailureAgentLogger',
            'from ..logs.risk_management_logger import RiskManagementLogger',
            content
        )
        content = re.sub(
            r'from \.\.\.market_conditions\.logs\.failure_agent_logger import FailureAgentLogger',
            'from ...logs.risk_management_logger import RiskManagementLogger',
            content
        )
        content = re.sub(
            r'from \.\.\.\.market_conditions\.logs\.failure_agent_logger import FailureAgentLogger',
            'from ....logs.risk_management_logger import RiskManagementLogger',
            content
        )
        content = re.sub(
            r'from \.\.\.\.\.market_conditions\.logs\.failure_agent_logger import FailureAgentLogger',
            'from .....logs.risk_management_logger import RiskManagementLogger',
            content
        )
        
        # Fix memory imports (remove them since risk_management doesn't have IncidentCache)
        content = re.sub(
            r'from \.\.market_conditions\.memory\.incident_cache import IncidentCache\n',
            '',
            content
        )
        content = re.sub(
            r'from \.\.\.market_conditions\.memory\.incident_cache import IncidentCache\n',
            '',
            content
        )
        content = re.sub(
            r'from \.\.\.\.market_conditions\.memory\.incident_cache import IncidentCache\n',
            '',
            content
        )
        content = re.sub(
            r'from \.\.\.\.\.market_conditions\.memory\.incident_cache import IncidentCache\n',
            '',
            content
        )
        
        # Fix class constructors
        content = re.sub(
            r'def __init__\(self, config: Dict\[str, Any\], logger: FailureAgentLogger, cache: IncidentCache\):',
            'def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):',
            content
        )
        
        # Remove cache references
        content = re.sub(
            r'self\.cache = cache\n',
            '',
            content
        )
        
        # Fix logger method calls
        content = re.sub(
            r'self\.logger\.log_issue\(',
            'self.logger.log_risk_assessment("issue", ',
            content
        )
        content = re.sub(
            r'self\.cache\.store_incident\(',
            '',
            content
        )
        
        # Add time import if needed
        if 'time.time()' in content and 'import time' not in content:
            content = re.sub(
                r'from typing import Dict, Any, List',
                'from typing import Dict, Any, List\nimport time',
                content
            )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed imports in {file_path}")
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

def main():
    """Main function to fix all risk_management imports."""
    risk_management_dir = Path("risk_management")
    
    if not risk_management_dir.exists():
        print("risk_management directory not found!")
        return
    
    # Find all Python files in risk_management
    python_files = list(risk_management_dir.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files to process")
    
    for file_path in python_files:
        if file_path.name != "__init__.py":  # Skip __init__.py for now
            fix_imports_in_file(file_path)
    
    print("Import fixes completed!")

if __name__ == "__main__":
    main()
