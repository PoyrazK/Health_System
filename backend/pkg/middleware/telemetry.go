package middleware

import (
	"sync/atomic"
	"time"

	"github.com/gofiber/fiber/v2"
)

var (
	StartTime    = time.Now()
	RequestCount uint64
	ErrorCount   uint64
)

func PerformanceMiddleware(c *fiber.Ctx) error {
	atomic.AddUint64(&RequestCount, 1)
	
	err := c.Next()
	
	if err != nil || (c.Response().StatusCode() >= 400 && c.Response().StatusCode() != 429) {
		atomic.AddUint64(&ErrorCount, 1)
	}
	
	return err
}
