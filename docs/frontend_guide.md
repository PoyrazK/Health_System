# Frontend Integration Guide: Real-Time WebSockets ⚡

This guide explains how to connect your Next.js frontend to the new real-time diagnostic stream.

## Connection Details
- **Endpoint**: `ws://localhost:3000/ws/diagnostics`
- **Protocol**: Standard WebSocket (JSON)

## 1. Establishing a Connection
Use a standard `WebSocket` client in your React component.

```javascript
const ws = new WebSocket("ws://localhost:3000/ws/diagnostics");

ws.onopen = () => {
    console.log("Connected to clinical diagnostic stream");
};
```

## 2. Subscribing to a Patient
Once the connection is open, you must tell the server which patient you are interested in. Send a "subscribe" message with the `patient_id`.

```javascript
ws.send(JSON.stringify({
    type: "subscribe",
    patient_id: 42 // Replace with the actual patient ID
}));
```

## 3. Handling Updates
The server will send a message of type `diagnosis_update` as soon as the AI finishes its analysis.

```javascript
ws.onmessage = (event) => {
    const data = json.parse(event.data);
    
    if (data.type === "diagnosis_update") {
        console.log("Real-time Diagnosis Received:", data.diagnosis);
        // data contains: 
        // - patient_id
        // - diagnosis (Markdown string)
        // - status ("ready" or "error")
        
        // UPDATE YOUR UI STATE HERE
        setDiagnosis(data.diagnosis);
        setStatus(data.status);
    }
};
```

## Why use this instead of polling?
1. **Zero Latency**: The diagnosis appears the millisecond the LLM finishes.
2. **Efficiency**: No need for `setInterval` loops that waste battery and server resources.
3. **UX**: Allows for a "Ready!" notification or toast to pop up even if the doctor has switched tabs.
