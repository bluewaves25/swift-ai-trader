FROM python:3.13.3-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.src.server:app", "--bind", "0.0.0.0:3000"]