FROM node:24-slim

# Set working directory
WORKDIR /app

# Set up entrypoint.sh
RUN apt-get update && \
    apt-get install -y --no-install-recommends dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
