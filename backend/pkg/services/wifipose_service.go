package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// WiFiPoseServiceURL is the URL of the WiFi DensePose microservice
const WiFiPoseServiceURL = "http://localhost:8001"

// WiFiPoseService communicates with the WiFi DensePose microservice
type WiFiPoseService struct {
	BaseURL    string
	HTTPClient *http.Client
}

// Keypoint represents a single body keypoint
type Keypoint struct {
	X          float64 `json:"x"`
	Y          float64 `json:"y"`
	Confidence float64 `json:"confidence"`
}

// PersonPose represents full body pose for a person
type PersonPose struct {
	PersonID   string              `json:"person_id"`
	Keypoints  map[string]Keypoint `json:"keypoints"`
	Activity   string              `json:"activity"`
	Confidence float64             `json:"confidence"`
	RoomID     *string             `json:"room_id"`
	Zone       *string             `json:"zone"`
	Timestamp  time.Time           `json:"timestamp"`
}

// FallEvent represents a fall detection event
type FallEvent struct {
	EventID      string    `json:"event_id"`
	PersonID     string    `json:"person_id"`
	RoomID       *string   `json:"room_id"`
	Severity     string    `json:"severity"`
	Confidence   float64   `json:"confidence"`
	Timestamp    time.Time `json:"timestamp"`
	Acknowledged bool      `json:"acknowledged"`
}

// SystemStatus represents the WiFi Pose service status
type SystemStatus struct {
	Status        string  `json:"status"`
	Version       string  `json:"version"`
	Mode          string  `json:"mode"`
	FPS           int     `json:"fps"`
	ActivePersons int     `json:"active_persons"`
	FallDetection bool    `json:"fall_detection"`
	UptimeSeconds float64 `json:"uptime_seconds"`
}

// ActivitySummary represents activity information
type ActivitySummary map[string][]struct {
	PersonID   string  `json:"person_id"`
	RoomID     *string `json:"room_id"`
	Confidence float64 `json:"confidence"`
}

// RoomOccupancy represents room occupancy information
type RoomOccupancy map[string]struct {
	Persons []struct {
		PersonID string  `json:"person_id"`
		Activity string  `json:"activity"`
		Zone     *string `json:"zone"`
	} `json:"persons"`
	Zones map[string]int `json:"zones"`
}

// NewWiFiPoseService creates a new WiFi Pose service client
func NewWiFiPoseService(baseURL string) *WiFiPoseService {
	if baseURL == "" {
		baseURL = WiFiPoseServiceURL
	}
	return &WiFiPoseService{
		BaseURL: baseURL,
		HTTPClient: &http.Client{
			Timeout: 5 * time.Second,
		},
	}
}

// GetStatus fetches the service status
func (s *WiFiPoseService) GetStatus() (*SystemStatus, error) {
	resp, err := s.HTTPClient.Get(s.BaseURL + "/health")
	if err != nil {
		return nil, fmt.Errorf("failed to connect to WiFi Pose service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("WiFi Pose service returned status %d", resp.StatusCode)
	}

	var status SystemStatus
	if err := json.NewDecoder(resp.Body).Decode(&status); err != nil {
		return nil, fmt.Errorf("failed to decode status response: %w", err)
	}

	return &status, nil
}

// GetPoses fetches current pose estimations
func (s *WiFiPoseService) GetPoses() ([]PersonPose, error) {
	resp, err := s.HTTPClient.Get(s.BaseURL + "/api/poses")
	if err != nil {
		return nil, fmt.Errorf("failed to get poses: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("poses request failed with status %d", resp.StatusCode)
	}

	var poses []PersonPose
	if err := json.NewDecoder(resp.Body).Decode(&poses); err != nil {
		return nil, fmt.Errorf("failed to decode poses: %w", err)
	}

	return poses, nil
}

// GetPersonPose fetches pose for a specific person
func (s *WiFiPoseService) GetPersonPose(personID string) (*PersonPose, error) {
	resp, err := s.HTTPClient.Get(s.BaseURL + "/api/poses/" + personID)
	if err != nil {
		return nil, fmt.Errorf("failed to get person pose: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return nil, fmt.Errorf("person %s not found", personID)
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("person pose request failed with status %d", resp.StatusCode)
	}

	var pose PersonPose
	if err := json.NewDecoder(resp.Body).Decode(&pose); err != nil {
		return nil, fmt.Errorf("failed to decode person pose: %w", err)
	}

	return &pose, nil
}

// GetFallEvents fetches recent fall events
func (s *WiFiPoseService) GetFallEvents(limit int) ([]FallEvent, error) {
	url := fmt.Sprintf("%s/api/falls?limit=%d", s.BaseURL, limit)
	resp, err := s.HTTPClient.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to get fall events: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("fall events request failed with status %d", resp.StatusCode)
	}

	var events []FallEvent
	if err := json.NewDecoder(resp.Body).Decode(&events); err != nil {
		return nil, fmt.Errorf("failed to decode fall events: %w", err)
	}

	return events, nil
}

// SimulateFall triggers a fall simulation
func (s *WiFiPoseService) SimulateFall(personID string) (*FallEvent, error) {
	url := fmt.Sprintf("%s/api/falls/simulate/%s", s.BaseURL, personID)
	resp, err := s.HTTPClient.Post(url, "application/json", nil)
	if err != nil {
		return nil, fmt.Errorf("failed to simulate fall: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("simulate fall request failed with status %d", resp.StatusCode)
	}

	var event FallEvent
	if err := json.NewDecoder(resp.Body).Decode(&event); err != nil {
		return nil, fmt.Errorf("failed to decode fall event: %w", err)
	}

	return &event, nil
}

// AcknowledgeFall marks a fall event as acknowledged
func (s *WiFiPoseService) AcknowledgeFall(eventID string) error {
	url := fmt.Sprintf("%s/api/falls/%s/acknowledge", s.BaseURL, eventID)
	resp, err := s.HTTPClient.Post(url, "application/json", nil)
	if err != nil {
		return fmt.Errorf("failed to acknowledge fall: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound {
		return fmt.Errorf("event %s not found", eventID)
	}
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("acknowledge request failed with status %d", resp.StatusCode)
	}

	return nil
}

// GetActivities fetches activity summary
func (s *WiFiPoseService) GetActivities() (map[string]interface{}, error) {
	resp, err := s.HTTPClient.Get(s.BaseURL + "/api/activities")
	if err != nil {
		return nil, fmt.Errorf("failed to get activities: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("activities request failed with status %d", resp.StatusCode)
	}

	var activities map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&activities); err != nil {
		return nil, fmt.Errorf("failed to decode activities: %w", err)
	}

	return activities, nil
}

// GetRoomOccupancy fetches room occupancy information
func (s *WiFiPoseService) GetRoomOccupancy() (map[string]interface{}, error) {
	resp, err := s.HTTPClient.Get(s.BaseURL + "/api/rooms")
	if err != nil {
		return nil, fmt.Errorf("failed to get room occupancy: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("room occupancy request failed with status %d", resp.StatusCode)
	}

	var rooms map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&rooms); err != nil {
		return nil, fmt.Errorf("failed to decode room occupancy: %w", err)
	}

	return rooms, nil
}
