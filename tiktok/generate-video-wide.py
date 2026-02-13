#!/usr/bin/env python3
"""Widescreen (16:9) wrapper for generate-video-v4.py — for X/Twitter thread intros"""
import sys, os, json, importlib.util

# Load the v4 module despite the hyphenated filename
spec = importlib.util.spec_from_file_location("gen_v4", os.path.join(os.path.dirname(__file__), "generate-video-v4.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

# Override to 16:9 widescreen
gen.WIDTH = 1920
gen.HEIGHT = 1080

scripts_path = os.path.join(gen.TIKTOK_DIR, "video-scripts-wide.json")
if not os.path.exists(scripts_path):
    print("No video-scripts-wide.json found")
    sys.exit(1)

with open(scripts_path) as f:
    videos = json.load(f)

idx = int(sys.argv[1]) if len(sys.argv) > 1 else -1
if idx >= 0:
    if idx < len(videos):
        gen.generate_video(videos[idx])
    else:
        print(f"Index {idx} out of range ({len(videos)} videos)")
else:
    for v in videos:
        gen.generate_video(v)
