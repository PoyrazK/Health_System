package unit

import (
	"healthcare-backend/pkg/queue"
	"testing"
	"github.com/nats-io/nats.go"
)

// TestNATS_IsConnected tests connection status check
func TestNATS_IsConnected(t *testing.T) {
	if queue.NC == nil {
		connected := queue.IsConnected()
		if connected {
			t.Error("Expected IsConnected to return false when NC is nil")
		}
	}
}

// TestNATS_PublishWithoutConnection tests publish behavior without connection
func TestNATS_PublishWithoutConnection(t *testing.T) {
	if queue.NC != nil {
		t.Skip("NATS is connected, skipping disconnection test")
	}
	
	err := queue.Publish("test.subject", []byte("test message"))
	if err == nil {
		t.Error("Expected error when publishing without NATS connection")
	}
}

// TestNATS_CloseNil tests Close behavior when NC is nil
func TestNATS_CloseNil(t *testing.T) {
	// Save original NC
	originalNC := queue.NC
	queue.NC = nil
	
	queue.Close()
	
	// Restore
	queue.NC = originalNC
}

// TestNATS_Integration_PublishSubscribe is an integration test
func TestNATS_Integration_PublishSubscribe(t *testing.T) {
	if queue.NC == nil || !queue.IsConnected() {
		t.Skip("NATS not connected, skipping integration test")
	}
	
	received := make(chan []byte, 1)
	
	sub, err := queue.NC.Subscribe("test.integration", func(msg *nats.Msg) {
		received <- msg.Data
	})
	if err != nil {
		t.Fatalf("Failed to subscribe: %v", err)
	}
	defer sub.Unsubscribe()
	
	testData := []byte("integration test message")
	err = queue.Publish("test.integration", testData)
	if err != nil {
		t.Fatalf("Failed to publish: %v", err)
	}
	
	_ = received
}
