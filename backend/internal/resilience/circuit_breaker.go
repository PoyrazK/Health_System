package resilience

import (
	"log"
	"time"

	"github.com/sony/gobreaker"
)

// NewCircuitBreaker creates a configured Sony gobreaker
func NewCircuitBreaker(name string) *gobreaker.CircuitBreaker {
	settings := gobreaker.Settings{
		Name:        name,
		MaxRequests: 3,
		Interval:    time.Minute,
		Timeout:     30 * time.Second,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
			return counts.Requests >= 5 && failureRatio >= 0.6
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			log.Printf("🔌 Circuit Breaker [%s]: %s -> %s", name, from, to)
		},
	}

	return gobreaker.NewCircuitBreaker(settings)
}
