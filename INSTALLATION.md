# 🚀 Möbius AI Assistant - Installation Guide

## Quick Start (Core Features Only)

To run the bot with basic features, install core dependencies:

```bash
# Method 1: Use the installation script (recommended)
chmod +x install_dependencies.sh
./install_dependencies.sh

# Method 2: Install manually
pip install python-telegram-bot[job-queue]>=21.0
pip install pytz>=2024.1
pip install python-dotenv>=1.0.0
pip install requests>=2.31.0
pip install aiohttp>=3.9.0
pip install cryptography>=42.0
pip install APScheduler>=3.10.0
```

## Full Installation (All Features)

For comprehensive features including portfolio management, advanced alerts, etc.:

```bash
pip install -r requirements.txt
```

## Common Issues & Solutions

### ❌ ModuleNotFoundError: No module named 'telegram'
**Solution:** Install python-telegram-bot
```bash
pip install python-telegram-bot[job-queue]>=21.0
```

### ❌ ModuleNotFoundError: No module named 'pytz'
**Solution:** Install pytz
```bash
pip install pytz>=2024.1
```

### ❌ etherscan-python version error
**Solution:** The requirements.txt has been fixed to use version 2.1.0

### ❌ Comprehensive features not available
**Solution:** Install all dependencies
```bash
pip install -r requirements.txt
```

## Environment Setup

1. Create a `.env` file with your bot token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

2. Run the bot:
```bash
python src/main.py
```

## Feature Availability

- **Core Features**: Work with basic installation
- **Comprehensive Features**: Require full installation
  - Portfolio Management (`/portfolio`)
  - Advanced Alerts (`/alerts`)
  - Natural Language Queries (`/ask`)
  - Social Trading (`/social`)
  - Advanced Research (`/research`)
  - Trading Strategies (`/strategy`)
  - Cross-Chain Analytics (`/multichain`)

## Troubleshooting

If you encounter import errors:

1. **Check Python version**: Requires Python 3.8+
2. **Install core dependencies first**: Use `./install_dependencies.sh`
3. **Check for typos**: Ensure `.env` file is properly configured
4. **Virtual environment**: Consider using a virtual environment

## Support

For issues, check the logs when running `python src/main.py` - the bot will show which features are available and which dependencies are missing.