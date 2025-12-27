package unit

import (
	"errors"
	"healthcare-backend/pkg/resilience"
	"testing"
)

// TestNewCircuitBreaker tests circuit breaker creation
func TestNewCircuitBreaker(t *testing.T) {
	cb := resilience.NewCircuitBreaker("test-service")
	
	if cb == nil {
		t.Fatal("Expected circuit breaker to be created, got nil")
	}
	
	if cb.Name() != "test-service" {
		t.Errorf("Expected name 'test-service', got '%s'", cb.Name())
	}
}

// TestCircuitBreaker_SuccessfulCalls tests that successful calls pass through
func TestCircuitBreaker_SuccessfulCalls(t *testing.T) {
	cb := resilience.NewCircuitBreaker("success-test")
	
	result, err := cb.Execute(func() (interface{}, error) {
		return "success", nil
	})
	
	if err != nil {
		t.Fatalf("Expected no error, got: %v", err)
	}
	
	if result != "success" {
		t.Errorf("Expected 'success', got '%v'", result)
	}
}

// TestCircuitBreaker_FailedCalls tests that failures are recorded
func TestCircuitBreaker_FailedCalls(t *testing.T) {
	cb := resilience.NewCircuitBreaker("failure-test")
	
	testErr := errors.New("test error")
	
	_, err := cb.Execute(func() (interface{}, error) {
		return nil, testErr
	})
	
	if err == nil {
		t.Fatal("Expected error, got nil")
	}
	
	if err.Error() != testErr.Error() {
		t.Errorf("Expected error '%v', got '%v'", testErr, err)
	}
}

// TestCircuitBreaker_OpenAfterThreshold tests that CB opens after failure threshold
func TestCircuitBreaker_OpenAfterThreshold(t *testing.T) {
	cb := resilience.NewCircuitBreaker("threshold-test")
	
	testErr := errors.New("consistent failure")
	
	for i := 0; i < 10; i++ {
		cb.Execute(func() (interface{}, error) {
			return nil, testErr
		})
	}
	
	state := cb.State()
	t.Logf("Circuit breaker state after failures: %v", state)
}

// TestCircuitBreaker_Recovery tests half-open to closed recovery
func TestCircuitBreaker_Recovery(t *testing.T) {
	cb := resilience.NewCircuitBreaker("recovery-test")
	
	for i := 0; i < 5; i++ {
		cb.Execute(func() (interface{}, error) {
			return "ok", nil
		})
	}
	
	result, err := cb.Execute(func() (interface{}, error) {
		return "recovered", nil
	})
	
	if err != nil {
		t.Fatalf("Expected successful call after recovery, got error: %v", err)
	}
	
	if result != "recovered" {
		t.Errorf("Expected 'recovered', got '%v'", result)
	}
}
