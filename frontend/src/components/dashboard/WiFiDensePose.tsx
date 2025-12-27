'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import MediaPipeCameraModal from './MediaPipeCameraModal';

interface Keypoint {
    x: number;
    y: number;
    confidence: number;
}

interface PersonPose {
    person_id: string;
    keypoints: Record<string, Keypoint>;
    activity: string;
    confidence: number;
    room_id?: string;
    zone?: string;
    timestamp: string;
}

interface FallEvent {
    event_id: string;
    person_id: string;
    room_id?: string;
    severity: string;
    confidence: number;
    timestamp: string;
    acknowledged: boolean;
}

interface WiFiDensePoseProps {
    className?: string;
}

const SKELETON_CONNECTIONS = [
    ['left_shoulder', 'right_shoulder'],
    ['left_shoulder', 'left_elbow'],
    ['left_elbow', 'left_wrist'],
    ['right_shoulder', 'right_elbow'],
    ['right_elbow', 'right_wrist'],
    ['left_shoulder', 'left_hip'],
    ['right_shoulder', 'right_hip'],
    ['left_hip', 'right_hip'],
    ['left_hip', 'left_knee'],
    ['left_knee', 'left_ankle'],
    ['right_hip', 'right_knee'],
    ['right_knee', 'right_ankle'],
    ['nose', 'left_eye'],
    ['nose', 'right_eye'],
    ['left_eye', 'left_ear'],
    ['right_eye', 'right_ear'],
];

const ACTIVITY_COLORS: Record<string, string> = {
    standing: '#10B981',   // emerald
    sitting: '#3B82F6',    // blue
    walking: '#F59E0B',    // amber
    lying_down: '#8B5CF6', // purple
    fallen: '#EF4444',     // red
};

const ACTIVITY_LABELS: Record<string, string> = {
    standing: 'Ayakta',
    sitting: 'Oturuyor',
    walking: 'Yürüyor',
    lying_down: 'Uzanıyor',
    fallen: 'Düşmüş',
};

export default function WiFiDensePose({ className = '' }: WiFiDensePoseProps) {
    const [poses, setPoses] = useState<PersonPose[]>([]);
    const [fallAlerts, setFallAlerts] = useState<FallEvent[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [serviceStatus, setServiceStatus] = useState<string>('connecting');
    const [isCameraModalOpen, setIsCameraModalOpen] = useState(false);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    // Connect to WebSocket
    useEffect(() => {
        const connectWebSocket = () => {
            const ws = new WebSocket('ws://localhost:8001/ws/stream');

            ws.onopen = () => {
                setIsConnected(true);
                setServiceStatus('live');
            };

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);

                if (message.type === 'pose_update') {
                    setPoses(message.data);
                } else if (message.type === 'fall_alert') {
                    setFallAlerts(prev => [message.data, ...prev.slice(0, 4)]);
                }
            };

            ws.onerror = () => {
                setServiceStatus('error');
            };

            ws.onclose = () => {
                setIsConnected(false);
                setServiceStatus('disconnected');
                // Try reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };

            wsRef.current = ws;
        };

        // Check service health first
        fetch('http://localhost:8001/health')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'healthy') {
                    connectWebSocket();
                }
            })
            .catch(() => {
                setServiceStatus('offline');
            });

        return () => {
            wsRef.current?.close();
        };
    }, []);

    // Draw skeleton on canvas
    const drawSkeleton = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;

        // Clear canvas
        ctx.fillStyle = 'rgba(10, 15, 28, 0.9)';
        ctx.fillRect(0, 0, width, height);

        // Draw grid
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.1)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 10; i++) {
            ctx.beginPath();
            ctx.moveTo(i * width / 10, 0);
            ctx.lineTo(i * width / 10, height);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, i * height / 10);
            ctx.lineTo(width, i * height / 10);
            ctx.stroke();
        }

        // Draw each person
        poses.forEach((pose) => {
            const color = ACTIVITY_COLORS[pose.activity] || '#3B82F6';

            // Draw connections
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;

            SKELETON_CONNECTIONS.forEach(([from, to]) => {
                const fromKp = pose.keypoints[from];
                const toKp = pose.keypoints[to];

                if (fromKp && toKp) {
                    ctx.beginPath();
                    ctx.moveTo(fromKp.x * width, fromKp.y * height);
                    ctx.lineTo(toKp.x * width, toKp.y * height);
                    ctx.stroke();
                }
            });

            // Draw keypoints
            Object.entries(pose.keypoints).forEach(([name, kp]) => {
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(kp.x * width, kp.y * height, name === 'nose' ? 6 : 4, 0, Math.PI * 2);
                ctx.fill();

                // Draw glow effect for nose
                if (name === 'nose') {
                    ctx.fillStyle = `${color}40`;
                    ctx.beginPath();
                    ctx.arc(kp.x * width, kp.y * height, 12, 0, Math.PI * 2);
                    ctx.fill();
                }
            });

            // Draw person label
            const nose = pose.keypoints['nose'];
            if (nose) {
                ctx.fillStyle = 'white';
                ctx.font = '10px Inter, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText(
                    `${pose.person_id.replace('person_', 'P')} - ${ACTIVITY_LABELS[pose.activity] || pose.activity}`,
                    nose.x * width,
                    nose.y * height - 20
                );
            }
        });
    }, [poses]);

    useEffect(() => {
        drawSkeleton();
    }, [drawSkeleton]);

    // Handle canvas resize
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const resizeCanvas = () => {
            const parent = canvas.parentElement;
            if (parent) {
                canvas.width = parent.clientWidth;
                canvas.height = parent.clientHeight;
                drawSkeleton();
            }
        };

        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        return () => window.removeEventListener('resize', resizeCanvas);
    }, [drawSkeleton]);

    const getStatusColor = () => {
        switch (serviceStatus) {
            case 'live': return 'text-emerald-400';
            case 'connecting': return 'text-yellow-400';
            case 'error':
            case 'disconnected':
            case 'offline': return 'text-red-400';
            default: return 'text-slate-400';
        }
    };

    const getStatusText = () => {
        switch (serviceStatus) {
            case 'live': return 'CANLI';
            case 'connecting': return 'BAĞLANIYOR';
            case 'error': return 'HATA';
            case 'disconnected': return 'BAĞLANTI KESİLDİ';
            case 'offline': return 'ÇEVRİMDIŞI';
            default: return 'BİLİNMİYOR';
        }
    };

    return (
        <div className={`glass-card rounded-3xl overflow-hidden ${className}`}>
            {/* Header */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-purple-500/10">
                        <span className="material-symbols-outlined text-purple-400">wifi</span>
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white">WiFi DensePose</h3>
                        <p className="text-[10px] text-slate-500 uppercase tracking-widest">Duvar Arkası İzleme</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setIsCameraModalOpen(true)}
                        className="p-2 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 transition-colors"
                        title="MediaPipe Kamera"
                    >
                        <span className="material-symbols-outlined text-blue-400 text-[18px]">videocam</span>
                    </button>
                    <div className="flex items-center gap-1.5">
                        <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
                        <span className={`text-[10px] font-bold uppercase tracking-widest ${getStatusColor()}`}>
                            {getStatusText()}
                        </span>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                        {poses.length} kişi
                    </span>
                </div>
            </div>

            {/* Pose Visualization */}
            <div className="relative h-48 bg-[#0A0F1C]">
                <canvas
                    ref={canvasRef}
                    className="w-full h-full"
                />

                {/* Overlay when offline */}
                {serviceStatus === 'offline' && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50">
                        <span className="material-symbols-outlined text-slate-500 text-4xl mb-2">wifi_off</span>
                        <p className="text-xs text-slate-500">WiFi DensePose servisi çalışmıyor</p>
                        <p className="text-[10px] text-slate-600 mt-1">Port 8001 üzerinden bağlanılamıyor</p>
                    </div>
                )}
            </div>

            {/* Activity Legend */}
            <div className="p-3 border-t border-white/5 flex items-center justify-between">
                <div className="flex gap-4">
                    {Object.entries(ACTIVITY_LABELS).slice(0, 4).map(([key, label]) => (
                        <div key={key} className="flex items-center gap-1.5">
                            <span
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: ACTIVITY_COLORS[key] }}
                            ></span>
                            <span className="text-[10px] text-slate-500">{label}</span>
                        </div>
                    ))}
                </div>

                {/* Fall alerts count */}
                {fallAlerts.length > 0 && (
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-red-500/10 border border-red-500/20">
                        <span className="material-symbols-outlined text-red-400 text-[14px]">warning</span>
                        <span className="text-[10px] text-red-400 font-bold">{fallAlerts.length} Düşme Uyarısı</span>
                    </div>
                )}
            </div>

            {/* MediaPipe Camera Modal */}
            <MediaPipeCameraModal
                isOpen={isCameraModalOpen}
                onClose={() => setIsCameraModalOpen(false)}
            />
        </div>
    );
}
