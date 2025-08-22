#!/bin/bash

# Online Python Compiler Setup Script

echo "🐍 Setting up Online Python Compiler with LLM Integration..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -e .

# Install aiohttp if not already installed
echo "🌐 Installing aiohttp for HTTP requests..."
pip install aiohttp>=3.8.0

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file and add your Perplexity API key"
fi

# Check if Docker is running
echo "🐳 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Pull Python Docker image
echo "🐳 Pulling Python Docker image..."
docker pull python:3.11-alpine

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Perplexity API key"
echo "2. Run: python main.py"
echo "3. Open: http://localhost:8888"
echo ""
echo "Features:"
echo "- 🔍 Analyze: Check code for security issues and get suggestions"
echo "- ▶️ Run Code: Execute code in a secure Docker container"
echo "- 🧠 Smart Run: Analyze code first, then run if safe"
