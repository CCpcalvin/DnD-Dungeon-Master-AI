#!/bin/sh
set -e

cd /frontend

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Vite dev server
echo "Starting Vite dev server..."
npm run dev -- --host 0.0.0.0
