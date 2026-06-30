# We use a slim Python wheel target matching our local environment version footprint cleanly
FROM python:3.13-slim

WORKDIR /workspace

# Install system utilities needed for building low-level binary extensions safely, and nginx
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration matrices dependencies directly inside target workspace paths
COPY requirements.txt .

# Pre-compile multi-model binary libraries caching dependencies cleanly inside local layer hashes
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose ports mapping the reverse proxy gateway
EXPOSE 8080

CMD ["python", "entrypoint.py"]