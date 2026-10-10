package main

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"html"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

type Payment struct {
	ID          string     `json:"id"`
	OrderID     string     `json:"order_id"`
	Amount      float64    `json:"amount"`
	Status      string     `json:"status"`
	Method      string     `json:"method"`
	CreatedAt   time.Time  `json:"created_at"`
	ProcessedAt *time.Time `json:"processed_at,omitempty"`
}

type CreatePaymentRequest struct {
	OrderID string  `json:"order_id" binding:"required"`
	Amount  float64 `json:"amount" binding:"required"`
	Method  string  `json:"method" binding:"required"`
}

var (
	payments        = make(map[string]*Payment)
	paymentsMutex   = sync.RWMutex{}
	orderServiceURL = envOrDefault("ORDER_SERVICE_URL", "http://localhost:8002")
	// Cache for order validation to improve performance
	orderValidationCache = make(map[string]bool)
	cacheMutex           = sync.RWMutex{}
	cacheExpiry          = 30 * time.Second
	lastCacheClean       = time.Now()
	csrfTokens           = make(map[string]time.Time)
	csrfMutex            = sync.RWMutex{}
)

func main() {
	setupRouter().Run(":8003")
}

func setupRouter() *gin.Engine {
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

	r.GET("/csrf-token", func(c *gin.Context) {
		token := generateCSRFToken()
		csrfMutex.Lock()
		csrfTokens[token] = time.Now().Add(time.Hour)
		csrfMutex.Unlock()
		secure := strings.EqualFold(os.Getenv("COOKIE_SECURE"), "true")
		c.SetSameSite(http.SameSiteStrictMode)
		c.SetCookie("csrf_token", token, 3600, "/", "", secure, true)
		c.JSON(http.StatusOK, gin.H{"csrf_token": token})
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

	return r
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
	orderURL := fmt.Sprintf("%s/orders/%s", strings.TrimRight(orderServiceURL, "/"), url.PathEscape(orderID))
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
		// Handle rate limiting with retry
		if resp.StatusCode == 429 {
			resp.Body.Close()
			if attempt == 2 {
				cacheOrderValidation(orderID, false)
				return false
			}
			// Wait longer for rate limit
			time.Sleep(time.Duration(200*(attempt+1)) * time.Millisecond)
			continue
		}

		isValid := resp.StatusCode == http.StatusOK
		resp.Body.Close()
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

	configuredURL, err := url.Parse(orderServiceURL)
	return err == nil && parsedURL.Host == configuredURL.Host
}

func csrfMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Skip CSRF for health check and GET requests
		if c.Request.URL.Path == "/health" || c.Request.Method == "GET" {
			c.Next()
			return
		}

		// CSRF protects browser sessions. Internal API clients without Origin or
		// cookies are not susceptible to this browser-specific attack.
		if c.Request.Method == "POST" || c.Request.Method == "PUT" || c.Request.Method == "DELETE" {
			origin := c.GetHeader("Origin")
			cookieToken, cookieErr := c.Cookie("csrf_token")
			if origin == "" && cookieErr != nil {
				c.Next()
				return
			}
			if !isAllowedOrigin(origin) || cookieErr != nil || !validCSRFToken(c.GetHeader("X-CSRF-Token"), cookieToken) {
				c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "Invalid CSRF token"})
				return
			}
		}
		c.Next()
	}
}

func isAllowedOrigin(origin string) bool {
	configured := envOrDefault("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8003,http://127.0.0.1:8003")
	for _, allowed := range strings.Split(configured, ",") {
		if strings.TrimSpace(allowed) == origin {
			return true
		}
	}
	return false
}

func validCSRFToken(headerToken, cookieToken string) bool {
	if headerToken == "" || cookieToken == "" || subtle.ConstantTimeCompare([]byte(headerToken), []byte(cookieToken)) != 1 {
		return false
	}
	csrfMutex.Lock()
	expiresAt, exists := csrfTokens[headerToken]
	valid := exists && time.Now().Before(expiresAt)
	if valid {
		delete(csrfTokens, headerToken)
	}
	csrfMutex.Unlock()
	return valid
}

func envOrDefault(key, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(key)); value != "" {
		return value
	}
	return fallback
}

func generateCSRFToken() string {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		panic(fmt.Sprintf("cannot generate CSRF token: %v", err))
	}
	return base64.URLEncoding.EncodeToString(b)
}
