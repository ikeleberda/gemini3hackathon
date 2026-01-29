# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add Flask for HTTP endpoint
RUN pip install --no-cache-dir flask gunicorn

# Copy application code
COPY main.py .
COPY src/ ./src/
COPY pihrate-hub-c8f3s-1c07e5d73634.json .

# Copy the Flask wrapper
COPY app.py .

# Create directory for generated assets
RUN mkdir -p /app/generated_assets

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/pihrate-hub-c8f3s-1c07e5d73634.json

# Expose port 8080 (Cloud Run requirement)
EXPOSE 8080

# Run with gunicorn for production
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 900 app:app
