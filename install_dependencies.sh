#!/bin/bash
# Install core dependencies first to avoid import errors

echo "🚀 Installing core dependencies for Möbius AI Assistant..."

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install python-telegram-bot[job-queue]>=21.0
pip install pytz>=2024.1
pip install python-dotenv>=1.0.0
pip install requests>=2.31.0
pip install aiohttp>=3.9.0
pip install cryptography>=42.0
pip install APScheduler>=3.10.0

echo "📦 Installing AI dependencies..."
pip install groq>=0.9.0
pip install openai>=1.14.0
pip install google-generativeai>=0.5.0
pip install anthropic>=0.25.0

echo "📦 Installing utility dependencies..."
pip install beautifulsoup4>=4.12.0
pip install PyMuPDF>=1.24.0
pip install web3>=6.15.0
pip install prometheus-client>=0.19.0
pip install psutil>=5.9.0
pip install matplotlib>=3.8.0
pip install pillow>=10.0.0
pip install numpy>=1.24.0

echo "✅ Core dependencies installed! You can now run the bot with: python src/main.py"
echo "💡 To install all comprehensive features, run: pip install -r requirements.txt"