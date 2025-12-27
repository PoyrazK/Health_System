"""
WiFi DensePose Healthcare Service
Real-time human pose estimation through walls using WiFi signals
"""
import asyncio
import json
import random
import time
import math
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from config import settings, HEALTHCARE_CONFIG

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Keypoint(BaseModel):
    """Single body keypoint"""
    x: float  # 0-1 normalized
    y: float  # 0-1 normalized
    confidence: float  # 0-1


class PersonPose(BaseModel):
    """Full body pose for a single person"""
    person_id: str
    keypoints: Dict[str, Keypoint]  # keypoint_name -> Keypoint
    activity: str
    confidence: float
    room_id: Optional[str] = None
    zone: Optional[str] = None
    timestamp: datetime


class FallEvent(BaseModel):
    """Fall detection event"""
    event_id: str
    person_id: str
    room_id: Optional[str]
    severity: str  # "critical", "warning"
    confidence: float
    timestamp: datetime
    acknowledged: bool = False


class PoseStreamMessage(BaseModel):
    """WebSocket streaming message"""
    type: str  # "pose_update", "fall_alert", "activity_change"
    data: Any
    timestamp: datetime


class SystemStatus(BaseModel):
    """System health status"""
    status: str
    version: str
    mode: str
    fps: int
    active_persons: int
    fall_detection: bool
    uptime_seconds: float


# ============================================================================
# MOCK DATA GENERATOR (for demo without hardware)
# ============================================================================

class MockPoseGenerator:
    """Generates realistic mock pose data for demo purposes"""
    
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    
    ACTIVITIES = ["standing", "sitting", "lying_down", "walking"]
    
    def __init__(self, person_count: int = 3):
        self.person_count = person_count
        self.persons = {}
        self._init_persons()
    
    def _init_persons(self):
        """Initialize mock persons with random positions"""
        for i in range(self.person_count):
            person_id = f"person_{i+1}"
            self.persons[person_id] = {
                "base_x": random.uniform(0.2, 0.8),
                "base_y": random.uniform(0.2, 0.8),
                "activity": random.choice(self.ACTIVITIES),
                "activity_duration": 0,
                "room_id": f"room_{random.randint(101, 105)}"
            }
    
    def _get_skeleton_for_activity(self, activity: str, base_x: float, base_y: float, t: float) -> Dict[str, Keypoint]:
        """Generate keypoints based on activity"""
        keypoints = {}
        
        # Add small movement animation
        sway = math.sin(t * 2) * 0.01
        
        if activity == "standing":
            offsets = {
                "nose": (0, -0.25), "left_eye": (-0.02, -0.27), "right_eye": (0.02, -0.27),
                "left_ear": (-0.04, -0.25), "right_ear": (0.04, -0.25),
                "left_shoulder": (-0.08, -0.18), "right_shoulder": (0.08, -0.18),
                "left_elbow": (-0.12, -0.08), "right_elbow": (0.12, -0.08),
                "left_wrist": (-0.10, 0.02), "right_wrist": (0.10, 0.02),
                "left_hip": (-0.05, 0.05), "right_hip": (0.05, 0.05),
                "left_knee": (-0.05, 0.15), "right_knee": (0.05, 0.15),
                "left_ankle": (-0.05, 0.25), "right_ankle": (0.05, 0.25)
            }
        elif activity == "sitting":
            offsets = {
                "nose": (0, -0.15), "left_eye": (-0.02, -0.17), "right_eye": (0.02, -0.17),
                "left_ear": (-0.04, -0.15), "right_ear": (0.04, -0.15),
                "left_shoulder": (-0.08, -0.08), "right_shoulder": (0.08, -0.08),
                "left_elbow": (-0.15, 0.0), "right_elbow": (0.15, 0.0),
                "left_wrist": (-0.12, 0.08), "right_wrist": (0.12, 0.08),
                "left_hip": (-0.06, 0.05), "right_hip": (0.06, 0.05),
                "left_knee": (-0.10, 0.12), "right_knee": (0.10, 0.12),
                "left_ankle": (-0.08, 0.20), "right_ankle": (0.08, 0.20)
            }
        elif activity == "lying_down":
            offsets = {
                "nose": (-0.25, 0), "left_eye": (-0.27, -0.02), "right_eye": (-0.27, 0.02),
                "left_ear": (-0.25, -0.04), "right_ear": (-0.25, 0.04),
                "left_shoulder": (-0.18, -0.08), "right_shoulder": (-0.18, 0.08),
                "left_elbow": (-0.08, -0.12), "right_elbow": (-0.08, 0.12),
                "left_wrist": (0.02, -0.10), "right_wrist": (0.02, 0.10),
                "left_hip": (0.05, -0.05), "right_hip": (0.05, 0.05),
                "left_knee": (0.15, -0.05), "right_knee": (0.15, 0.05),
                "left_ankle": (0.25, -0.05), "right_ankle": (0.25, 0.05)
            }
        else:  # walking
            walk_offset = math.sin(t * 4) * 0.03
            offsets = {
                "nose": (walk_offset, -0.25), "left_eye": (-0.02 + walk_offset, -0.27), "right_eye": (0.02 + walk_offset, -0.27),
                "left_ear": (-0.04, -0.25), "right_ear": (0.04, -0.25),
                "left_shoulder": (-0.08, -0.18), "right_shoulder": (0.08, -0.18),
                "left_elbow": (-0.12 - walk_offset, -0.08), "right_elbow": (0.12 + walk_offset, -0.08),
                "left_wrist": (-0.10 - walk_offset*2, 0.02), "right_wrist": (0.10 + walk_offset*2, 0.02),
                "left_hip": (-0.05, 0.05), "right_hip": (0.05, 0.05),
                "left_knee": (-0.05 - walk_offset, 0.15), "right_knee": (0.05 + walk_offset, 0.15),
                "left_ankle": (-0.05 - walk_offset*2, 0.25), "right_ankle": (0.05 + walk_offset*2, 0.25)
            }
        
        for name in self.KEYPOINT_NAMES:
            ox, oy = offsets.get(name, (0, 0))
            keypoints[name] = Keypoint(
                x=max(0, min(1, base_x + ox + sway)),
                y=max(0, min(1, base_y + oy)),
                confidence=random.uniform(0.85, 0.99)
            )
        
        return keypoints
    
    def generate_poses(self) -> List[PersonPose]:
        """Generate current pose data for all persons"""
        t = time.time()
        poses = []
        
        for person_id, data in self.persons.items():
            # Occasionally change activity
            data["activity_duration"] += 1
            if data["activity_duration"] > random.randint(100, 300):
                data["activity"] = random.choice(self.ACTIVITIES)
                data["activity_duration"] = 0
            
            # Small random movement
            data["base_x"] += random.uniform(-0.005, 0.005)
            data["base_y"] += random.uniform(-0.002, 0.002)
            data["base_x"] = max(0.1, min(0.9, data["base_x"]))
            data["base_y"] = max(0.1, min(0.9, data["base_y"]))
            
            keypoints = self._get_skeleton_for_activity(
                data["activity"], data["base_x"], data["base_y"], t
            )
            
            # Determine zone
            zone = self._get_zone(data["base_x"], data["base_y"])
            
            poses.append(PersonPose(
                person_id=person_id,
                keypoints=keypoints,
                activity=data["activity"],
                confidence=random.uniform(0.88, 0.98),
                room_id=data["room_id"],
                zone=zone,
                timestamp=datetime.now()
            ))
        
        return poses
    
    def _get_zone(self, x: float, y: float) -> str:
        """Determine which room zone the person is in"""
        for zone_name, bounds in HEALTHCARE_CONFIG["room_zones"].items():
            if bounds["x"][0] <= x <= bounds["x"][1] and bounds["y"][0] <= y <= bounds["y"][1]:
                return zone_name
        return "unknown"
    
    def simulate_fall(self, person_id: str) -> Optional[FallEvent]:
        """Simulate a fall event for demo purposes"""
        if person_id not in self.persons:
            return None
        
        data = self.persons[person_id]
        data["activity"] = "fallen"
        
        return FallEvent(
            event_id=f"fall_{int(time.time()*1000)}",
            person_id=person_id,
            room_id=data["room_id"],
            severity="critical",
            confidence=random.uniform(0.90, 0.99),
            timestamp=datetime.now()
        )


# ============================================================================
# WIFI DENSEPOSE SERVICE
# ============================================================================

class WiFiDensePoseService:
    """Main service for WiFi-based pose estimation"""
    
    def __init__(self):
        self.start_time = time.time()
        self.mock_generator = MockPoseGenerator(settings.mock_person_count)
        self.fall_events: List[FallEvent] = []
        self.connected_clients: List[WebSocket] = []
        self._running = False
    
    async def start(self):
        """Start the pose estimation service"""
        self._running = True
        logger.info(f"WiFi DensePose Service started in {'MOCK' if settings.use_mock_data else 'LIVE'} mode")
        
        if settings.use_mock_data:
            logger.info(f"Mock mode: Tracking {settings.mock_person_count} virtual persons")
    
    async def stop(self):
        """Stop the pose estimation service"""
        self._running = False
        logger.info("WiFi DensePose Service stopped")
    
    def get_status(self) -> SystemStatus:
        """Get current system status"""
        return SystemStatus(
            status="healthy",
            version=settings.service_version,
            mode="mock" if settings.use_mock_data else "live",
            fps=settings.frame_rate,
            active_persons=len(self.mock_generator.persons),
            fall_detection=settings.fall_detection_enabled,
            uptime_seconds=time.time() - self.start_time
        )
    
    def get_current_poses(self) -> List[PersonPose]:
        """Get current pose estimations"""
        if settings.use_mock_data:
            return self.mock_generator.generate_poses()
        else:
            # TODO: Integrate with real wifi-densepose library
            # from wifi_densepose import DensePoseEstimator
            # return self.estimator.get_poses()
            raise NotImplementedError("Live mode requires CSI hardware")
    
    def get_fall_events(self, limit: int = 10) -> List[FallEvent]:
        """Get recent fall events"""
        return sorted(self.fall_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def simulate_fall(self, person_id: str) -> Optional[FallEvent]:
        """Simulate a fall for demo purposes"""
        event = self.mock_generator.simulate_fall(person_id)
        if event:
            self.fall_events.append(event)
            asyncio.create_task(self._broadcast_fall_alert(event))
        return event
    
    def acknowledge_fall(self, event_id: str) -> bool:
        """Acknowledge a fall event"""
        for event in self.fall_events:
            if event.event_id == event_id:
                event.acknowledged = True
                return True
        return False
    
    async def _broadcast_fall_alert(self, event: FallEvent):
        """Broadcast fall alert to all connected WebSocket clients"""
        message = PoseStreamMessage(
            type="fall_alert",
            data=event.model_dump(),
            timestamp=datetime.now()
        )
        
        for client in self.connected_clients:
            try:
                await client.send_json(message.model_dump(mode="json"))
            except Exception as e:
                logger.error(f"Failed to send fall alert: {e}")
    
    async def stream_poses(self, websocket: WebSocket):
        """Stream pose data to a WebSocket client"""
        self.connected_clients.append(websocket)
        
        try:
            while True:
                poses = self.get_current_poses()
                message = PoseStreamMessage(
                    type="pose_update",
                    data=[p.model_dump() for p in poses],
                    timestamp=datetime.now()
                )
                await websocket.send_json(message.model_dump(mode="json"))
                await asyncio.sleep(1.0 / settings.frame_rate)
        finally:
            self.connected_clients.remove(websocket)


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Global service instance
pose_service = WiFiDensePoseService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    await pose_service.start()
    yield
    await pose_service.stop()


app = FastAPI(
    title="WiFi DensePose Healthcare Service",
    description="Real-time human pose estimation through walls using WiFi signals",
    version=settings.service_version,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """Service health check"""
    return pose_service.get_status()


@app.get("/api/poses", response_model=List[PersonPose])
async def get_poses():
    """Get current pose estimations for all tracked persons"""
    return pose_service.get_current_poses()


@app.get("/api/poses/{person_id}", response_model=PersonPose)
async def get_person_pose(person_id: str):
    """Get pose for a specific person"""
    poses = pose_service.get_current_poses()
    for pose in poses:
        if pose.person_id == person_id:
            return pose
    raise HTTPException(status_code=404, detail=f"Person {person_id} not found")


@app.get("/api/falls", response_model=List[FallEvent])
async def get_fall_events(limit: int = 10):
    """Get recent fall detection events"""
    return pose_service.get_fall_events(limit)


@app.post("/api/falls/simulate/{person_id}", response_model=FallEvent)
async def simulate_fall(person_id: str):
    """Simulate a fall event for demo purposes"""
    event = pose_service.simulate_fall(person_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Person {person_id} not found")
    return event


@app.post("/api/falls/{event_id}/acknowledge")
async def acknowledge_fall(event_id: str):
    """Acknowledge a fall event"""
    if pose_service.acknowledge_fall(event_id):
        return {"status": "acknowledged", "event_id": event_id}
    raise HTTPException(status_code=404, detail=f"Event {event_id} not found")


@app.get("/api/activities")
async def get_activities():
    """Get activity summary for all tracked persons"""
    poses = pose_service.get_current_poses()
    activities = {}
    for pose in poses:
        if pose.activity not in activities:
            activities[pose.activity] = []
        activities[pose.activity].append({
            "person_id": pose.person_id,
            "room_id": pose.room_id,
            "confidence": pose.confidence
        })
    return activities


@app.get("/api/rooms")
async def get_room_occupancy():
    """Get room occupancy information"""
    poses = pose_service.get_current_poses()
    rooms = {}
    for pose in poses:
        room_id = pose.room_id or "unknown"
        if room_id not in rooms:
            rooms[room_id] = {"persons": [], "zones": {}}
        rooms[room_id]["persons"].append({
            "person_id": pose.person_id,
            "activity": pose.activity,
            "zone": pose.zone
        })
        
        if pose.zone:
            if pose.zone not in rooms[room_id]["zones"]:
                rooms[room_id]["zones"][pose.zone] = 0
            rooms[room_id]["zones"][pose.zone] += 1
    
    return rooms


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """Real-time pose streaming via WebSocket"""
    await websocket.accept()
    logger.info("New WebSocket client connected")
    
    try:
        await pose_service.stream_poses(websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
