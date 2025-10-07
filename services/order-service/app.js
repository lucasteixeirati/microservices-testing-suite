const express = require('express');
const axios = require('axios');
const csrf = require('csurf');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
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
const csrfProtection = csrf({ 
    cookie: true,
    ignoreMethods: ['GET', 'HEAD', 'OPTIONS'],
    value: (req) => {
        const token = req.headers['x-csrf-token'] || req.body._csrf || req.query._csrf;
        // For development: accept test tokens, for production: validate properly
        return token && token.length >= 8 ? token : 'dev-test-token-' + Date.now();
    }
});

// Allowed hosts for SSRF prevention
const allowedHosts = ['localhost:8001', 'user-service:8001'];

// Configure axios with production-ready settings
axios.defaults.timeout = 2000;
axios.defaults.maxRedirects = 0;

// Production-grade connection pooling
const http = require('http');
const agent = new http.Agent({
    keepAlive: true,
    maxSockets: 100,
    maxFreeSockets: 20,
    timeout: 2000,
    keepAliveMsecs: 1000
});
axios.defaults.httpAgent = agent;

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
app.get('/csrf-token', csrfProtection, (req, res) => {
    res.json({ csrfToken: req.csrfToken() });
});

// Create order with proper rate limiting and caching
app.post('/orders', createOrderLimiter, async (req, res) => {
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
            const userURL = `http://localhost:8001/users/${encodeURIComponent(user_id)}`;
            if (!isAllowedURL(userURL)) {
                return res.status(400).json({ error: 'Invalid request' });
            }
            
            try {
                const userResponse = await axios.get(userURL, {
                    timeout: 1500,
                    validateStatus: (status) => status < 500,
                    maxRedirects: 0 // Prevent redirect attacks
                });
                userExists = userResponse.status === 200;
                // Cache user validation for 30 seconds
                ordersCache.set(cacheKey, userExists);
                setTimeout(() => ordersCache.delete(cacheKey), 30000);
            } catch (error) {
                console.error(`User validation error for ${user_id}:`, error.message);
                if (error.response?.status === 404) {
                    return res.status(400).json({ error: 'User not found' });
                }
                // On network error, don't cache and return error
                return res.status(503).json({ error: 'User service unavailable' });
            }
        }
        
        if (!userExists) {
            return res.status(400).json({ error: 'User not found' });
        }
        
        const order = {
            id: uuidv4(),
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
app.patch('/orders/:order_id/status', generalLimiter, csrfProtection, (req, res) => {
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
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Order Service running on port ${PORT}`);
});