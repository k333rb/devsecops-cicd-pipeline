# Slim base: smaller image, smaller attack surface for the security scan
FROM python:3.12-slim

WORKDIR /app

# Applies any security patches Debian has published, even ones not yet
# baked into the official python:3.12-slim image itself
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install deps before copying app code so Docker caches this layer
# and doesn't reinstall on every code change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Run as non-root, limits blast radius if the container is ever compromised
RUN useradd -m appuser
USER appuser

# Documents the app's port; actual publishing happens at `docker run -p`
EXPOSE 5000

CMD ["python", "app.py"]