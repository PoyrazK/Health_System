import { useState, useEffect } from 'react';

interface TelemetryStatus {
    status: string;
    dependencies: {
        db: string;
        redis: string;
        nats: string;
    };
    latency: number;
}

export const useTelemetry = (intervalMs: number = 10000) => {
    const [status, setStatus] = useState<TelemetryStatus>({
        status: 'loading',
        dependencies: {
            db: 'loading',
            redis: 'loading',
            nats: 'loading'
        },
        latency: 0
    });

    useEffect(() => {
        const checkHealth = async () => {
            const start = performance.now();
            try {
                const res = await fetch("http://localhost:3000/health/ready");
                const data = await res.json();
                const end = performance.now();

                setStatus({
                    status: data.status,
                    dependencies: data.dependencies,
                    latency: Math.round(end - start)
                });
            } catch (err) {
                setStatus(prev => ({
                    ...prev,
                    status: 'unreachable',
                    dependencies: {
                        db: 'error',
                        redis: 'error',
                        nats: 'error'
                    }
                }));
            }
        };

        checkHealth();
        const interval = setInterval(checkHealth, intervalMs);
        return () => clearInterval(interval);
    }, [intervalMs]);

    return status;
};
