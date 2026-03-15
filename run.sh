#!/bin/bash

# AI Email Writer - Startup Script
# This script sets up and runs the AI Email Writer application

set -e

echo "🚀 AI Email Writer - Startup"
echo "============================="

# Check if Ollama is running
echo ""
echo "📡 Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running!"
else
    echo "⚠️  Ollama is not running on localhost:11434"
    echo ""
    echo "To start Ollama, open a new terminal and run:"
    echo "    ollama serve"
    echo ""
    echo "If you need to install Ollama, visit: https://ollama.ai"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Check Python version
echo ""
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version found"

# Install dependencies if needed
echo ""
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Create directories
mkdir -p uploads templates static

# Start the application
echo ""
echo "🎉 Starting AI Email Writer..."
echo ""
echo "═════════════════════════════════════════"
echo "📧 Application starting on http://localhost:8000"
echo "📡 Make sure Ollama is running (ollama serve)"
echo "🏥 Health check: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo "═════════════════════════════════════════"
echo ""

python3 app.py
