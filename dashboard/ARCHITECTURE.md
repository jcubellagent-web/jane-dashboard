# Mobile Dashboard Architecture v2

## Overview

This document outlines the architecture for Josh's mobile dashboard, designed for:
- **Minimalist, sleek design** - Dark theme, data-dense but not cluttered
- **Progressive disclosure** - More data one tap away
- **Native-feeling interactions** - Smooth animations, responsive touch
- **Resilient data loading** - Graceful error handling, offline-ready patterns

---

## Current Dashboard Audit (mobile.html v7.9)

### What Works Well ✅
1. **Dark theme colors** - `#0a0f1a` background with accent greens/blues looks premium
2. **Card-based layout** - Clean section separation
3. **Widget refresh buttons** - Individual refresh per section
4. **Bubble map for "What I Know"** - Visual, interactive
5. **Floating chat FAB** - Accessible, discoverable
6. **Safe area handling** - Proper viewport-fit=cover for notch devices

### Architectural Issues ❌

#### 1. No Loading States
- Data appears suddenly when it loads
- No skeleton screens or spinners
- User doesn't know if data is stale or loading

#### 2. Poor Error Handling
- Errors silently fail
- No user feedback on network issues
- No retry mechanisms

#### 3. Race Conditions
- All data fetches fire simultaneously at load
- No coordination or prioritization
- Critical data (PENGUIN balance) loads same time as low-priority data

#### 4. Monolithic Structure
- 1800+ lines in single file
- CSS, HTML, and JS all mixed
- Hard to maintain and debug

#### 5. No Caching Strategy
- Every refresh hits the network
- No stale-while-revalidate
- No localStorage fallback

#### 6. Hardcoded Data
- Bubble map knowledge is hardcoded in HTML
- Should be data-driven from API

#### 7. Inconsistent Patterns
- Some functions use async/await, others use callbacks
- fetchTasks() references non-existent elements (rag-dots)
- Duplicate refresh intervals (jane-status called twice)

#### 8. WebSocket Fragility
- Basic reconnection (3s timeout)
- No exponential backoff
- No heartbeat/keepalive

---

## New Architecture (v2)

### Design Principles

1. **Progressive Enhancement**
   - Core content loads first (PENGUIN!)
   - Secondary data loads after
   - Graceful degradation when APIs fail

2. **Data Layer Abstraction**
   - Clean API class with retry logic
   - Request deduplication
   - Response caching with TTL

3. **State Management**
   - Centralized widget state
   - Loading/error/data states per widget
   - Timestamp tracking for freshness

4. **Component Model**
   - Each widget is self-contained
   - Consistent render pattern
   - Easy to add/remove widgets

### Data Priority Tiers

| Priority | Widget | Refresh | Why |
|----------|--------|---------|-----|
| 🔥 Critical | PENGUIN Tracker | 30s | "All hail the penguin" - Main focus |
| 🔥 Critical | Jane Status | 30s | Need to know she's working |
| ⚡ High | Prediction Markets | 2min | Timely odds matter |
| ⚡ High | Mac Mini Status | 1min | Infrastructure health |
| 📊 Normal | TikTok Metrics | 5min | Less urgent |
| 📊 Normal | Bubble Map | 5min | Static-ish content |
| 📊 Normal | Completed Tasks | 2min | Historical, less urgent |

### API Layer Design

```javascript
class API {
  // Configuration
  static BASE_URL = window.location.origin;
  static cache = new Map();
  static inflight = new Map();
  
  // Request with retry, deduplication, caching
  static async fetch(endpoint, options = {}) {
    const {
      cacheTTL = 0,       // Cache duration in ms (0 = no cache)
      retries = 2,        // Number of retry attempts
      timeout = 5000,     // Request timeout
      priority = 'auto'   // 'high' | 'low' | 'auto'
    } = options;
    
    // Check cache first
    if (cacheTTL > 0) {
      const cached = this.cache.get(endpoint);
      if (cached && Date.now() - cached.timestamp < cacheTTL) {
        return cached.data;
      }
    }
    
    // Deduplicate in-flight requests
    if (this.inflight.has(endpoint)) {
      return this.inflight.get(endpoint);
    }
    
    // Create request with retry logic
    const request = this._fetchWithRetry(endpoint, retries, timeout);
    this.inflight.set(endpoint, request);
    
    try {
      const data = await request;
      // Cache successful response
      if (cacheTTL > 0) {
        this.cache.set(endpoint, { data, timestamp: Date.now() });
      }
      return data;
    } finally {
      this.inflight.delete(endpoint);
    }
  }
}
```

### Widget State Model

```javascript
const WidgetState = {
  penguin: {
    data: null,
    loading: false,
    error: null,
    lastUpdated: null
  },
  // ... other widgets
};

function updateWidget(name, updates) {
  Object.assign(WidgetState[name], updates);
  renderWidget(name);
}
```

### Loading States (Skeleton Screens)

Each widget shows a skeleton while loading:
- Pulsing gray bars for text
- Subtle animation to indicate activity
- Same dimensions as real content (no layout shift)

### Error States

Three error levels:
1. **Soft fail** - Show cached data with "stale" indicator
2. **Retry available** - Show error with retry button
3. **Critical fail** - Show fallback content

### Responsive Layout

```
Mobile (< 430px):
┌─────────────────┐
│ 🐧 PENGUIN      │  ← Hero widget, always visible
├─────────────────┤
│ 🦾 Jane Status  │
├─────────────────┤
│ 📊 Markets      │
├─────────────────┤
│ 🧠 What I Know  │
└─────────────────┘
```

---

## Implementation Notes

### File Structure
- `mobile-v2.html` - Single file for simplicity (inline CSS/JS)
- No build step required
- ~1000 lines target (down from 1800)

### Critical Path
1. Render shell immediately (no blocking resources)
2. Fetch PENGUIN balance first (hero metric)
3. Parallel fetch remaining data
4. WebSocket for real-time updates

### Performance Targets
- First paint: < 100ms
- First meaningful content: < 500ms
- Full load: < 2s on 3G

### Accessibility
- Touch targets: 48px minimum
- Color contrast: 4.5:1 ratio
- Focus indicators for keyboard nav

---

## Changelog

### v2.0 (February 3, 2026)
- Complete rewrite with proper architecture
- Added skeleton loading states for all widgets
- Added retry logic with exponential backoff (3 retries)
- Added request caching and deduplication via API class
- Merged Jane + Tasks + Agents + Cron into unified widget
- PENGUIN tracker as hero widget (loads first, updates every 30s)
- Improved prediction markets with category grouping
- Better error handling with fallback states
- WebSocket reconnection with 5s backoff
- Reduced code from ~1870 lines to ~1100 lines (~40% reduction)
- Improved animations (fade-in, shimmer skeletons)
- Touch-optimized (48px targets, tap feedback)
- Safe area handling for notched devices

### Technical Improvements
- API layer with deduplication prevents duplicate requests
- Cached responses with configurable TTL per endpoint
- Priority loading: PENGUIN → Rest (100ms stagger)
- State management pattern for widget data
- Clean separation: API → State → Render

### Files
- `mobile-v2.html` - New dashboard (self-contained)
- `mobile.html` - Legacy (kept for comparison)
- `server.js` - Unchanged, same API endpoints
- `ARCHITECTURE.md` - This file

### Access URLs
- Local: http://localhost:3000/mobile-v2.html
- Tunnel: https://newfoundland-tracking-deserve-intermediate.trycloudflare.com/mobile-v2.html

---

*Built with 💚 by Jane while Josh sleeps @ 12:45 AM EST*
