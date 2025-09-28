const express = require('express');
const axios = require('axios');
const csrf = require('csurf');
const cookieParser = require('cookie-parser');
const { v4: uuidv4 } = require('uuid');
const { URL } = require('url');

const app = express();
app.use(express.json());
app.use(cookieParser());

// CSRF Protection enabled
const csrfProtection = csrf({ cookie: true });

// Allowed hosts for SSRF prevention
const allowedHosts = ['localhost:8001', 'user-service:8001'];

// Configure axios with timeout
axios.defaults.timeout = 5000;

// In-memory storage
const orders = {};

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'order-service' });
});

// CSRF token endpoint
app.get('/csrf-token', csrfProtection, (req, res) => {
    res.json({ csrfToken: req.csrfToken() });
});

// Create order
app.post('/orders', csrfProtection, async (req, res) => {
    try {
        const { user_id, items, total_amount } = req.body;
        
        // Validate input
        if (!isValidUserId(user_id)) {
            return res.status(400).json({ error: 'Invalid user ID' });
        }
        
        // Validate user exists with SSRF protection
        const userURL = `http://localhost:8001/users/${encodeURIComponent(user_id)}`;
        if (!isAllowedURL(userURL)) {
            return res.status(400).json({ error: 'Invalid request' });
        }
        
        const userResponse = await axios.get(userURL, {
            timeout: 5000
        });
        
        const order = {
            id: uuidv4(),
            user_id,
            items,
            total_amount,
            status: 'pending',
            created_at: new Date().toISOString()
        };
        
        orders[order.id] = order;
        res.status(201).json(order);
    } catch (error) {
        if (error.response?.status === 404) {
            return res.status(400).json({ error: 'User not found' });
        }
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Get order
app.get('/orders/:order_id', (req, res) => {
    const order = orders[req.params.order_id];
    if (!order) {
        return res.status(404).json({ error: 'Order not found' });
    }
    res.json(order);
});

// List orders
app.get('/orders', (req, res) => {
    res.json(Object.values(orders));
});

// Update order status
app.patch('/orders/:order_id/status', csrfProtection, (req, res) => {
    const order = orders[req.params.order_id];
    if (!order) {
        return res.status(404).json({ error: 'Order not found' });
    }
    
    order.status = req.body.status;
    order.updated_at = new Date().toISOString();
    
    res.json(order);
});

// Validation functions
function isValidUserId(userId) {
    return /^[a-zA-Z0-9-]+$/.test(userId) && userId.length > 0 && userId.length <= 50;
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