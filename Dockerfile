# Dockerfile for running the Mesa "Bank Reserves" example

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first to leverage caching
COPY requirements.txt /app/requirements.txt

# Install any required system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies, pinning Mesa to a specific version
RUN pip install --no-cache-dir networkx -r requirements.txt

# Copy the rest of the code
COPY . /app

# Command to run the Mesa server explicitly via run.py
CMD ["python", "batch_run.py"]

