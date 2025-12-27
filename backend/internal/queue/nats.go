package queue

import (
	"log"
	"time"

	"github.com/nats-io/nats.go"
)

var (
	NC *nats.Conn
	JS nats.JetStreamContext
)

// InitNATS initializes the NATS connection
func InitNATS(url string) {
	var err error
	// Use exponential backoff for NATS connection
	for i := 0; i < 5; i++ {
		NC, err = nats.Connect(url, 
			nats.RetryOnFailedConnect(true),
			nats.MaxReconnects(10),
			nats.ReconnectWait(time.Second*2),
		)
		if err == nil {
			break
		}
		log.Printf("⚠️ NATS connection failed (attempt %d): %v", i+1, err)
		time.Sleep(time.Duration(i+1) * time.Second)
	}

	if err != nil {
		log.Printf("❌ Fatal: Could not connect to NATS: %v", err)
		return
	}

	// Initialize JetStream (for persistent streams if needed)
	JS, err = NC.JetStream()
	if err != nil {
		log.Printf("⚠️ JetStream initialization failed: %v", err)
	}

	log.Println("⚡ NATS connected successfully")
}

// Publish sends a message to a subject
func Publish(subject string, data []byte) error {
	return NC.Publish(subject, data)
}

// Subscribe listens to a subject
func Subscribe(subject string, cb nats.MsgHandler) (*nats.Subscription, error) {
	return NC.Subscribe(subject, cb)
}

// Close closes the NATS connection
func Close() {
	if NC != nil {
		NC.Close()
	}
}

// IsConnected checks if NATS is connected
func IsConnected() bool {
	return NC != nil && NC.Status() == nats.CONNECTED
}
