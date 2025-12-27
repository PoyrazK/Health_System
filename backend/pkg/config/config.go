package config

import (
	"log"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

// Config holds all application configuration
type Config struct {
	// Server
	ServerPort string

	// Database
	DBHost       string
	DBUser       string
	DBPassword   string
	DBName       string
	DBPort       string

	// External Services
	MLServiceURL string
	RedisURL     string
	NatsURL      string

	// Feature Flags
	EnableAuditLog  bool
	EnableWebSocket bool

	// Rate Limits
	RateLimitGlobalMax   int
	RateLimitMLMax       int
	RateLimitFeedbackMax int
}

// Global config instance
var AppConfig *Config

// Load initializes configuration from environment variables
func Load() *Config {
	// Try to load .env file (ignore error if not found)
	if err := godotenv.Load(); err != nil {
		log.Println("ℹ️ No .env file found, using environment variables")
	}

	config := &Config{
		// Server
		ServerPort: getEnv("SERVER_PORT", "3000"),

		// Database
		DBHost:       getEnv("DB_HOST", "localhost"),
		DBUser:       getEnv("DB_USER", "postgres"),
		DBPassword:   getEnv("DB_PASSWORD", "postgres"),
		DBName:       getEnv("DB_NAME", "healthcare"),
		DBPort:       getEnv("DB_PORT", "5432"),

		// External Services
		MLServiceURL: getEnv("ML_SERVICE_URL", "http://127.0.0.1:8000"),
		RedisURL:     getEnv("REDIS_URL", "localhost:6379"),
		NatsURL:      getEnv("NATS_URL", "nats://localhost:4222"),

		// Feature Flags
		EnableAuditLog:  getEnvBool("ENABLE_AUDIT_LOG", true),
		EnableWebSocket: getEnvBool("ENABLE_WEBSOCKET", true),

		// Rate Limits
		RateLimitGlobalMax:   getEnvInt("RATE_LIMIT_GLOBAL_MAX", 100),
		RateLimitMLMax:       getEnvInt("RATE_LIMIT_ML_MAX", 20),
		RateLimitFeedbackMax: getEnvInt("RATE_LIMIT_FEEDBACK_MAX", 10),
	}

	AppConfig = config

	log.Printf("⚙️ Config loaded: Port=%s, DB=%s:%s, ML=%s", 
		config.ServerPort, 
		config.DBHost,
		config.DBPort,
		config.MLServiceURL,
	)

	return config
}

// getEnv returns environment variable or default value
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// getEnvBool returns environment variable as bool or default value
func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		b, err := strconv.ParseBool(value)
		if err == nil {
			return b
		}
	}
	return defaultValue
}

// getEnvInt returns environment variable as int or default value
func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		i, err := strconv.Atoi(value)
		if err == nil {
			return i
		}
	}
	return defaultValue
}
