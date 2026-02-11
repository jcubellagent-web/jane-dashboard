/**
 * Dashboard API Helper
 * Handles communication with OpenClaw Gateway via server-side proxy
 * (Tokens are kept server-side — see /api/gateway/* endpoints in server.js)
 */

/**
 * Send a message to Jane via the server proxy
 */
async function sendToJane(message, options = {}) {
    const response = await fetch('/api/gateway/hook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            name: options.name || 'Dashboard',
            sessionKey: options.sessionKey || 'dashboard:main',
            deliver: options.deliver !== undefined ? options.deliver : true,
            channel: options.channel || 'whatsapp',
            ...options
        })
    });

    if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
    }

    return response.json();
}

/**
 * Wake Jane with a system event
 */
async function wakeJane(text, mode = 'now') {
    const response = await fetch('/api/gateway/wake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, mode })
    });

    if (!response.ok) {
        throw new Error(`Failed to wake: ${response.status}`);
    }

    return response.json();
}

/**
 * Get session history via server proxy
 */
async function getSessionHistory(sessionKey = 'agent:main:main', limit = 20) {
    const response = await fetch(`/api/gateway/sessions/${encodeURIComponent(sessionKey)}/history?limit=${limit}`);

    if (!response.ok) {
        throw new Error(`Failed to get history: ${response.status}`);
    }

    return response.json();
}

/**
 * Get gateway status via server proxy
 */
async function getGatewayStatus() {
    const response = await fetch('/api/gateway/status');

    if (!response.ok) {
        throw new Error(`Failed to get status: ${response.status}`);
    }

    return response.json();
}

// Export for use in browser
if (typeof window !== 'undefined') {
    window.JaneAPI = {
        sendToJane,
        wakeJane,
        getSessionHistory,
        getGatewayStatus
    };
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sendToJane,
        wakeJane,
        getSessionHistory,
        getGatewayStatus
    };
}
