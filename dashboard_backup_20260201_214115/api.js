/**
 * Dashboard API Helper
 * Handles communication with OpenClaw Gateway
 */

const GATEWAY_URL = 'http://127.0.0.1:18789';
const GATEWAY_TOKEN = '47cf46ba8962b26d18a3d690d80a3e109f57e2525b8f6941';
const HOOK_TOKEN = '5c8d56dd45438059dddecbedb8a7123abaf72721153dc95d';

/**
 * Send a message to Jane via the webhook
 */
async function sendToJane(message, options = {}) {
    const response = await fetch(`${GATEWAY_URL}/hooks/agent`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${HOOK_TOKEN}`,
            'Content-Type': 'application/json'
        },
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
    const response = await fetch(`${GATEWAY_URL}/hooks/wake`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${HOOK_TOKEN}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text, mode })
    });

    if (!response.ok) {
        throw new Error(`Failed to wake: ${response.status}`);
    }

    return response.json();
}

/**
 * Get session history (requires gateway auth)
 */
async function getSessionHistory(sessionKey = 'agent:main:main', limit = 20) {
    const response = await fetch(`${GATEWAY_URL}/api/sessions/${encodeURIComponent(sessionKey)}/history?limit=${limit}`, {
        headers: {
            'Authorization': `Bearer ${GATEWAY_TOKEN}`
        }
    });

    if (!response.ok) {
        throw new Error(`Failed to get history: ${response.status}`);
    }

    return response.json();
}

/**
 * Get gateway status
 */
async function getGatewayStatus() {
    const response = await fetch(`${GATEWAY_URL}/api/status`, {
        headers: {
            'Authorization': `Bearer ${GATEWAY_TOKEN}`
        }
    });

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
        getGatewayStatus,
        GATEWAY_URL,
        GATEWAY_TOKEN,
        HOOK_TOKEN
    };
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sendToJane,
        wakeJane,
        getSessionHistory,
        getGatewayStatus,
        GATEWAY_URL,
        GATEWAY_TOKEN,
        HOOK_TOKEN
    };
}
