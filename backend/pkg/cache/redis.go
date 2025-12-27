package cache

import (
	"context"
	"log"
	"time"

	"github.com/redis/go-redis/v9"
)

var (
	RedisClient *redis.Client
	ctx         = context.Background()
)

// InitRedis initializes the Redis client
func InitRedis(url string) {
	RedisClient = redis.NewClient(&redis.Options{
		Addr:         url,
		Password:     "", // no password set
		DB:           0,  // use default DB
		PoolSize:     10, // connection pool size
		MinIdleConns: 3,
	})

	// Test connection
	_, err := RedisClient.Ping(ctx).Result()
	if err != nil {
		log.Printf("⚠️ Redis connection failed: %v", err)
	} else {
		log.Println("🔴 Redis connected successfully")
	}
}

// Get returns the value for a given key
func Get(key string) (string, error) {
	if RedisClient == nil {
		return "", context.DeadlineExceeded
	}
	return RedisClient.Get(ctx, key).Result()
}

// Set stores a value for a given key with TTL
func Set(key string, value interface{}, ttl time.Duration) error {
	if RedisClient == nil {
		return context.DeadlineExceeded
	}
	return RedisClient.Set(ctx, key, value, ttl).Err()
}

// Delete removes a key
func Delete(key string) error {
	if RedisClient == nil {
		return context.DeadlineExceeded
	}
	return RedisClient.Del(ctx, key).Err()
}

// Ping checks if Redis is alive
func Ping() error {
	if RedisClient == nil {
		return context.DeadlineExceeded
	}
	return RedisClient.Ping(ctx).Err()
}
