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

	// Feature Flags
	EnableAuditLog bool
	EnableWebSocket bool
}

// Global config instance
var AppConfig *Config

// Load initializes configuration from environment variables
func Load() *Config {
	// Try to load .env file (ignore error if not found)
	_ = godotenv.Load()

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

		// Feature Flags
		EnableAuditLog:  getEnvBool("ENABLE_AUDIT_LOG", true),
		EnableWebSocket: getEnvBool("ENABLE_WEBSOCKET", true),
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
