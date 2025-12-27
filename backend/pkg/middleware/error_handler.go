package middleware

import (
	"log"
	"runtime/debug"

	"github.com/gofiber/fiber/v2"
)

// ErrorResponse is the standard error format for all API errors
type ErrorResponse struct {
	Success bool   `json:"success"`
	Error   string `json:"error"`
	Code    int    `json:"code"`
}

// ErrorHandler is a global error handling middleware
func ErrorHandler(c *fiber.Ctx) error {
	// Recover from panics
	defer func() {
		if r := recover(); r != nil {
			log.Printf("🔥 PANIC RECOVERED: %v\n%s", r, debug.Stack())
			c.Status(500).JSON(ErrorResponse{
				Success: false,
				Error:   "Internal Server Error",
				Code:    500,
			})
		}
	}()

	err := c.Next()

	if err != nil {
		// Log the error
		log.Printf("❌ Error: %v | Path: %s | Method: %s", err, c.Path(), c.Method())

		// Check if it's a Fiber error
		if e, ok := err.(*fiber.Error); ok {
			return c.Status(e.Code).JSON(ErrorResponse{
				Success: false,
				Error:   e.Message,
				Code:    e.Code,
			})
		}

		// Default to 500 for unknown errors
		return c.Status(500).JSON(ErrorResponse{
			Success: false,
			Error:   "Internal Server Error",
			Code:    500,
		})
	}

	return nil
}
