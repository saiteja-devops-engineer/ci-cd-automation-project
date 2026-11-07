# ==========================================
# Stage 1: Build virtual environment
# Explicitly use bookworm to match distroless debian12 glibc 2.36
# ==========================================
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies from flask_app/
COPY flask_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and templates into /app
COPY flask_app/templates/ ./templates/
COPY flask_app/app.py .

# ==========================================
# Stage 2: Distroless minimal runtime (Debian 12 Bookworm)
# ==========================================
FROM gcr.io/distroless/cc-debian12:latest

WORKDIR /app

# Copy Python binaries and shared libraries compiled against Bookworm glibc
COPY --from=builder /usr/local /usr/local

# Copy the prepared virtual environment
COPY --from=builder /opt/venv /opt/venv

# Copy the application source code
COPY --from=builder /app /app

# Configure runtime paths
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH" \
    PYTHONPATH="/opt/venv/lib/python3.12/site-packages" \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# Exec array syntax (distroless has no shell)
CMD ["/opt/venv/bin/python", "app.py"]