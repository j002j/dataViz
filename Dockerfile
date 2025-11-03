# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install any needed system dependencies (like for OpenCV)
# --- THIS IS THE FIX ---
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*
# --- END FIX ---

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the Python path to include the root directory
ENV PYTHONPATH="/app"

# Default command (can be overridden in docker-compose.yml)
CMD ["python"]