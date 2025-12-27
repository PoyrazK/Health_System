"""
WiFi DensePose Service Configuration
Healthcare Domain Optimized Settings
Auto-fallback: Uses mock data if no CSI hardware detected
"""
import os
import subprocess
from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def detect_csi_hardware() -> bool:
    """
    Detect if CSI-capable WiFi hardware is available.
    Returns True if real hardware is detected, False otherwise.
    """
    try:
        # Check for common CSI-capable interfaces
        # This checks for wireless interfaces that might support CSI
        result = subprocess.run(
            ["ls", "/sys/class/net"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        interfaces = result.stdout.strip().split('\n')
        wifi_interfaces = [iface for iface in interfaces if iface.startswith(('wlan', 'wlp', 'ath'))]
        
        if wifi_interfaces:
            # Check if nexmon CSI tool is available (common for CSI extraction)
            nexmon_check = subprocess.run(
                ["which", "nexutil"],
                capture_output=True,
                timeout=5
            )
            if nexmon_check.returncode == 0:
                logger.info(f"CSI hardware detected: {wifi_interfaces} with nexmon support")
                return True
            
            # Check for Intel 5300 CSI tool
            intel_check = subprocess.run(
                ["which", "log_to_file"],
                capture_output=True,
                timeout=5
            )
            if intel_check.returncode == 0:
                logger.info(f"CSI hardware detected: {wifi_interfaces} with Intel CSI tool")
                return True
        
        logger.info("No CSI hardware detected, falling back to mock mode")
        return False
        
    except Exception as e:
        logger.warning(f"Hardware detection failed: {e}, using mock mode")
        return False


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
    # "auto" means detect hardware automatically
    # "true" forces mock mode
    # "false" forces live mode (will fail if no hardware)
    use_mock_data: str = "auto"  # "auto", "true", or "false"
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
    
    def should_use_mock(self) -> bool:
        """Determine if mock mode should be used based on config and hardware detection"""
        if self.use_mock_data.lower() == "true":
            return True
        elif self.use_mock_data.lower() == "false":
            return False
        else:  # "auto" - detect hardware
            has_hardware = detect_csi_hardware()
            return not has_hardware


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
