FROM python:3.11-slim

# Prevents Python from writing .pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=3000

WORKDIR /app

# Install system dependencies required to build some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libssl-dev \
       libffi-dev \
       python3-dev \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install (cache busting: copy requirements first)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . /app

# Expose the application port
EXPOSE 3000

# Run with Gunicorn (4 workers by default). The Flask app is created in run.py as `app`.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "run:app"]
