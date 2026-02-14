#!/bin/bash
# TikTok Upload via Android Emulator (adb)
# Usage: ./tiktok-upload.sh <video_path> "<caption>" ["#tag1 #tag2 ..."] [dry]
#
# Caption: plain text only (no emojis — adb can't type them)
# Hashtags: pass as "#ai #tech #fyp" — uses TikTok's Hashtag button for proper linking

set -e

ADB="$HOME/Library/Android/sdk/platform-tools/adb"
VIDEO_PATH="$1"
CAPTION="$2"
HASHTAGS="${3:-}"
DRY_RUN="${4:-}"

if [ -z "$VIDEO_PATH" ] || [ -z "$CAPTION" ]; then
    echo "Usage: $0 <video_path> \"<caption>\" [\"#tag1 #tag2\"] [dry]"
    exit 1
fi

[ ! -f "$VIDEO_PATH" ] && echo "ERROR: Video not found: $VIDEO_PATH" && exit 1

# Check emulator
if ! $ADB devices 2>/dev/null | grep -q "emulator"; then
    echo "ERROR: No emulator running"
    exit 1
fi

screenshot() { $ADB exec-out screencap -p > "/tmp/tiktok-step-$1.png" 2>/dev/null; }

# Type caption using adb input text (spaces encoded as %s, no special chars)
type_caption() {
    local text="$1"
    # Clean: replace spaces with %s, strip non-ASCII and problematic chars
    local encoded=$(python3 -c "
import sys
t = sys.argv[1]
out = ''
for c in t:
    if c == ' ': out += '%s'
    elif c.isalnum() or c in '.,!?-_+:;/': out += c
    # Skip emojis, #, @, and other problematic chars
print(out)
" "$text")
    $ADB shell input text "$encoded"
}

echo "📱 Step 1: Pushing video to emulator..."
REMOTE_PATH="/sdcard/DCIM/upload_video.mp4"
$ADB push "$VIDEO_PATH" "$REMOTE_PATH"
$ADB shell "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://$REMOTE_PATH" > /dev/null
sleep 2

echo "📱 Step 2: Opening TikTok..."
$ADB shell am start -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.splash.SplashActivity > /dev/null 2>&1
sleep 3

echo "📱 Step 3: Tapping Create..."
$ADB shell input tap 540 2272
sleep 3

# Handle permission dialogs
SCREEN=$($ADB shell uiautomator dump /sdcard/_ui.xml 2>&1 && $ADB shell cat /sdcard/_ui.xml)
if echo "$SCREEN" | grep -qi "Allow\|permission"; then
    echo "📱 Granting permissions..."
    $ADB shell input tap 540 1200
    sleep 2
fi

echo "📱 Step 4: Tapping gallery/upload..."
$ADB shell input tap 89 2225
sleep 3

echo "📱 Step 5: Selecting Videos tab..."
$ADB shell input tap 381 313
sleep 1

echo "📱 Step 6: Selecting first video..."
$ADB shell input tap 182 555
sleep 2

echo "📱 Step 7: Tapping Next (gallery)..."
$ADB shell input tap 794 2237
sleep 5

echo "📱 Step 8: Tapping Next (editor)..."
$ADB shell input tap 796 2181
sleep 5

echo "📱 Step 9: Entering caption..."
screenshot "pre-caption"

# Tap description field: [42,266][673,673]
$ADB shell input tap 357 469
sleep 1

# Type caption (clean text only)
type_caption "$CAPTION"
sleep 0.5

# Dismiss keyboard before adding hashtags
$ADB shell input keyevent 4
sleep 1

# Add hashtags via TikTok's Hashtag button
if [ -n "$HASHTAGS" ]; then
    echo "📱 Step 10: Adding hashtags..."
    
    for tag in $HASHTAGS; do
        TAG_CLEAN=$(echo "$tag" | sed 's/^#//')
        [ -z "$TAG_CLEAN" ] && continue
        
        # Tap TikTok's "Hashtags" button: [42,715][289,799]
        $ADB shell input tap 165 757
        sleep 2
        
        # Type tag name (without #) in search
        $ADB shell input text "$TAG_CLEAN"
        sleep 2
        
        # Dump UI to find autocomplete suggestion
        $ADB shell uiautomator dump /sdcard/_ui_ht.xml 2>&1 > /dev/null
        AUTO_BOUNDS=$($ADB shell cat /sdcard/_ui_ht.xml | python3 -c "
import sys, re
xml = sys.stdin.read()
tag = '${TAG_CLEAN}'.lower()
best = None
for m in re.finditer(r'text=\"([^\"]*?)\"[^/]*bounds=\"\[(\d+),(\d+)\]\[(\d+),(\d+)\]\"', xml):
    text = m.group(1).lower().replace('#','').strip()
    x1,y1,x2,y2 = [int(x) for x in m.groups()[1:]]
    if tag in text and y1 > 200 and y1 < 1500:
        print(f'{(x1+x2)//2} {(y1+y2)//2}')
        break
" 2>/dev/null)
        
        if [ -n "$AUTO_BOUNDS" ]; then
            echo "  → Selecting #$TAG_CLEAN"
            $ADB shell input tap $AUTO_BOUNDS
        else
            # Fallback: tap first result row
            echo "  → Tapping first result for #$TAG_CLEAN"
            $ADB shell input tap 400 400
        fi
        sleep 1
    done
fi

# Dismiss keyboard
$ADB shell input keyevent 4
sleep 1

screenshot "pre-post"

if [ "$DRY_RUN" = "dry" ]; then
    echo "🏁 DRY RUN — stopping before Post. Screenshot at /tmp/tiktok-step-pre-post.png"
    exit 0
fi

echo "📱 Step 11: Tapping Post..."
# Post button: [550,2179][1048,2305]
$ADB shell input tap 799 2242
sleep 2

# Check for confirmation
$ADB shell uiautomator dump /sdcard/_ui_confirm.xml 2>&1 > /dev/null
if $ADB shell cat /sdcard/_ui_confirm.xml | grep -qi "upload\|posting\|processing"; then
    echo "✅ Upload started!"
fi

sleep 5
screenshot "post-result"
echo "✅ TikTok upload complete!"

$ADB shell rm -f "$REMOTE_PATH"
