########################
# Stage 1: Builder
########################
FROM python:3.11-slim AS builder

# Work inside /app
WORKDIR /app

# Copy only requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


########################
# Stage 2: Runtime
########################
FROM python:3.11-slim AS runtime

# Set timezone to UTC (important for TOTP & cron)
ENV TZ=UTC

# Work inside /app
WORKDIR /app

ENV PYTHONPATH="/app"


# Install system dependencies: cron + tzdata
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime && echo "Etc/UTC" > /etc/timezone

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your application code into the image
COPY . /app

# Copy cron configuration file into cron.d
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Set correct permissions and register cron job
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron

# Create volume mount points for seed & cron output
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose API port
EXPOSE 8080

# Start cron service AND FastAPI app when container starts
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
