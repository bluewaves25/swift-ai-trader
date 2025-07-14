# Dockerfile

# Multi-stage build for Python 3.13.3 (Core) + Python 3.10.3 (ML)
FROM python:3.13.3-slim as core

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ \
    libpq-dev \
    libta-lib-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
