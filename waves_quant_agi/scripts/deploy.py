# scripts/deploy.py

import os
import subprocess

def deploy_backend():
    """Run Docker Compose to deploy the backend."""
    try:
        print("🚀 Starting deployment via Docker...")
        subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)
        print("✅ Deployment successful.")
    except subprocess.CalledProcessError:
        print("❌ Deployment failed. Please check your Docker setup.")

def migrate_database():
    """Optional DB migrations (if using Alembic or similar)."""
    # Placeholder for migration command if needed
    pass

if __name__ == "__main__":
    deploy_backend()
