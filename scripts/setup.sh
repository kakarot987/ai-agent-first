#!/bin/bash

# Setup script for AI Agent project
set -e

echo "🚀 Setting up AI Agent project..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
python.exe -m pip install --upgrade pip

# Install dependencies
if [ "$1" = "dev" ]; then
    echo "🛠️ Installing development dependencies..."
    pip install -r requirements-dev.txt
else
    echo "📚 Installing dependencies..."
    pip install -r requirements.txt
fi

# Install the package in development mode
echo "📋 Installing package in development mode..."
pip install -e .

# Create necessary directories
echo "📁 Creating directories..."
/usr/bin/mkdir -p conversations
/usr/bin/mkdir -p logs

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys"
fi

# Install pre-commit hooks if in dev mode
if [ "$1" = "dev" ]; then
    echo "🔗 Installing pre-commit hooks..."
    pre-commit install
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenAI API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: ai-agent chat"
echo ""
