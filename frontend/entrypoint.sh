#!/bin/sh
set -e

cd /app/frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install 
fi

HOST=0.0.0.0 npm run dev
