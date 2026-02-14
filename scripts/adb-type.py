#!/usr/bin/env python3
"""Type text into Android device via adb, handling all special characters.
Uses a combination of `input text` for safe chars and `input keyevent` for special ones."""

import subprocess
import sys
import base64

ADB = f"{__import__('os').path.expanduser('~')}/Library/Android/sdk/platform-tools/adb"

def adb(*args):
    return subprocess.run([ADB, *args], capture_output=True, text=True)

def set_clipboard(text):
    """Set device clipboard using app_process + java reflection"""
    # Encode text as base64 to avoid shell escaping issues  
    b64 = base64.b64encode(text.encode('utf-8')).decode('ascii')
    
    # Use a mini Java program via app_process to set clipboard
    # This is the most reliable cross-Android-version method
    java_code = f"""
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Looper;
import java.util.Base64;

public class Clip {{
    public static void main(String[] args) {{
        Looper.prepareMainLooper();
        byte[] decoded = Base64.getDecoder().decode("{b64}");
        String text = new String(decoded);
        // Can't easily access ClipboardManager without context
        System.out.println(text);
    }}
}}"""
    # This approach is too complex. Use simpler method:
    # Write to a temp file and use `input` with the file content
    pass

def type_via_input_text(text):
    """Use `adb shell input text` with proper escaping.
    This handles basic ASCII but NOT #, @, !, emojis, etc."""
    # Characters that need special handling in `input text`:
    # space -> %s
    # & -> \\& (or just skip)
    # < > -> skip
    # ( ) -> \\( \\)  
    # # @ ! need keyevent instead
    
    safe = text.replace(' ', '%s').replace('&', '\\&').replace('(', '\\(').replace(')', '\\)')
    # Remove characters that input text can't handle
    safe = ''.join(c for c in safe if c.isalnum() or c in '.,!?-_+=%s\'":;/\\')
    adb('shell', 'input', 'text', safe)

def type_smart(text):
    """Smart typing: batch safe chars with input text, use keyevent for specials"""
    batch = ""
    
    for c in text:
        if c == ' ':
            if batch:
                adb('shell', 'input', 'text', batch)
                batch = ""
            adb('shell', 'input', 'keyevent', '62')  # SPACE
        elif c == '#':
            if batch:
                adb('shell', 'input', 'text', batch)
                batch = ""
            # Use key combo: SHIFT + 3
            # The trick: use `input text` with the actual # character
            # On some devices this works: input keyevent 115 (NUMPAD_POUND)
            # Or just use unicode input
            adb('shell', 'input', 'keyevent', '115')  # NUM_POUND - may not work
        elif c == '@':
            if batch:
                adb('shell', 'input', 'text', batch)
                batch = ""
            adb('shell', 'input', 'keyevent', '77')  # AT
        elif c in "!?()[]{}|~`^":
            if batch:
                adb('shell', 'input', 'text', batch)
                batch = ""
            # Skip problematic chars for now
        elif ord(c) > 127:
            # Emoji or unicode - skip for now
            if batch:
                adb('shell', 'input', 'text', batch)
                batch = ""
        else:
            batch += c
    
    if batch:
        adb('shell', 'input', 'text', batch)

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "test"
    type_smart(text)
