# ==========================================
# Stage 1: Build virtual environment
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pinned dependencies from flask_app/
COPY flask_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and templates from flask_app/
COPY flask_app/templates/ ./templates/
COPY flask_app/app.py .

# ==========================================
# Stage 2: Distroless minimal runtime
# ==========================================
FROM gcr.io/distroless/cc-debian12:latest

WORKDIR /app

# Copy Python binaries and shared C runtime libraries
COPY --from=builder /usr/local /usr/local

# Copy the prepared virtual environment
COPY --from=builder /opt/venv /opt/venv

# Copy application source files
COPY --from=builder /app /app

# Configure execution environment
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH" \
    PYTHONPATH="/opt/venv/lib/python3.12/site-packages" \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# Exec array notation (distroless has no shell)
CMD ["/opt/venv/bin/python", "app.py"]