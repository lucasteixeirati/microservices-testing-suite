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

	// Create payment
	r.POST("/payments", func(c *gin.Context) {
		var req CreatePaymentRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		// Validate order exists
		if !validateOrder(req.OrderID) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Order not found"})
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

	// Get payment
	r.GET("/payments/:payment_id", func(c *gin.Context) {
		paymentID := c.Param("payment_id")
		payment, exists := payments[paymentID]
		if !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Payment not found"})
			return
		}
		c.JSON(http.StatusOK, payment)
	})

	// Process payment
	r.POST("/payments/:payment_id/process", func(c *gin.Context) {
		paymentID := c.Param("payment_id")
		payment, exists := payments[paymentID]
		if !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Payment not found"})
			return
		}

		// Simulate payment processing
		if payment.Amount > 1000 {
			payment.Status = "failed"
		} else {
			payment.Status = "completed"
		}
		
		now := time.Now()
		payment.ProcessedAt = &now

		c.JSON(http.StatusOK, payment)
	})

	// List payments
	r.GET("/payments", func(c *gin.Context) {
		paymentList := make([]*Payment, 0, len(payments))
		for _, payment := range payments {
			paymentList = append(paymentList, payment)
		}
		c.JSON(http.StatusOK, paymentList)
	})

	r.Run(":8003")
}

var httpClient = &http.Client{
	Timeout: 5 * time.Second,
}

func validateOrder(orderID string) bool {
	// Sanitize and validate orderID
	if !isValidOrderID(orderID) {
		return false
	}
	
	// Use only allowed hosts to prevent SSRF
	orderURL := fmt.Sprintf("http://localhost:8002/orders/%s", html.EscapeString(orderID))
	if !isAllowedURL(orderURL) {
		return false
	}
	
	resp, err := httpClient.Get(orderURL)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	
	return resp.StatusCode == http.StatusOK
}

func isValidOrderID(orderID string) bool {
	// Only allow alphanumeric characters and hyphens
	matched, _ := regexp.MatchString(`^[a-zA-Z0-9-]+$`, orderID)
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
		// Skip CSRF for health check and development
		if c.Request.URL.Path == "/health" {
			c.Next()
			return
		}
		
		// For development/testing, allow all requests and just generate tokens
		if c.Request.Method == "POST" || c.Request.Method == "PUT" || c.Request.Method == "DELETE" {
			token := c.GetHeader("X-CSRF-Token")
			if token == "" {
				// Generate and provide a token for development, but don't block the request
				c.Header("X-Generated-CSRF-Token", generateCSRFToken())
			}
		}
		c.Next()
	}
}

func generateCSRFToken() string {
	b := make([]byte, 32)
	rand.Read(b)
	return base64.URLEncoding.EncodeToString(b)
}