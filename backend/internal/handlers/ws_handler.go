package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"

	"healthcare-backend/internal/cache"
	"github.com/gofiber/contrib/websocket"
)

type WebSocketHandler struct {
	mu          sync.RWMutex
	conns       map[*websocket.Conn]bool
	patientSubs map[uint][]*websocket.Conn // patientID -> list of connections
}

func NewWebSocketHandler() *WebSocketHandler {
	return &WebSocketHandler{
		conns:       make(map[*websocket.Conn]bool),
		patientSubs: make(map[uint][]*websocket.Conn),
	}
}

func (h *WebSocketHandler) HandleConnection(c *websocket.Conn) {
	h.mu.Lock()
	h.conns[c] = true
	h.mu.Unlock()

	defer func() {
		h.mu.Lock()
		delete(h.conns, c)
		// Clean up subscriptions
		for id, subs := range h.patientSubs {
			for i, sub := range subs {
				if sub == c {
					h.patientSubs[id] = append(subs[:i], subs[i+1:]...)
					break
				}
			}
		}
		h.mu.Unlock()
		c.Close()
	}()

	for {
		_, msg, err := c.ReadMessage()
		if err != nil {
			break
		}

		var payload struct {
			Type      string `json:"type"`
			PatientID uint   `json:"patient_id"`
		}

		if err := json.Unmarshal(msg, &payload); err != nil {
			log.Printf("WS error: invalid payload: %v", err)
			continue
		}

		if payload.Type == "subscribe" {
			h.mu.Lock()
			h.patientSubs[payload.PatientID] = append(h.patientSubs[payload.PatientID], c)
			h.mu.Unlock()
			log.Printf("WS: Client subscribed to patient %d", payload.PatientID)
		}
	}
}

// StartGlobalListener listens for diagnosis updates on Redis and broadcasts them locally
func (h *WebSocketHandler) StartGlobalListener() {
	pubsub := cache.RedisClient.Subscribe(context.Background(), "diagnosis_updates")
	ch := pubsub.Channel()

	go func() {
		log.Println("🌐 WS Handler: Listening for global diagnosis updates on Redis...")
		for msg := range ch {
			var update struct {
				PatientID uint   `json:"patient_id"`
				Diagnosis string `json:"diagnosis"`
				Status    string `json:"status"`
			}

			if err := json.Unmarshal([]byte(msg.Payload), &update); err != nil {
				log.Printf("❌ WS Handler: Redis msg unmarshal error: %v", err)
				continue
			}

			h.BroadcastDiagnosis(update.PatientID, update.Diagnosis, update.Status)
		}
	}()
}

func (h *WebSocketHandler) BroadcastDiagnosis(patientID uint, diagnosis string, status string) {
	h.mu.RLock()
	subs, ok := h.patientSubs[patientID]
	h.mu.RUnlock()

	if !ok || len(subs) == 0 {
		return
	}

	msg := struct {
		Type      string `json:"type"`
		PatientID uint   `json:"patient_id"`
		Diagnosis string `json:"diagnosis"`
		Status    string `json:"status"`
	}{
		Type:      "diagnosis_update",
		PatientID: patientID,
		Diagnosis: diagnosis,
		Status:    status,
	}

	payload, _ := json.Marshal(msg)

	for _, c := range subs {
		if err := c.WriteMessage(websocket.TextMessage, payload); err != nil {
			log.Printf("WS write error: %v", err)
		}
	}
}
