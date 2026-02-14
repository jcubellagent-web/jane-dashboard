# TikTok Upload Automation - CDP Injection Findings

**Date:** 2026-02-13  
**Approach:** CDP (Chrome DevTools Protocol) file injection via React onChange hack

## Summary
❌ **CDP injection did NOT work for TikTok Studio uploads**

## What Worked
✅ Successfully connected to browser via CDP  
✅ Found file input element: `input[type="file"]` with `accept="video/*"`  
✅ Detected React Fiber key: `__reactFiber$evp518et7dv`  
✅ Injected video file as base64 (tested with 2.9MB mp4)  
✅ Created File blob and DataTransfer object successfully  
✅ Triggered React Fiber onChange handler - **returned SUCCESS**  

## What DIDN'T Work
❌ Upload process never started despite onChange being triggered  
❌ Page remained in "Select video to upload" state  
❌ No upload progress indicator appeared  
❌ No network requests for video upload initiated  

## Technical Details

### File Input Structure
- Element: `document.querySelector('input[type="file"]')`
- React integration: Uses React Fiber (`__reactFiber$...`)
- Accept: `video/*`
- Multiple: `false`

### Injection Script
Created `scripts/tiktok-upload-inject.js` modeled after `scripts/x-image-inject.js`:
- Connects via CDP WebSocket endpoint
- Reads video as base64
- Creates File blob from base64 data
- Assigns to input.files via DataTransfer
- Searches React Fiber tree for onChange handlers (up to 30 levels deep)
- Triggers React's synthetic event

### Why It Failed
TikTok Studio likely has one or more anti-automation measures:

1. **Event validation** - Checks if the onChange event originated from a real user interaction
2. **Trusted events only** - May require `isTrusted: true` flag (can't be spoofed in JS)
3. **Additional validation** - Could be checking for mouse/keyboard events before file selection
4. **Custom upload flow** - May not rely solely on standard file input onChange
5. **Security headers/fingerprinting** - Could be detecting automated behavior

### Comparison with X/Twitter
The same CDP approach WORKS for X because:
- X's React onChange handler doesn't validate event origin
- X accepts programmatically created synthetic events
- No additional security checks on file input

TikTok has stricter validation, likely because:
- They're dealing with video uploads (larger security concern)
- More sophisticated anti-bot/anti-automation
- Newer codebase with modern security practices

## Script Location
- **Inject script:** `scripts/tiktok-upload-inject.js`
- **Reference script:** `scripts/x-image-inject.js`
- **Browser lock:** `scripts/browser-lock.sh`

## Next Steps (per task requirements)
Since CDP injection doesn't work, alternatives:
1. **Android emulator** - Use ADB to upload via TikTok mobile app (mentioned in task)
2. **Playwright native upload** - Try Playwright's setInputFiles (likely also won't work)
3. **Browser extension** - Create Chrome extension with elevated permissions
4. **API approach** - Check if TikTok has official Creator API for uploads
5. **Selenium with real clicks** - Use actual mouse automation to click "Select video"

## Recommendation
**Try Android emulator next** as suggested in the task. The TikTok mobile app likely has fewer anti-automation measures for file selection since it uses native Android file pickers.

## Files Created
- `scripts/tiktok-upload-inject.js` - CDP injection script (6.5KB)
- `tiktok/CDP_INJECTION_FINDINGS.md` - This document

## Test Run Output
```
Connected. 1 contexts found.
Using page: https://www.tiktok.com/tiktokstudio/upload
Video: base.mp4, 2902834 bytes, base64: 3870448 chars
Injecting video file...
File injection result: SUCCESS: fiber-onChange triggered at depth 0, file size=2902834
Waiting for upload to process...
Upload automation complete. Review and click Post manually or extend script.
```

Despite "SUCCESS", no upload actually started.
