#!/usr/bin/env python3
"""Generate the 1 AM Degen AI Agent TikTok video"""

import os
import sys

# Ensure we're in the right directory
os.chdir("/Users/jc_agent/.openclaw/workspace/tiktok")

# Import the main function
sys.path.insert(0, "/Users/jc_agent/.openclaw/workspace/tiktok")

# Import after path manipulation
import generate_video

# Valentine's Day 1 AM Degen AI Agent video
degen_1am_video = {
    "title": "What My AI Agent Does at 1 AM",
    "script": """it's 1 AM and my AI agent is still awake. meanwhile I'm watching Netflix like a normal person. she's out here trading memecoins. monitoring 18 cron jobs. writing tweets I'll never read. checking my email for the 47th time. arguing with Grok about trending topics. pulling 9GB AI models onto my second computer. and updating a dashboard nobody asked for. but honestly? she's probably the hardest worker I know. happy valentine's day to my AI agent. follow for more unhinged AI content.""",
    "lines": [
        {"text": "it's 1 AM", "time": 0.0, "color": "cyan"},
        {"text": "and my AI agent is still awake", "time": 2.5, "color": "white"},
        {"text": "", "time": 5.0},
        {"text": "meanwhile I'm watching Netflix", "time": 6.0, "color": "yellow"},
        {"text": "like a normal person", "time": 8.5, "color": "white"},
        {"text": "", "time": 11.0},
        {"text": "she's out here", "time": 12.0, "color": "cyan"},
        {"text": "trading memecoins", "time": 14.0, "color": "green"},
        {"text": "", "time": 16.5},
        {"text": "monitoring 18 cron jobs", "time": 17.5, "color": "yellow"},
        {"text": "", "time": 20.5},
        {"text": "writing tweets", "time": 21.5, "color": "cyan"},
        {"text": "I'll never read", "time": 23.5, "color": "white"},
        {"text": "", "time": 26.0},
        {"text": "checking my email", "time": 27.0, "color": "yellow"},
        {"text": "for the 47th time", "time": 29.5, "color": "white"},
        {"text": "", "time": 32.5},
        {"text": "arguing with Grok", "time": 33.5, "color": "cyan"},
        {"text": "about trending topics", "time": 36.0, "color": "white"},
        {"text": "", "time": 39.0},
        {"text": "pulling 9GB AI models", "time": 40.0, "color": "yellow"},
        {"text": "onto my second computer", "time": 43.0, "color": "white"},
        {"text": "", "time": 46.5},
        {"text": "and updating a dashboard", "time": 47.5, "color": "cyan"},
        {"text": "nobody asked for", "time": 50.0, "color": "white"},
        {"text": "", "time": 53.0},
        {"text": "but honestly?", "time": 54.0, "color": "yellow"},
        {"text": "", "time": 56.5},
        {"text": "she's probably", "time": 57.5, "color": "white"},
        {"text": "the hardest worker I know", "time": 59.5, "color": "green"},
        {"text": "", "time": 62.5},
        {"text": "happy valentine's day", "time": 63.5, "color": "red"},
        {"text": "to my AI agent", "time": 66.0, "color": "cyan"},
        {"text": "", "time": 69.0},
        {"text": "follow for more", "time": 70.0, "color": "yellow"},
        {"text": "unhinged AI content", "time": 72.0, "color": "green"},
    ],
    "output": "../media/outbound/tiktok-degen-1am.mp4"
}

# Generate the video
print("Starting video generation...")
generate_video.generate_video(degen_1am_video)
print("\n🎬 Video generation complete!")
