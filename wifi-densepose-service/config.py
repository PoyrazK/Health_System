"""
WiFi DensePose Service Configuration
Healthcare Domain Optimized Settings
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """WiFi DensePose service configuration"""
    
    # Service Settings
    service_name: str = "wifi-densepose-service"
    service_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    
    # Domain Configuration
    domain: str = "healthcare"  # healthcare, fitness, smart_home, security
    
    # WiFi DensePose Settings
    use_mock_data: bool = True  # True for demo mode without real hardware
    mock_person_count: int = 3
    frame_rate: int = 30  # FPS
    
    # CSI Hardware Settings (for production)
    csi_interface: Optional[str] = None  # e.g., "wlan0"
    router_ips: list = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    
    # Analytics Settings
    fall_detection_enabled: bool = True
    fall_detection_threshold: float = 0.8
    activity_recognition_enabled: bool = True
    
    # Healthcare Specific
    patient_room_mapping_enabled: bool = True
    alert_webhook_url: Optional[str] = None
    
    # Backend Integration
    backend_url: str = "http://localhost:8080"
    
    # Redis (for state management)
    redis_url: str = "redis://localhost:6379"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "WIFI_POSE_"
        env_file = ".env"


settings = Settings()


# Healthcare domain specific configuration
HEALTHCARE_CONFIG = {
    "sensitivity": "high",  # More sensitive fall detection
    "min_confidence": 0.7,
    "alert_cooldown_seconds": 30,
    "keypoints": 17,  # COCO format
    "tracked_activities": [
        "standing",
        "sitting",
        "lying_down",
        "walking",
        "falling",
        "fallen"
    ],
    "critical_events": [
        "falling",
        "fallen"
    ],
    "room_zones": {
        "bed_area": {"x": [0, 0.4], "y": [0, 1]},
        "bathroom": {"x": [0.7, 1], "y": [0, 0.4]},
        "walking_area": {"x": [0.4, 0.7], "y": [0, 1]}
    }
}
