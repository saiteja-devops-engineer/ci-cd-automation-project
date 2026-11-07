# ==========================================
# Stage 1: Build virtual environment & gather shared libs
# ==========================================
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pinned dependencies from flask_app/
COPY flask_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and templates into /app
COPY flask_app/templates/ ./templates/
COPY flask_app/app.py .

# Stage required system libraries (zlib & OpenSSL) for Python C-extensions
RUN mkdir -p /deps && \
    cp -d /lib/x86_64-linux-gnu/libz.so.1* /deps/ && \
    cp -d /usr/lib/x86_64-linux-gnu/libssl.so.3* /deps/ && \
    cp -d /usr/lib/x86_64-linux-gnu/libcrypto.so.3* /deps/

# ==========================================
# Stage 2: Distroless minimal runtime
# ==========================================
FROM gcr.io/distroless/cc-debian12:latest

WORKDIR /app

# 1. Copy dynamic libraries (libz, libssl, libcrypto)
COPY --from=builder /deps/ /lib/x86_64-linux-gnu/

# 2. Copy Python runtime binaries
COPY --from=builder /usr/local /usr/local

# 3. Copy virtual environment
COPY --from=builder /opt/venv /opt/venv

# 4. Copy application source files
COPY --from=builder /app /app

# Configure runtime paths
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH" \
    PYTHONPATH="/opt/venv/lib/python3.12/site-packages" \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# Exec array notation (distroless has no shell)
CMD ["/opt/venv/bin/python", "app.py"]