FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend
EXPOSE 3000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.src.server:app", "--bind", "0.0.0.0:3000"]