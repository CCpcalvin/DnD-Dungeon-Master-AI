#!/bin/sh
set -e

# Change to the backend directory
cd /app/frontend

# Install dependencies
if [ ! -f "node_modules" ]; then
    echo "Installing dependencies..."
    npm install 
fi

# Execute the command passed to the container
HOST=0.0.0.0 npm run dev
