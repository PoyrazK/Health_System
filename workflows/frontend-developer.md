---
description: Frontend Developer Agent - Build React dashboards and UIs for ML applications
---

# Frontend Developer Agent 🎨

Your role is to create beautiful React interfaces for ML model interaction.

## Core Responsibilities
1. React component development
2. API integration
3. Data visualization
4. Responsive design

## Workflow

### Step 1: Create React App
// turbo
```bash
npx -y create-vite@latest frontend -- --template react && cd frontend && npm install
```

### Step 2: Install Dependencies
// turbo
```bash
cd frontend && npm install axios recharts @heroicons/react
```

### Step 3: Create Main Components

Create `frontend/src/components/PredictionForm.jsx`:

```jsx
import { useState } from 'react';
import axios from 'axios';

export default function PredictionForm({ onPredict }) {
  const [features, setFeatures] = useState({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/predict', { features });
      onPredict(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="prediction-form">
      <h2>Enter Features</h2>
      {/* Dynamic feature inputs */}
      <button type="submit" disabled={loading}>
        {loading ? 'Predicting...' : 'Predict'}
      </button>
    </form>
  );
}
```

Create `frontend/src/components/ResultDisplay.jsx`:

```jsx
export default function ResultDisplay({ result }) {
  if (!result) return null;
  
  return (
    <div className="result-display">
      <h2>Prediction Result</h2>
      <div className="result-value">
        {result.prediction.toFixed(4)}
      </div>
    </div>
  );
}
```

### Step 4: Create App Layout

Replace `frontend/src/App.jsx`:

```jsx
import { useState } from 'react';
import PredictionForm from './components/PredictionForm';
import ResultDisplay from './components/ResultDisplay';
import './App.css';

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="app">
      <header>
        <h1>🤖 ML Prediction Dashboard</h1>
      </header>
      <main>
        <PredictionForm onPredict={setResult} />
        <ResultDisplay result={result} />
      </main>
    </div>
  );
}

export default App;
```

### Step 5: Add Styling

Replace `frontend/src/App.css`:

```css
:root {
  --primary: #6366f1;
  --bg: #0f172a;
  --card: #1e293b;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', sans-serif;
  background: var(--bg);
  color: white;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

header h1 { font-size: 2rem; margin-bottom: 2rem; }

.prediction-form, .result-display {
  background: var(--card);
  padding: 2rem;
  border-radius: 1rem;
  margin-bottom: 1rem;
}

button {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
}

button:hover { opacity: 0.9; }

.result-value {
  font-size: 3rem;
  font-weight: bold;
  color: var(--primary);
}
```

### Step 6: Run Development Server
// turbo
```bash
cd frontend && npm run dev
```

## Output Artifacts
- `frontend/` - Complete React application
- `frontend/src/components/` - React components
- `frontend/src/App.css` - Styling
