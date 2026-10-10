const express = require('express');
const cookieParser = require('cookie-parser');
const { randomBytes, randomUUID, timingSafeEqual } = require('crypto');
const { URL } = require('url');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(express.json());
app.use(cookieParser());

// Rate limiting - Per-endpoint with sliding window
const createOrderLimiter = rateLimit({
    windowMs: 10 * 1000, // 10 second sliding window
    max: 100, // 100 requests per 10 seconds per IP
    message: 'Rate limit exceeded for order creation',
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req) => req.path === '/health'
});

const generalLimiter = rateLimit({
    windowMs: 10 * 1000, // 10 second window
    max: 200, // Higher limit for GET operations
    message: 'Rate limit exceeded',
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req) => req.path === '/health'
});

// Enhanced CSRF Protection for testing and production
const csrfTokens = new Map();
const allowedOrigins = new Set(
    (process.env.ALLOWED_ORIGINS || 'http://localhost:3000,http://localhost:8002,http://127.0.0.1:8002')
        .split(',')
        .map((origin) => origin.trim())
        .filter(Boolean)
);

// CSRF is a browser-session threat. Service-to-service requests without Origin
// or cookies do not need a CSRF token.
function browserCsrfProtection(req, res, next) {
    if (!req.headers.origin && !req.headers.cookie) {
        return next();
    }
    const headerToken = req.headers['x-csrf-token'];
    const cookieToken = req.cookies.csrf_token;
    const expiresAt = csrfTokens.get(headerToken);
    const sameToken = typeof headerToken === 'string'
        && typeof cookieToken === 'string'
        && headerToken.length === cookieToken.length
        && timingSafeEqual(Buffer.from(headerToken), Buffer.from(cookieToken));

    if (!allowedOrigins.has(req.headers.origin) || !sameToken || !expiresAt || expiresAt < Date.now()) {
        return res.status(403).json({ error: 'Invalid CSRF token' });
    }
    csrfTokens.delete(headerToken);
    return next();
}

// Allowed hosts for SSRF prevention
const userServiceUrl = new URL(process.env.USER_SERVICE_URL || 'http://localhost:8001');
const allowedHosts = [userServiceUrl.host];

// In-memory storage with optimized access
const orders = {};
const ordersCache = new Map(); // LRU-like cache for frequent access
const MAX_CACHE_SIZE = 1000;

// Helper function to manage cache
function cacheOrder(orderId, order) {
    if (ordersCache.size >= MAX_CACHE_SIZE) {
        // Remove oldest entry (simple FIFO)
        const firstKey = ordersCache.keys().next().value;
        ordersCache.delete(firstKey);
    }
    ordersCache.set(orderId, order);
}

function getCachedOrder(orderId) {
    return ordersCache.get(orderId) || orders[orderId];
}

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'order-service' });
});

// CSRF token endpoint
app.get('/csrf-token', (req, res) => {
    const token = randomBytes(32).toString('base64url');
    csrfTokens.set(token, Date.now() + 60 * 60 * 1000);
    res.cookie('csrf_token', token, {
        httpOnly: true,
        sameSite: 'strict',
        secure: process.env.COOKIE_SECURE === 'true',
        maxAge: 60 * 60 * 1000
    });
    res.json({ csrfToken: token });
});

// Create order with proper rate limiting and caching
app.post('/orders', createOrderLimiter, browserCsrfProtection, async (req, res) => {
    try {
        const { user_id, items, total_amount } = req.body;
        
        // Validate input
        if (!isValidUserId(user_id)) {
            return res.status(400).json({ error: 'Invalid user ID' });
        }
        
        // Check user cache first
        const cacheKey = `user_${user_id}`;
        let userExists = ordersCache.get(cacheKey);
        
        if (userExists === undefined) {
            // Validate user exists with SSRF protection
            const userURL = new URL(`/users/${encodeURIComponent(user_id)}`, userServiceUrl).toString();
            if (!isAllowedURL(userURL)) {
                return res.status(400).json({ error: 'Invalid request' });
            }
            
            try {
                const userResponse = await fetch(userURL, {
                    signal: AbortSignal.timeout(1500),
                    redirect: 'manual'
                });
                userExists = userResponse.status === 200;
                // Cache user validation for 30 seconds
                ordersCache.set(cacheKey, userExists);
                const evictionTimer = setTimeout(() => ordersCache.delete(cacheKey), 30000);
                evictionTimer.unref();
            } catch (error) {
                const cause = error.cause?.message || error.cause?.code;
                console.error(
                    `User validation error for ${user_id}:`,
                    cause ? `${error.message} (${cause})` : error.message
                );
                // On network error, don't cache and return error
                return res.status(503).json({ error: 'User service unavailable' });
            }
        }
        
        if (!userExists) {
            return res.status(400).json({ error: 'User not found' });
        }
        
        const order = {
            id: randomUUID(),
            user_id,
            items,
            total_amount,
            status: 'pending',
            created_at: new Date().toISOString()
        };
        
        orders[order.id] = order;
        cacheOrder(order.id, order);
        res.status(201).json(order);
    } catch (error) {
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get order - optimized with cache and rate limiting
app.get('/orders/:order_id', generalLimiter, (req, res) => {
    const order = getCachedOrder(req.params.order_id);
    if (!order) {
        return res.status(404).json({ error: 'Order not found' });
    }
    res.json(order);
});

// List orders
app.get('/orders', (req, res) => {
    res.json(Object.values(orders));
});

// Update order status with rate limiting and CSRF protection
app.patch('/orders/:order_id/status', generalLimiter, browserCsrfProtection, (req, res) => {
    // CSRF token is now validated by middleware
    
    const order = getCachedOrder(req.params.order_id);
    if (!order) {
        return res.status(404).json({ error: 'Order not found' });
    }
    
    order.status = req.body.status;
    order.updated_at = new Date().toISOString();
    
    // Update both storage and cache
    orders[req.params.order_id] = order;
    cacheOrder(req.params.order_id, order);
    
    res.json(order);
});

// Validation functions - more flexible for UUIDs
function isValidUserId(userId) {
    // Allow UUIDs and alphanumeric with hyphens
    return /^[a-fA-F0-9-]+$/.test(userId) && userId.length > 0 && userId.length <= 50;
}

function isAllowedURL(targetURL) {
    try {
        const parsedURL = new URL(targetURL);
        
        // Only allow HTTP protocol
        if (parsedURL.protocol !== 'http:') {
            return false;
        }
        
        // Check if host is in allowed list
        return allowedHosts.includes(parsedURL.host);
    } catch (error) {
        return false;
    }
}

const PORT = process.env.PORT || 8002;
if (require.main === module) {
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Order Service running on port ${PORT}`);
    });
}

module.exports = { app, isAllowedURL, isValidUserId };
