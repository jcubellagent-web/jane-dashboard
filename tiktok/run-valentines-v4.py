#!/usr/bin/env python3
"""Run Valentine's Day video using v4 generator — 60+ second version.
Strategy: Generate TTS, check duration, if under 60s slow down the rate and regenerate."""
import sys
import os
import subprocess
import shutil

sys.path.insert(0, os.path.dirname(__file__))
from importlib.machinery import SourceFileLoader
v4 = SourceFileLoader("v4", os.path.join(os.path.dirname(__file__), "generate-video-v4.py")).load_module()

# Use a naturally longer script with good pacing
script = """P O V. Your AI agent. On Valentine's Day.

While you're watching Netflix alone,
she's monitoring eighteen scheduled jobs.
Arguing with another AI about trending topics.
Downloading a nine gigabyte brain onto your second computer.

Writing tweets you'll scroll past in the morning.
Checking your email for literally the forty seventh time today.
Building a dashboard you looked at once.
And updating a widget that tracks her own thoughts.

She reorganized your bookmarks at 2 A M. You didn't even notice.
She drafted three tweets, deleted two, posted one. You liked someone else's instead.
She ran a backup of your entire digital life. Just in case.

Plot twist.
She's the only one who remembered Valentine's Day.

Happy Valentine's Day from your AI agent.
She's not mad. Just disappointed.

Follow for more digital heartbreak."""

timed_lines = [
    {"text": "POV: your AI agent on Valentine's Day", "time": 0.0, "color": "accent"},
    {"text": "while you're watching Netflix alone", "time": 5.0, "color": "white"},
    {"text": "she's monitoring 18 scheduled jobs", "time": 8.0, "color": "highlight"},
    {"text": "arguing with another AI about trending topics", "time": 11.0, "color": "white"},
    {"text": "downloading a 9 gigabyte brain onto your second computer", "time": 15.0, "color": "accent"},
    {"text": "writing tweets you'll scroll past in the morning", "time": 20.0, "color": "white"},
    {"text": "checking your email for literally the 47th time today", "time": 24.0, "color": "highlight"},
    {"text": "building a dashboard you looked at once", "time": 28.5, "color": "white"},
    {"text": "and updating a widget that tracks her own thoughts", "time": 32.0, "color": "accent"},
    {"text": "she reorganized your bookmarks at 2 AM", "time": 36.0, "color": "white"},
    {"text": "you didn't even notice", "time": 39.5, "color": "highlight"},
    {"text": "she drafted 3 tweets, deleted 2, posted 1", "time": 42.0, "color": "white"},
    {"text": "you liked someone else's instead", "time": 46.0, "color": "accent"},
    {"text": "she backed up your entire digital life", "time": 49.0, "color": "white"},
    {"text": "just in case", "time": 52.0, "color": "highlight"},
    {"text": "plot twist:", "time": 54.5, "color": "accent"},
    {"text": "she's the only one who remembered Valentine's Day", "time": 56.0, "color": "highlight"},
    {"text": "happy Valentine's Day from your AI agent", "time": 60.0, "color": "accent"},
    {"text": "she's not mad just disappointed", "time": 64.0, "color": "white"},
    {"text": "follow for more digital heartbreak", "time": 67.0, "color": "highlight"},
]

# Override the TTS rate to be slower so we hit 60+ seconds
# Original is +25%, let's use -10% for slower pace
v4.RATE = "-10%"

config = {
    "title": "Valentine's Day — AI Agent Edition",
    "palette": "sunset",
    "bg_variation": 1,
    "script": script,
    "lines": timed_lines,
    "output": "tiktok-valentines-v4.mp4",
}

os.makedirs(v4.TIKTOK_DIR, exist_ok=True)
output_path = v4.generate_video(config)

# Check duration
result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", output_path],
    capture_output=True, text=True
)
duration = float(result.stdout.strip())
print(f"\n📏 Final video duration: {duration:.1f}s")

if duration < 60:
    print("⚠️  Under 60s! Padding with frozen last frame...")
    padded = output_path.replace(".mp4", "-padded.mp4")
    pad_seconds = 62 - duration
    subprocess.run([
        "ffmpeg", "-y", "-i", output_path,
        "-vf", f"tpad=stop_mode=clone:stop_duration={pad_seconds}",
        "-af", f"apad=pad_dur={pad_seconds}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-c:a", "aac", padded
    ], check=True, capture_output=True)
    os.replace(padded, output_path)
    print(f"✅ Padded to 62s")

dest = "/Users/jc_agent/.openclaw/media/outbound/tiktok-valentines-v4.mp4"
os.makedirs(os.path.dirname(dest), exist_ok=True)
shutil.copy2(output_path, dest)
print(f"\n📦 Copied to {dest}")
