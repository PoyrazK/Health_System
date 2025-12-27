package unit

import (
	"healthcare-backend/pkg/cache"
	"testing"
	"time"
)

// TestRedis_SetGet tests basic set/get operations
func TestRedis_SetGet(t *testing.T) {
	if cache.RedisClient == nil {
		t.Skip("Redis client not initialized, skipping test")
	}
	
	key := "test:key:1"
	value := "test_value"
	
	err := cache.Set(key, value, 1*time.Minute)
	if err != nil {
		t.Fatalf("Failed to set value: %v", err)
	}
	
	result, err := cache.Get(key)
	if err != nil {
		t.Fatalf("Failed to get value: %v", err)
	}
	
	if result != value {
		t.Errorf("Expected %s, got %s", value, result)
	}
	
	cache.Delete(key)
}

// TestRedis_Delete tests key deletion
func TestRedis_Delete(t *testing.T) {
	if cache.RedisClient == nil {
		t.Skip("Redis client not initialized, skipping test")
	}
	
	key := "test:key:delete"
	value := "to_be_deleted"
	
	cache.Set(key, value, 1*time.Minute)
	
	err := cache.Delete(key)
	if err != nil {
		t.Fatalf("Failed to delete key: %v", err)
	}
	
	_, err = cache.Get(key)
	if err == nil {
		t.Error("Expected error when getting deleted key, got nil")
	}
}

// TestRedis_Ping tests connection health check
func TestRedis_Ping(t *testing.T) {
	if cache.RedisClient == nil {
		err := cache.Ping()
		if err == nil {
			t.Error("Expected error when Redis not connected, got nil")
		}
		return
	}
	
	err := cache.Ping()
	if err != nil {
		t.Errorf("Ping failed: %v", err)
	}
}

// TestRedis_TTL tests that keys expire after TTL
func TestRedis_TTL(t *testing.T) {
	if cache.RedisClient == nil {
		t.Skip("Redis client not initialized, skipping test")
	}
	
	key := "test:key:ttl"
	value := "expires_soon"
	
	err := cache.Set(key, value, 1*time.Second)
	if err != nil {
		t.Fatalf("Failed to set value: %v", err)
	}
	
	_, err = cache.Get(key)
	if err != nil {
		t.Fatalf("Key should exist immediately after set: %v", err)
	}
	
	time.Sleep(2 * time.Second)
	
	_, err = cache.Get(key)
	if err == nil {
		t.Error("Expected key to be expired")
	}
}
