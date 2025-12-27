'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import MetallicPaint to avoid SSR issues
const MetallicPaint = dynamic(() => import('./MetallicPaint'), { ssr: false });

interface MetallicTextProps {
    text: string;
    fontSize?: number;
    fontFamily?: string;
    className?: string;
}

const defaultParams = {
    patternScale: 2,
    refraction: 0.015,
    edge: 1,
    patternBlur: 0.005,
    liquid: 0.07,
    speed: 0.3
};

export default function MetallicText({
    text,
    fontSize = 200,
    fontFamily = 'system-ui, -apple-system, sans-serif',
    className = ''
}: MetallicTextProps) {
    const [imageData, setImageData] = useState<ImageData | null>(null);

    useEffect(() => {
        // Create canvas to render text
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set up font
        ctx.font = `bold ${fontSize}px ${fontFamily}`;

        // Measure text
        const metrics = ctx.measureText(text);
        const textWidth = metrics.width;
        const textHeight = fontSize * 1.2;

        // Set canvas size with padding
        const padding = 40;
        canvas.width = Math.max(500, textWidth + padding * 2);
        canvas.height = Math.max(500, textHeight + padding * 2);

        // Fill white background
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw text in black
        ctx.font = `bold ${fontSize}px ${fontFamily}`;
        ctx.fillStyle = 'black';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, canvas.width / 2, canvas.height / 2);

        // Get image data
        const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
        setImageData(data);
    }, [text, fontSize, fontFamily]);

    if (!imageData) {
        return <div className={className}>Loading...</div>;
    }

    return (
        <div className={className}>
            <MetallicPaint imageData={imageData} params={defaultParams} />
        </div>
    );
}
