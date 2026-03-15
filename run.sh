#!/bin/bash

# AI Email Writer - Startup Script
# This script sets up and runs the AI Email Writer application

set -e

echo "AI Email Writer - Startup"
echo "============================="

# Check if Docker is installed
echo ""
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker to proceed."
    exit 1
else
    echo "Docker is installed."
fi

# Check if Docker is running
echo ""
echo "Checking if Docker is running..."
if ! systemctl is-active --quiet docker; then
    echo "Docker is not running. Starting Docker..."
    sudo systemctl start docker
else
    echo "Docker is running."
fi

# Build and run Docker containers
echo ""
echo "Building and running Docker containers..."
docker-compose up --build -d

# Check if Ollama is running
echo ""
echo "Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Ollama is running!"
else
    ollama serve > /dev/null 2>&1 &
    echo "Ollama started."
fi

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python $python_version found"

# Install dependencies if needed
echo ""
echo "Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt
    echo "Dependencies installed"
else
    echo "Dependencies already installed"
fi

# Create directories
mkdir -p uploads templates static

# Start the application
echo ""
echo "Starting AI Email Writer..."
echo ""
echo "═════════════════════════════════════════"
echo "Application starting on http://localhost:8000"
echo "Make sure Ollama is running (ollama serve)"
echo "Health check: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "═════════════════════════════════════════"
echo ""

python3 app.py
