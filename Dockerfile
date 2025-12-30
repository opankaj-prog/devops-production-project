# 1. Base image
FROM python:3.12-slim

# WHY: curl is needed for HEALTHCHECK
RUN apt-get update \
 && apt-get install -y curl \
 && rm -rf /var/lib/apt/lists/*

# 2. Set working directory
WORKDIR /app

# 3. Copy dependency file first (layer caching)
COPY app/requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY app/ .

# 6. Expose application port
EXPOSE 5000

# 7. Health check
HEALTHCHECK CMD curl --fail http://localhost:5000/health || exit 1

# 8. Run application
CMD ["python", "app.py"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
