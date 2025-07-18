#!/usr/bin/env python3
"""
Waifu/Husbando Collector Bot
Entry point for the Telegram bot
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main function from src
from main import main

if __name__ == "__main__":
    main()