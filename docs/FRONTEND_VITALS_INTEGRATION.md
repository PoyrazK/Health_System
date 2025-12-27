# Frontend Integration Guide: Vitals (rPPG) Scanner

This document explains how to integrate the new MediaPipe-based Vitals Scanner into the Next.js frontend.

## API Endpoint
- **URL:** `/api/vitals/analyze`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Field Name:** `video` (The video file to be analyzed)

## Example Implementation (React/Next.js)

### 1. API Client Extension
Add this to your `src/lib/api.ts`:

```typescript
export async function analyzeVitals(videoFile: File) {
  const formData = new FormData();
  formData.append('video', videoFile);

  const response = await fetch(`${API_BASE_URL}/api/vitals/analyze`, {
    method: 'POST',
    body: formData,
    // Note: Do NOT set Content-Type header manually, 
    // the browser will set it with the correct boundary.
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Vitals analysis failed');
  }

  return response.json();
}
```

### 2. Scanner Component UI Recommendation
Use a simple state-driven UI to handle the upload and result:

```tsx
import { useState } from 'react';
import { analyzeVitals } from '@/lib/api';

export const VitalsScanner = () => {
    const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'success' | 'error'>('idle');
    const [result, setResult] = useState<any>(null);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            setStatus('uploading');
            const data = await analyzeVitals(file);
            setResult(data.data);
            setStatus('success');
        } catch (err) {
            setStatus('error');
            console.error(err);
        }
    };

    return (
        <div className="p-6 bg-slate-900 rounded-xl border border-blue-500/20 shadow-2xl">
            <h3 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
                AI Vitals Scanner
            </h3>
            
            <input 
                type="file" 
                accept="video/*" 
                onChange={handleFileChange} 
                disabled={status !== 'idle' && status !== 'success' && status !== 'error'}
                className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-500/10 file:text-blue-400 hover:file:bg-blue-500/20 transition-all cursor-pointer"
            />

            {status === 'uploading' && <p className="mt-4 text-blue-400 animate-pulse">Uploading video...</p>}
            {status === 'success' && result && (
                <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg space-y-3">
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-sm">Heart Rate</span>
                        <span className="text-emerald-400 font-bold text-xl">
                            {result.heart_rate ? `${Math.round(result.heart_rate)} BPM` : 'N/A'}
                        </span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-sm">SpO2 (Est.)</span>
                        <span className="text-blue-400 font-bold text-xl">
                            {result.spo2_estimate.toFixed(1)}%
                        </span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-sm">Risk Level</span>
                        <span className={`font-bold px-2 py-1 rounded text-xs ${
                            result.risk_level === 'RED' ? 'bg-red-500/20 text-red-500' : 
                            result.risk_level === 'YELLOW' ? 'bg-yellow-500/20 text-yellow-500' : 
                            'bg-emerald-500/20 text-emerald-500'
                        }`}>
                            {result.risk_level}
                        </span>
                    </div>
                    <div className="pt-2 border-t border-slate-700/50 flex justify-between text-[10px] text-slate-500">
                        <span>SNR: {result.snr.toFixed(2)}</span>
                        <span>Asymmetry: {result.asymmetry_score.toFixed(3)}</span>
                        <span>Face: {(result.face_detected_ratio * 100).toFixed(0)}%</span>
                    </div>
                </div>
            )}
        </div>
    );
};
```

## Technical Flow
1. **Frontend:** User selects a video of their face.
2. **Backend (Go):** Receives the file, saves it to a shared Docker volume (`/app/uploads`).
3. **ML API (Python):** Reads the file from the shared volume, processes it with MediaPipe + rPPG.
4. **Result:** Returns Heart Rate (BPM) and processing metadata back to the Frontend.
