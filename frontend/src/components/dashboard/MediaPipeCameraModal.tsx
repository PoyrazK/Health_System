'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface MediaPipeCameraModalProps {
    isOpen: boolean;
    onClose: () => void;
}

// MediaPipe Pose connections for drawing skeleton
const POSE_CONNECTIONS = [
    [11, 12], // shoulders
    [11, 13], [13, 15], // left arm
    [12, 14], [14, 16], // right arm
    [11, 23], [12, 24], // torso
    [23, 24], // hips
    [23, 25], [25, 27], // left leg
    [24, 26], [26, 28], // right leg
    [0, 1], [1, 2], [2, 3], [3, 7], // left face
    [0, 4], [4, 5], [5, 6], [6, 8], // right face
];

export default function MediaPipeCameraModal({ isOpen, onClose }: MediaPipeCameraModalProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isTracking, setIsTracking] = useState(false);
    const [fps, setFps] = useState(0);
    const [poseData, setPoseData] = useState<any>(null);
    const poseRef = useRef<any>(null);
    const animationRef = useRef<number | null>(null);
    const lastFrameTime = useRef<number>(0);
    const frameCount = useRef<number>(0);

    // Initialize camera
    const initCamera = useCallback(async () => {
        if (!videoRef.current) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });

            videoRef.current.srcObject = stream;
            await videoRef.current.play();
            setIsLoading(false);
            setError(null);
        } catch (err) {
            setError('Kamera erişimi reddedildi veya kamera bulunamadı');
            setIsLoading(false);
        }
    }, []);

    // Load MediaPipe Pose
    const initMediaPipe = useCallback(async () => {
        try {
            // Dynamically import MediaPipe
            const { Pose } = await import('@mediapipe/pose');
            const { Camera } = await import('@mediapipe/camera_utils');
            const { drawConnectors, drawLandmarks } = await import('@mediapipe/drawing_utils');

            const pose = new Pose({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
                }
            });

            pose.setOptions({
                modelComplexity: 1,
                smoothLandmarks: true,
                enableSegmentation: false,
                smoothSegmentation: false,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            pose.onResults((results: any) => {
                if (!canvasRef.current || !videoRef.current) return;

                const ctx = canvasRef.current.getContext('2d');
                if (!ctx) return;

                // Update FPS
                const now = performance.now();
                frameCount.current++;
                if (now - lastFrameTime.current >= 1000) {
                    setFps(frameCount.current);
                    frameCount.current = 0;
                    lastFrameTime.current = now;
                }

                // Draw video frame
                ctx.save();
                ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
                ctx.drawImage(results.image, 0, 0, canvasRef.current.width, canvasRef.current.height);

                // Draw pose landmarks
                if (results.poseLandmarks) {
                    setPoseData(results.poseLandmarks);
                    setIsTracking(true);

                    // Draw connections
                    ctx.strokeStyle = '#3B82F6';
                    ctx.lineWidth = 3;

                    POSE_CONNECTIONS.forEach(([start, end]) => {
                        const startLm = results.poseLandmarks[start];
                        const endLm = results.poseLandmarks[end];

                        if (startLm && endLm && startLm.visibility > 0.5 && endLm.visibility > 0.5) {
                            ctx.beginPath();
                            ctx.moveTo(startLm.x * canvasRef.current!.width, startLm.y * canvasRef.current!.height);
                            ctx.lineTo(endLm.x * canvasRef.current!.width, endLm.y * canvasRef.current!.height);
                            ctx.stroke();
                        }
                    });

                    // Draw landmarks
                    results.poseLandmarks.forEach((landmark: any, i: number) => {
                        if (landmark.visibility > 0.5) {
                            const x = landmark.x * canvasRef.current!.width;
                            const y = landmark.y * canvasRef.current!.height;

                            // Outer glow
                            ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
                            ctx.beginPath();
                            ctx.arc(x, y, 8, 0, Math.PI * 2);
                            ctx.fill();

                            // Inner point
                            ctx.fillStyle = '#3B82F6';
                            ctx.beginPath();
                            ctx.arc(x, y, 4, 0, Math.PI * 2);
                            ctx.fill();
                        }
                    });
                } else {
                    setIsTracking(false);
                    setPoseData(null);
                }

                ctx.restore();
            });

            poseRef.current = pose;

            // Start camera processing
            if (videoRef.current) {
                const camera = new Camera(videoRef.current, {
                    onFrame: async () => {
                        if (poseRef.current && videoRef.current) {
                            await poseRef.current.send({ image: videoRef.current });
                        }
                    },
                    width: 640,
                    height: 480
                });
                camera.start();
            }

        } catch (err) {
            console.error('MediaPipe yüklenemedi:', err);
            setError('MediaPipe yüklenemedi. Fallback moduna geçiliyor...');
            // Fallback: just show video without pose estimation
            startFallbackMode();
        }
    }, []);

    // Fallback mode without MediaPipe
    const startFallbackMode = useCallback(() => {
        const drawFrame = () => {
            if (!canvasRef.current || !videoRef.current) return;

            const ctx = canvasRef.current.getContext('2d');
            if (!ctx) return;

            ctx.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);

            // Draw overlay text
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, canvasRef.current.height - 40, canvasRef.current.width, 40);
            ctx.fillStyle = 'white';
            ctx.font = '14px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('MediaPipe yüklenemedi - Sadece kamera görüntüsü', canvasRef.current.width / 2, canvasRef.current.height - 15);

            animationRef.current = requestAnimationFrame(drawFrame);
        };

        drawFrame();
    }, []);

    // Cleanup
    useEffect(() => {
        if (isOpen) {
            initCamera().then(() => {
                initMediaPipe();
            });
        }

        return () => {
            // Stop camera
            if (videoRef.current?.srcObject) {
                const stream = videoRef.current.srcObject as MediaStream;
                stream.getTracks().forEach(track => track.stop());
            }

            // Cancel animation frame
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }

            // Close pose
            if (poseRef.current) {
                poseRef.current.close();
            }
        };
    }, [isOpen, initCamera, initMediaPipe]);

    // Get activity based on pose
    const getActivity = () => {
        if (!poseData) return 'Algılanmadı';

        const leftShoulder = poseData[11];
        const rightShoulder = poseData[12];
        const leftHip = poseData[23];
        const rightHip = poseData[24];

        if (!leftShoulder || !rightShoulder || !leftHip || !rightHip) return 'Algılanıyor...';

        const shoulderY = (leftShoulder.y + rightShoulder.y) / 2;
        const hipY = (leftHip.y + rightHip.y) / 2;
        const torsoAngle = Math.abs(shoulderY - hipY);

        if (torsoAngle < 0.15) {
            return 'Uzanıyor';
        } else if (shoulderY > 0.6) {
            return 'Oturuyor';
        } else {
            return 'Ayakta';
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/80 backdrop-blur-md"
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="glass-card w-full max-w-4xl rounded-3xl relative z-10 overflow-hidden"
                    >
                        {/* Header */}
                        <div className="p-5 border-b border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-xl bg-blue-500/10">
                                    <span className="material-symbols-outlined text-blue-400">videocam</span>
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold text-white">MediaPipe Poz Tahmini</h2>
                                    <p className="text-xs text-slate-500">Gerçek zamanlı iskelet takibi</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                {/* Status indicators */}
                                <div className="flex items-center gap-2">
                                    <span className={`w-2 h-2 rounded-full ${isTracking ? 'bg-emerald-500 animate-pulse' : 'bg-yellow-500'}`}></span>
                                    <span className="text-xs text-slate-400">
                                        {isTracking ? 'Takip Ediliyor' : 'Aranıyor...'}
                                    </span>
                                </div>
                                <div className="text-xs text-slate-500 font-mono">
                                    {fps} FPS
                                </div>
                                <button
                                    onClick={onClose}
                                    className="p-2 rounded-full hover:bg-white/5 text-slate-400 hover:text-white transition-all"
                                >
                                    <span className="material-symbols-outlined">close</span>
                                </button>
                            </div>
                        </div>

                        {/* Video/Canvas Container */}
                        <div className="relative bg-black aspect-video">
                            <video
                                ref={videoRef}
                                className="hidden"
                                playsInline
                                muted
                            />
                            <canvas
                                ref={canvasRef}
                                width={640}
                                height={480}
                                className="w-full h-full object-contain"
                            />

                            {/* Loading overlay */}
                            {isLoading && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
                                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                                    <p className="text-white text-sm">Kamera başlatılıyor...</p>
                                </div>
                            )}

                            {/* Error overlay */}
                            {error && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
                                    <span className="material-symbols-outlined text-red-400 text-5xl mb-4">videocam_off</span>
                                    <p className="text-white text-sm mb-2">{error}</p>
                                    <button
                                        onClick={() => {
                                            setError(null);
                                            setIsLoading(true);
                                            initCamera();
                                        }}
                                        className="px-4 py-2 rounded-xl bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors"
                                    >
                                        Tekrar Dene
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Stats Footer */}
                        <div className="p-4 border-t border-white/5 grid grid-cols-4 gap-4">
                            <div className="text-center">
                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Durum</p>
                                <p className={`text-sm font-bold ${isTracking ? 'text-emerald-400' : 'text-yellow-400'}`}>
                                    {isTracking ? 'Aktif' : 'Bekleniyor'}
                                </p>
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Aktivite</p>
                                <p className="text-sm font-bold text-blue-400">{getActivity()}</p>
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Eklem Sayısı</p>
                                <p className="text-sm font-bold text-white">{poseData ? '33' : '0'}</p>
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">Model</p>
                                <p className="text-sm font-bold text-purple-400">BlazePose</p>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
