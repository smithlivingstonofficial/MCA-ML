# ==========================================
# Backend Production Containerfile
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.162.4 \
    uvicorn[standard]==0.54.0 \
    pydantic==2.14.3 \
    sqlalchemy==2.1.8 \
    scipy==1.18.1 \
    pandas==3.1.1 \
    numpy==2.5.4 \
    scikit-learn==1.9.1 \
    PuLP==4.2.0 \
    highspy==1.16.0 \
    shap==0.54.1 \
    httpx==0.28.1 \
    pytest==9.2.0

# Copy application source
COPY backend /app/backend
COPY data /app/data
COPY hospital.db /app/hospital.db
COPY run_platform.py /app/run_platform.py

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
