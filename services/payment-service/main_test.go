package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
)

func setupOrderStub(t *testing.T, status int) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(status)
	}))
	originalURL, originalClient := orderServiceURL, httpClient
	orderServiceURL, httpClient = server.URL, server.Client()
	cacheMutex.Lock()
	orderValidationCache = make(map[string]bool)
	cacheMutex.Unlock()
	t.Cleanup(func() {
		server.Close()
		orderServiceURL, httpClient = originalURL, originalClient
	})
}

func performRequest(router http.Handler, method, path, body string) *httptest.ResponseRecorder {
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(method, path, strings.NewReader(body))
	request.Header.Set("Content-Type", "application/json")
	router.ServeHTTP(recorder, request)
	return recorder
}

func TestHealth(t *testing.T) {
	gin.SetMode(gin.TestMode)
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, "/health", nil)
	setupRouter().ServeHTTP(recorder, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", recorder.Code)
	}
}

func TestBrowserWriteRequiresCSRF(t *testing.T) {
	gin.SetMode(gin.TestMode)
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodPost, "/payments", strings.NewReader(`{"order_id":"abc-123","amount":10,"method":"card"}`))
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Origin", "http://localhost:3000")
	setupRouter().ServeHTTP(recorder, request)

	if recorder.Code != http.StatusForbidden {
		t.Fatalf("expected 403, got %d: %s", recorder.Code, recorder.Body.String())
	}
}

func TestCSRFIssuanceAndValidation(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := setupRouter()
	tokenRecorder := httptest.NewRecorder()
	router.ServeHTTP(tokenRecorder, httptest.NewRequest(http.MethodGet, "/csrf-token", nil))

	var payload map[string]string
	if err := json.Unmarshal(tokenRecorder.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	token := payload["csrf_token"]
	if token == "" || len(tokenRecorder.Result().Cookies()) == 0 {
		t.Fatal("expected token and CSRF cookie")
	}
	if !validCSRFToken(token, token) {
		t.Fatal("issued token should be valid")
	}
}

func TestURLAllowlist(t *testing.T) {
	original := orderServiceURL
	orderServiceURL = "http://order-service:8002"
	t.Cleanup(func() { orderServiceURL = original })

	if !isAllowedURL("http://order-service:8002/orders/abc-123") {
		t.Fatal("configured service URL should be allowed")
	}
	if isAllowedURL("http://evil.example/orders/abc-123") {
		t.Fatal("unconfigured host should be rejected")
	}
	if !isValidOrderID("550e8400-e29b-41d4-a716-446655440000") {
		t.Fatal("UUID should be accepted")
	}
	if isValidOrderID("../etc/passwd") {
		t.Fatal("path traversal should be rejected")
	}
}

func TestPaymentLifecycle(t *testing.T) {
	gin.SetMode(gin.TestMode)
	setupOrderStub(t, http.StatusOK)
	router := setupRouter()

	created := performRequest(router, http.MethodPost, "/payments", `{"order_id":"abc-123","amount":100,"method":"card"}`)
	if created.Code != http.StatusCreated {
		t.Fatalf("expected 201, got %d: %s", created.Code, created.Body.String())
	}
	var payment Payment
	if err := json.Unmarshal(created.Body.Bytes(), &payment); err != nil {
		t.Fatal(err)
	}

	if got := performRequest(router, http.MethodGet, "/payments/"+payment.ID, ""); got.Code != http.StatusOK {
		t.Fatalf("expected payment lookup to succeed, got %d", got.Code)
	}
	processed := performRequest(router, http.MethodPost, "/payments/"+payment.ID+"/process", "")
	if processed.Code != http.StatusOK || !strings.Contains(processed.Body.String(), `"status":"completed"`) {
		t.Fatalf("expected completed payment: %s", processed.Body.String())
	}
	if listed := performRequest(router, http.MethodGet, "/payments", ""); listed.Code != http.StatusOK {
		t.Fatalf("expected list to succeed, got %d", listed.Code)
	}
}

func TestPaymentValidationFailures(t *testing.T) {
	gin.SetMode(gin.TestMode)
	setupOrderStub(t, http.StatusNotFound)
	router := setupRouter()

	invalidJSON := performRequest(router, http.MethodPost, "/payments", `{`)
	if invalidJSON.Code != http.StatusBadRequest {
		t.Fatalf("expected invalid JSON to be rejected, got %d", invalidJSON.Code)
	}
	invalidOrder := performRequest(router, http.MethodPost, "/payments", `{"order_id":"def-456","amount":10,"method":"card"}`)
	if invalidOrder.Code != http.StatusBadRequest {
		t.Fatalf("expected missing order to be rejected, got %d", invalidOrder.Code)
	}
	missing := performRequest(router, http.MethodGet, "/payments/missing", "")
	if missing.Code != http.StatusNotFound {
		t.Fatalf("expected missing payment to return 404, got %d", missing.Code)
	}
}
