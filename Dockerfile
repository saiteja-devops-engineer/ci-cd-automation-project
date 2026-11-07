FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly
RUN pip install --no-cache-dir flask requests pytz

# Copy application files
COPY templates/ ./templates/
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]