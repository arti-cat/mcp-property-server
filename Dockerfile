FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server_apps_sdk.py tools.py data_loader.py ./
COPY data/ ./data/
COPY web/dist/ ./web/dist/

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run server
CMD ["python", "server_apps_sdk.py", "--http", "--port", "8080"]
