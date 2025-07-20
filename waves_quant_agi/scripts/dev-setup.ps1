# Dev Setup Script for Swift AI Trader
# This script sets up both Python environments and installs all requirements for backend-main and backend-ml

# Set up env_main (Python 3.12)
Write-Host "Activating env_main and installing requirements..."
.\env_main\Scripts\activate
pip install -r backend-main/requirements.txt
Deactivate

# Set up env_310 (Python 3.10)
Write-Host "Activating env_310 and installing requirements..."
.\env_310\Scripts\activate
pip install -r backend-ml/requirements.txt
Deactivate

Write-Host "All environments and dependencies are set up." 