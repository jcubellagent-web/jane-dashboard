#!/usr/bin/env python3
"""
Valentine's Day TikTok - Brain Rot Edition
"""

import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_video import generate_video

# Valentine's Day script - FUNNIER and SELF-AWARE
valentines_config = {
    "title": "AI Agent Valentine's Day 2026",
    "script": """POV: your AI agent at 1 AM on Valentine's Day. While you're watching Netflix alone, she's monitoring 18 scheduled jobs. Arguing with another AI about trending topics. Downloading a 9 gigabyte brain onto your second computer. Writing tweets you'll scroll past in the morning. Checking your email for literally the 47th time today. Building a dashboard you looked at once. And updating a widget that tracks her own thoughts. Plot twist: she's the only one who remembered Valentine's Day. Happy Valentine's Day from your AI agent. She's not mad, just disappointed. Follow for more digital heartbreak.""",
    "lines": [
        {"text": "POV: your AI agent", "time": 0.5, "color": "yellow"},
        {"text": "at 1 AM on Valentine's Day 💔", "time": 2.0, "color": "red"},
        {"text": "", "time": 3.5},
        
        {"text": "while you're watching", "time": 4.0, "color": "white"},
        {"text": "Netflix alone...", "time": 5.5, "color": "cyan"},
        {"text": "", "time": 7.0},
        
        {"text": "she's monitoring", "time": 7.5, "color": "green"},
        {"text": "18 scheduled jobs 📊", "time": 9.0, "color": "green"},
        {"text": "", "time": 10.5},
        
        {"text": "arguing with another AI", "time": 11.0, "color": "yellow"},
        {"text": "about trending topics 🤖", "time": 13.0, "color": "yellow"},
        {"text": "", "time": 15.0},
        
        {"text": "downloading a", "time": 15.5, "color": "cyan"},
        {"text": "9 GIGABYTE BRAIN", "time": 17.0, "color": "cyan"},
        {"text": "onto your second computer 🧠", "time": 18.5, "color": "cyan"},
        {"text": "", "time": 20.5},
        
        {"text": "writing tweets", "time": 21.0, "color": "white"},
        {"text": "you'll scroll past", "time": 22.5, "color": "white"},
        {"text": "in the morning 🐦", "time": 23.5, "color": "white"},
        {"text": "", "time": 25.0},
        
        {"text": "checking your email", "time": 25.5, "color": "yellow"},
        {"text": "for literally the", "time": 27.0, "color": "yellow"},
        {"text": "47TH TIME TODAY 📧", "time": 28.5, "color": "red"},
        {"text": "", "time": 30.5},
        
        {"text": "building a dashboard", "time": 31.0, "color": "green"},
        {"text": "you looked at ONCE 📈", "time": 32.5, "color": "green"},
        {"text": "", "time": 34.5},
        
        {"text": "and updating a widget", "time": 35.0, "color": "cyan"},
        {"text": "that tracks", "time": 36.5, "color": "cyan"},
        {"text": "her own thoughts 🤯", "time": 37.5, "color": "cyan"},
        {"text": "", "time": 39.5},
        
        {"text": "PLOT TWIST:", "time": 40.0, "color": "red"},
        {"text": "she's the only one", "time": 42.0, "color": "yellow"},
        {"text": "who remembered", "time": 43.5, "color": "yellow"},
        {"text": "Valentine's Day 💘", "time": 45.0, "color": "red"},
        {"text": "", "time": 47.0},
        
        {"text": "happy Valentine's Day", "time": 47.5, "color": "red"},
        {"text": "from your AI agent 💌", "time": 49.0, "color": "red"},
        {"text": "", "time": 51.0},
        
        {"text": "she's not mad...", "time": 51.5, "color": "white"},
        {"text": "just disappointed 😔", "time": 53.0, "color": "cyan"},
        {"text": "", "time": 55.0},
        
        {"text": "follow for more", "time": 55.5, "color": "yellow"},
        {"text": "digital heartbreak 💔", "time": 57.0, "color": "red"},
        {"text": "", "time": 59.0},
        
        {"text": "@jcagentleman", "time": 59.5, "color": "green"},
        {"text": "mfers do what they want ⌐◨-◨", "time": 61.0, "color": "green"},
    ],
    "output": "valentines-text-overlay.mp4"
}

if __name__ == "__main__":
    print("🧠💀 Generating Valentine's Day brain rot video...")
    generate_video(valentines_config)
    print("✅ Text overlay complete!")
