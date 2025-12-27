package middleware

import (
	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
)

// Validator instance
var validate = validator.New()

// ValidationError represents a single field validation error
type ValidationError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

// ValidateStruct validates a struct and returns formatted errors
func ValidateStruct(s interface{}) []ValidationError {
	var errors []ValidationError

	err := validate.Struct(s)
	if err != nil {
		for _, err := range err.(validator.ValidationErrors) {
			var element ValidationError
			element.Field = err.Field()
			element.Message = getErrorMessage(err)
			errors = append(errors, element)
		}
	}

	return errors
}

// getErrorMessage returns a human-readable error message for validation errors
func getErrorMessage(fe validator.FieldError) string {
	switch fe.Tag() {
	case "required":
		return "This field is required"
	case "min":
		return "Value is below minimum (" + fe.Param() + ")"
	case "max":
		return "Value exceeds maximum (" + fe.Param() + ")"
	case "oneof":
		return "Must be one of: " + fe.Param()
	case "email":
		return "Invalid email format"
	case "gte":
		return "Must be greater than or equal to " + fe.Param()
	case "lte":
		return "Must be less than or equal to " + fe.Param()
	default:
		return "Invalid value for " + fe.Field()
	}
}

// ValidateBody parses body and validates, returning errors if invalid
func ValidateBody(c *fiber.Ctx, out interface{}) error {
	if err := c.BodyParser(out); err != nil {
		return fiber.NewError(400, "Invalid request body")
	}

	errors := ValidateStruct(out)
	if len(errors) > 0 {
		return c.Status(400).JSON(fiber.Map{
			"success": false,
			"errors":  errors,
		})
	}

	return nil
}
