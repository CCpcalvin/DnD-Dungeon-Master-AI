FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the `requirements.txt`
COPY requirements.txt .

# Set environment variables
ENV DJANGO_DEBUG=1

# Install python library
RUN pip install --no-cache-dir -r requirements.txt

# To run the entrypoint.sh
RUN apt-get update && \
    apt-get install -y --no-install-recommends dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
