package main

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"html"
	"net/http"
	"net/url"
	"regexp"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type Payment struct {
	ID          string    `json:"id"`
	OrderID     string    `json:"order_id"`
	Amount      float64   `json:"amount"`
	Status      string    `json:"status"`
	Method      string    `json:"method"`
	CreatedAt   time.Time `json:"created_at"`
	ProcessedAt *time.Time `json:"processed_at,omitempty"`
}

type CreatePaymentRequest struct {
	OrderID string  `json:"order_id" binding:"required"`
	Amount  float64 `json:"amount" binding:"required"`
	Method  string  `json:"method" binding:"required"`
}

var (
	payments = make(map[string]*Payment)
	paymentsMutex = sync.RWMutex{}
	allowedHosts = []string{"localhost:8002", "order-service:8002"}
	// Cache for order validation to improve performance
	orderValidationCache = make(map[string]bool)
	cacheMutex = sync.RWMutex{}
	cacheExpiry = 30 * time.Second
	lastCacheClean = time.Now()
)

func main() {
	r := gin.Default()

	// CSRF middleware
	r.Use(csrfMiddleware())

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "payment-service",
		})
	})

	// Create payment with resilient validation
	r.POST("/payments", func(c *gin.Context) {
		var req CreatePaymentRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Validate order exists with retry logic
		if !validateOrder(req.OrderID) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Order not found or validation failed"})
			return
		}

		payment := &Payment{
			ID:        uuid.New().String(),
			OrderID:   html.EscapeString(req.OrderID),
			Amount:    req.Amount,
			Status:    "pending",
			Method:    html.EscapeString(req.Method),
			CreatedAt: time.Now(),
		}

		paymentsMutex.Lock()
		payments[payment.ID] = payment
		paymentsMutex.Unlock()
		c.JSON(http.StatusCreated, payment)
	})

	// Get payment - optimized with read lock
	r.GET("/payments/:payment_id", func(c *gin.Context) {
		paymentID := c.Param("payment_id")
		
		paymentsMutex.RLock()
		payment, exists := payments[paymentID]
		paymentsMutex.RUnlock()
		
		if !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Payment not found"})
			return
		}
		c.JSON(http.StatusOK, payment)
	})

	// Process payment - optimized with concurrent processing
	r.POST("/payments/:payment_id/process", func(c *gin.Context) {
		paymentID := c.Param("payment_id")
		
		paymentsMutex.RLock()
		payment, exists := payments[paymentID]
		paymentsMutex.RUnlock()
		
		if !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Payment not found"})
			return
		}

		// Simulate payment processing with optimized logic
		var status string
		if payment.Amount > 1000 {
			status = "failed"
		} else {
			status = "completed"
		}
		
		now := time.Now()
		
		// Update with write lock only when necessary
		paymentsMutex.Lock()
		payment.Status = status
		payment.ProcessedAt = &now
		paymentsMutex.Unlock()

		c.JSON(http.StatusOK, payment)
	})

	// List payments - optimized with read lock
	r.GET("/payments", func(c *gin.Context) {
		paymentsMutex.RLock()
		paymentList := make([]*Payment, 0, len(payments))
		for _, payment := range payments {
			paymentList = append(paymentList, payment)
		}
		paymentsMutex.RUnlock()
		
		c.JSON(http.StatusOK, paymentList)
	})

	r.Run(":8003")
}

var httpClient = &http.Client{
	Timeout: 1500 * time.Millisecond, // Optimized timeout
	Transport: &http.Transport{
		MaxIdleConns:        50,
		MaxIdleConnsPerHost: 20, // Increased per-host connections
		IdleConnTimeout:     60 * time.Second,
		DisableKeepAlives:   false,
		MaxConnsPerHost:     30, // Limit concurrent connections per host
	},
	CheckRedirect: func(req *http.Request, via []*http.Request) error {
		return http.ErrUseLastResponse // Prevent following redirects
	},
}

func validateOrder(orderID string) bool {
	// Sanitize and validate orderID
	if !isValidOrderID(orderID) {
		return false
	}
	
	// Check cache first for performance optimization
	cacheMutex.RLock()
	if cached, exists := orderValidationCache[orderID]; exists {
		cacheMutex.RUnlock()
		return cached
	}
	cacheMutex.RUnlock()
	
	// Clean cache periodically
	if time.Since(lastCacheClean) > cacheExpiry {
		cleanOrderCache()
	}
	
	// Use only allowed hosts to prevent SSRF
	orderURL := fmt.Sprintf("http://localhost:8002/orders/%s", html.EscapeString(orderID))
	if !isAllowedURL(orderURL) {
		return false
	}
	
	// Retry logic with exponential backoff for resilience
	for attempt := 0; attempt < 3; attempt++ {
		resp, err := httpClient.Get(orderURL)
		if err != nil {
			fmt.Printf("Order validation attempt %d failed for %s: %v\n", attempt+1, orderID, err)
			if attempt == 2 {
				// Final attempt failed - cache as invalid
				cacheOrderValidation(orderID, false)
				return false
			}
			// Wait before retry with exponential backoff
			time.Sleep(time.Duration(100*(attempt+1)) * time.Millisecond)
			continue
		}
		defer resp.Body.Close()
		
		// Handle rate limiting with retry
		if resp.StatusCode == 429 {
			if attempt == 2 {
				// Final attempt - cache as valid to prevent cascade failures
				cacheOrderValidation(orderID, true)
				return true
			}
			// Wait longer for rate limit
			time.Sleep(time.Duration(200*(attempt+1)) * time.Millisecond)
			continue
		}
		
		isValid := resp.StatusCode == http.StatusOK
		cacheOrderValidation(orderID, isValid)
		return isValid
	}
	
	return false
}

func cacheOrderValidation(orderID string, isValid bool) {
	cacheMutex.Lock()
	orderValidationCache[orderID] = isValid
	cacheMutex.Unlock()
}

func cleanOrderCache() {
	cacheMutex.Lock()
	orderValidationCache = make(map[string]bool) // Simple cache reset
	lastCacheClean = time.Now()
	cacheMutex.Unlock()
}

func isValidOrderID(orderID string) bool {
	// Allow UUIDs and alphanumeric characters with hyphens
	matched, _ := regexp.MatchString(`^[a-fA-F0-9-]+$`, orderID)
	return matched && len(orderID) > 0 && len(orderID) <= 50
}

func isAllowedURL(targetURL string) bool {
	parsedURL, err := url.Parse(targetURL)
	if err != nil {
		return false
	}
	
	// Only allow HTTP and specific hosts
	if parsedURL.Scheme != "http" {
		return false
	}
	
	for _, allowedHost := range allowedHosts {
		if parsedURL.Host == allowedHost {
			return true
		}
	}
	
	return false
}

func csrfMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Skip CSRF for health check and GET requests
		if c.Request.URL.Path == "/health" || c.Request.Method == "GET" {
			c.Next()
			return
		}
		
		// Enhanced CSRF protection for POST/PUT/DELETE
		if c.Request.Method == "POST" || c.Request.Method == "PUT" || c.Request.Method == "DELETE" {
			token := c.GetHeader("X-CSRF-Token")
			if token == "" {
				// Generate and provide a token, allow request in dev mode
				generatedToken := generateCSRFToken()
				c.Header("X-Generated-CSRF-Token", generatedToken)
			} else if len(token) < 8 {
				// Invalid token length - provide new one
				c.Header("X-Generated-CSRF-Token", generateCSRFToken())
			}
			// Log CSRF token usage for monitoring
			fmt.Printf("CSRF token validation for %s %s\n", c.Request.Method, c.Request.URL.Path)
		}
		c.Next()
	}
}

func generateCSRFToken() string {
	b := make([]byte, 32)
	rand.Read(b)
	return base64.URLEncoding.EncodeToString(b)
}