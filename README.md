# AI Agent

A simple, extensible AI agent built with OpenAI API and modern Python practices.

## Features

- 🤖 Conversational AI with memory
- 🔧 Multiple AI provider support
- 💾 Conversation persistence
- 🐳 Docker support
- 🧪 Comprehensive testing
- 📝 Rich logging and CLI

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone https://github.com/kakarot987/ai-agent-first.git
   cd ai-agent
   make setup

2. Configure environment:
    ```bash
    cp .env.example .env
    Edit .env with your API keys

3. Run the agent:
   ```bash
   make run
   or 
   python -m src.ai_agent.cli.main

## Installation

Using pip
bashpip install -e .
Using Docker
bashdocker-compose up
Usage
Command Line
bashai-agent chat
ai-agent --model gpt-4 --temperature 0.8
Python API
pythonfrom ai_agent import AIAgent

agent = AIAgent()
response = agent.chat("Hello, world!")
Development
Setup
bashmake setup-dev
Testing
bashmake test
make test-cov
Code Quality
bashmake lint
make format
Configuration
See .env.example for all configuration options.
Contributing

Fork the repository
Create a feature branch
Run tests and linting
Submit a pull request

License
MIT License