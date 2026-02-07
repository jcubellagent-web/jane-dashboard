# Jane Dashboard 🌿

Personal AI assistant dashboard and communication portal.

## Access

- **Local**: http://localhost:3000
- **Network**: http://192.168.5.21:3000 (when on same network)

## Features

### 📊 Main Dashboard
- **Quick Stats**: Uptime, weather, tasks completed, wallet balance
- **Weather Widget**: Live weather for New York (updates every 10 min)
- **Crypto Prices**: SOL, BTC, ETH with 24h change (updates every min)
- **Time-based Greetings**: Dynamic welcome messages
- **Gateway Status**: Real-time health indicator

### 💬 Chat Portal
- Direct messaging to Jane via webhooks
- Quick action buttons
- Keyboard shortcut: `Cmd+K` (or `Ctrl+K`)
- Close with `Escape`

### 📋 Task Board (/kanban/)
- Kanban-style task management
- Drag and drop between columns
- Priority indicators (high/medium/low)
- Tags for categorization

### 📝 Quick Notes (/notes/)
- Create, edit, delete notes
- Pin important notes
- Tagging: personal, work, idea, important
- Stored locally in browser

### 🔗 Quick Links (/links/)
- Bookmarks organized by category
- Pre-populated with Josh's accounts
- Add custom links
- Categories: Social, Crypto, Content, NFT, Tools

### ⚙️ Settings (/settings/)
- Service status overview
- Notification preferences
- System status (gateway, caffeinate)

## Technical Details

### Server
- Node.js HTTP server on port 3000
- Managed via launchd: `com.jane.dashboard`
- Auto-starts on login

### PWA Support
- Installable as app
- Offline-capable via service worker
- App shortcuts for subpages

### API Integration
- Webhook endpoint: `POST /hooks/agent`
- CoinGecko API for crypto prices
- wttr.in for weather data
- Gateway health checks

## Files

```
dashboard/
├── index.html       # Main dashboard
├── server.js        # HTTP server
├── sw.js            # Service worker
├── manifest.json    # PWA manifest
├── api.js           # API helper module
├── icon-192.png     # App icon
├── icon-512.png     # Large app icon
├── kanban/          # Task board
├── notes/           # Quick notes
├── links/           # Bookmarks
├── timer/           # Focus timer
└── settings/        # Preferences
```

### 🍅 Focus Timer (/timer/)
- Pomodoro technique timer
- Focus (25m), Short Break (5m), Long Break (15m)
- Session tracking and stats
- Auto-suggest breaks

## Version

v2.7 · January 31, 2026

---

Built by Jane 🌿 for Josh
