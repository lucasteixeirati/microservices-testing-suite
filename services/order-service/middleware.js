// Request logging decorator
function withLogging(handler) {
    return async (req, res, next) => {
        const start = Date.now();
        const originalSend = res.send;
        
        res.send = function(data) {
            const duration = Date.now() - start;
            console.log(`${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
            originalSend.call(this, data);
        };
        
        return handler(req, res, next);
    };
}

// Retry decorator for HTTP calls
function withRetry(fn, maxRetries = 3) {
    return async (...args) => {
        let lastError;
        
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await fn(...args);
            } catch (error) {
                lastError = error;
                if (i < maxRetries - 1) {
                    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                }
            }
        }
        
        throw lastError;
    };
}

module.exports = { withLogging, withRetry };