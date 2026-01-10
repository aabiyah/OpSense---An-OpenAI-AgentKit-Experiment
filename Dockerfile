# Multi-stage build for OpSense
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY run_opsense.py .
COPY ops_agents/ ./ops_agents/
COPY tools/ ./tools/
COPY data/ ./data/

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "run_opsense.py"]
