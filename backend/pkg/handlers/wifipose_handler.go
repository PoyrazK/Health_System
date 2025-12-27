package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"healthcare-backend/pkg/services"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/websocket/v2"
)

// WiFiPoseHandler handles WiFi DensePose related requests
type WiFiPoseHandler struct {
	Service    *services.WiFiPoseService
	wsClients  map[*websocket.Conn]bool
	wsMutex    sync.RWMutex
	broadcast  chan []byte
}

// NewWiFiPoseHandler creates a new WiFi Pose handler
func NewWiFiPoseHandler(service *services.WiFiPoseService) *WiFiPoseHandler {
	h := &WiFiPoseHandler{
		Service:   service,
		wsClients: make(map[*websocket.Conn]bool),
		broadcast: make(chan []byte, 100),
	}
	
	// Start broadcast goroutine
	go h.runBroadcaster()
	
	return h
}

// runBroadcaster sends messages to all connected WebSocket clients
func (h *WiFiPoseHandler) runBroadcaster() {
	for {
		message := <-h.broadcast
		h.wsMutex.RLock()
		for client := range h.wsClients {
			if err := client.WriteMessage(websocket.TextMessage, message); err != nil {
				log.Printf("WebSocket broadcast error: %v", err)
			}
		}
		h.wsMutex.RUnlock()
	}
}

// ============================================================================
// REST Endpoints
// ============================================================================

// GetStatus returns the WiFi DensePose service status
// GET /api/wifi-pose/status
func (h *WiFiPoseHandler) GetStatus(c *fiber.Ctx) error {
	status, err := h.Service.GetStatus()
	if err != nil {
		return c.Status(503).JSON(fiber.Map{
			"error":   "WiFi Pose service unavailable",
			"details": err.Error(),
		})
	}
	return c.JSON(status)
}

// GetPoses returns current pose estimations
// GET /api/wifi-pose/poses
func (h *WiFiPoseHandler) GetPoses(c *fiber.Ctx) error {
	poses, err := h.Service.GetPoses()
	if err != nil {
		return c.Status(503).JSON(fiber.Map{
			"error":   "Failed to get poses",
			"details": err.Error(),
		})
	}
	return c.JSON(poses)
}

// GetPersonPose returns pose for a specific person
// GET /api/wifi-pose/poses/:personId
func (h *WiFiPoseHandler) GetPersonPose(c *fiber.Ctx) error {
	personID := c.Params("personId")
	if personID == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Person ID required"})
	}
	
	pose, err := h.Service.GetPersonPose(personID)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{
			"error":   "Person not found",
			"details": err.Error(),
		})
	}
	return c.JSON(pose)
}

// GetFallEvents returns recent fall detection events
// GET /api/wifi-pose/falls
func (h *WiFiPoseHandler) GetFallEvents(c *fiber.Ctx) error {
	limit := c.QueryInt("limit", 10)
	
	events, err := h.Service.GetFallEvents(limit)
	if err != nil {
		return c.Status(503).JSON(fiber.Map{
			"error":   "Failed to get fall events",
			"details": err.Error(),
		})
	}
	return c.JSON(events)
}

// SimulateFall triggers a fall simulation for demo purposes
// POST /api/wifi-pose/falls/simulate/:personId
func (h *WiFiPoseHandler) SimulateFall(c *fiber.Ctx) error {
	personID := c.Params("personId")
	if personID == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Person ID required"})
	}
	
	event, err := h.Service.SimulateFall(personID)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{
			"error":   "Failed to simulate fall",
			"details": err.Error(),
		})
	}
	
	// Broadcast fall alert
	alertMsg, _ := json.Marshal(fiber.Map{
		"type":      "fall_alert",
		"data":      event,
		"timestamp": time.Now(),
	})
	h.broadcast <- alertMsg
	
	return c.JSON(event)
}

// AcknowledgeFall marks a fall event as acknowledged
// POST /api/wifi-pose/falls/:eventId/acknowledge
func (h *WiFiPoseHandler) AcknowledgeFall(c *fiber.Ctx) error {
	eventID := c.Params("eventId")
	if eventID == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Event ID required"})
	}
	
	err := h.Service.AcknowledgeFall(eventID)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{
			"error":   "Event not found",
			"details": err.Error(),
		})
	}
	
	return c.JSON(fiber.Map{
		"status":   "acknowledged",
		"event_id": eventID,
	})
}

// GetActivities returns activity summary
// GET /api/wifi-pose/activities
func (h *WiFiPoseHandler) GetActivities(c *fiber.Ctx) error {
	activities, err := h.Service.GetActivities()
	if err != nil {
		return c.Status(503).JSON(fiber.Map{
			"error":   "Failed to get activities",
			"details": err.Error(),
		})
	}
	return c.JSON(activities)
}

// GetRoomOccupancy returns room occupancy information
// GET /api/wifi-pose/rooms
func (h *WiFiPoseHandler) GetRoomOccupancy(c *fiber.Ctx) error {
	rooms, err := h.Service.GetRoomOccupancy()
	if err != nil {
		return c.Status(503).JSON(fiber.Map{
			"error":   "Failed to get room occupancy",
			"details": err.Error(),
		})
	}
	return c.JSON(rooms)
}

// ============================================================================
// WebSocket Endpoint
// ============================================================================

// HandleWebSocket handles the WebSocket connection for real-time pose streaming
func (h *WiFiPoseHandler) HandleWebSocket(c *websocket.Conn) {
	// Register client
	h.wsMutex.Lock()
	h.wsClients[c] = true
	h.wsMutex.Unlock()
	
	log.Printf("WiFi Pose WebSocket client connected: %s", c.RemoteAddr())
	
	defer func() {
		h.wsMutex.Lock()
		delete(h.wsClients, c)
		h.wsMutex.Unlock()
		c.Close()
		log.Printf("WiFi Pose WebSocket client disconnected: %s", c.RemoteAddr())
	}()
	
	// Start streaming poses
	ticker := time.NewTicker(33 * time.Millisecond) // ~30 FPS
	defer ticker.Stop()
	
	done := make(chan struct{})
	
	// Read messages (for keeping connection alive and handling commands)
	go func() {
		for {
			_, _, err := c.ReadMessage()
			if err != nil {
				close(done)
				return
			}
		}
	}()
	
	for {
		select {
		case <-done:
			return
		case <-ticker.C:
			poses, err := h.Service.GetPoses()
			if err != nil {
				log.Printf("Error getting poses for WebSocket: %v", err)
				continue
			}
			
			message := fiber.Map{
				"type":      "pose_update",
				"data":      poses,
				"timestamp": time.Now(),
			}
			
			msgBytes, err := json.Marshal(message)
			if err != nil {
				continue
			}
			
			if err := c.WriteMessage(websocket.TextMessage, msgBytes); err != nil {
				return
			}
		}
	}
}

// RegisterRoutes registers all WiFi Pose routes
func (h *WiFiPoseHandler) RegisterRoutes(app *fiber.App) {
	api := app.Group("/api/wifi-pose")
	
	// REST endpoints
	api.Get("/status", h.GetStatus)
	api.Get("/poses", h.GetPoses)
	api.Get("/poses/:personId", h.GetPersonPose)
	api.Get("/falls", h.GetFallEvents)
	api.Post("/falls/simulate/:personId", h.SimulateFall)
	api.Post("/falls/:eventId/acknowledge", h.AcknowledgeFall)
	api.Get("/activities", h.GetActivities)
	api.Get("/rooms", h.GetRoomOccupancy)
	
	// WebSocket endpoint
	app.Get("/ws/wifi-pose", websocket.New(h.HandleWebSocket))
	
	fmt.Println("📡 WiFi DensePose routes registered")
}
