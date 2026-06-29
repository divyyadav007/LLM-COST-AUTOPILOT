# We use a slim Python wheel target matching our local environment version footprint cleanly
FROM python:3.13-slim

WORKDIR /workspace

# Install system utilities needed for building low-level binary extensions safely
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration matrices dependencies directly inside target workspace paths
COPY requirements.txt .

# Pre-compile multi-model binary libraries caching dependencies cleanly inside local layer hashes
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ports mapping both FastAPI gateway and visual telemetry analytics engines console
EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0"]