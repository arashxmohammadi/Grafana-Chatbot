# Use local Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and wheel packages
COPY requirements.txt /app/
COPY pypacks/ /app/pypacks/

# Install dependencies from local wheel packages
RUN pip3 install --no-index --find-links=/app/pypacks/ -r requirements.txt

# Copy application code
COPY main.py /app/
COPY .env /app/

# Expose port
EXPOSE 8000

# Command to run the application in development mode with hot-reload
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]