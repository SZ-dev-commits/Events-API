# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Disable bytecode generation and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose API port
EXPOSE 5000

# Start Flask application binding to all interfaces
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
