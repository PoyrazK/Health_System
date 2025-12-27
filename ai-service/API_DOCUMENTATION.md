# 🏥 Healthcare AI Service - API & Model Documentation

Bu doküman, AI servisimizin modellerini ve API endpoint'lerini entegre etmek isteyen geliştiriciler/agentlar için hazırlanmıştır.

---

## 📋 İçindekiler

1. [Genel Bakış](#genel-bakış)
2. [Modeller](#modeller)
3. [API Endpoints](#api-endpoints)
4. [Entegrasyon Örnekleri](#entegrasyon-örnekleri)
5. [Veri Formatları](#veri-formatları)

---

## 🎯 Genel Bakış

### Servis Bilgileri

| Özellik | Değer |
|---------|-------|
| **Base URL** | `http://localhost:8001` |
| **API Version** | v1 |
| **Format** | JSON |
| **Authentication** | Yok (development) |

### Mevcut Modeller

| Model | Amaç | Accuracy | Endpoint |
|-------|------|----------|----------|
| Disease Classifier | Hastalık tahmini (527 sınıf) | %85 | `/api/v1/predict` |
| EKG Signal Analyzer | Sinyal bazlı aritmi tespiti | %92 | `/api/v1/ekg/analyze` |
| EKG Image Analyzer | Görüntüden aritmi tespiti | %92 | `/api/v1/ekg-image/analyze` |

---

## 🤖 Modeller

### 1. Disease Classifier (Hastalık Sınıflandırıcı)

**Neden bu modeli eğittik?**
- Doktorlara semptom bazlı hastalık önerisi sunmak için
- 316 farklı semptomu değerlendirip 527 hastalık arasından en olası olanları sıralamak için

**Model Detayları:**
```
Algoritma:      XGBoost
Veri Seti:      Kaggle Disease-Symptom Dataset
Örnekler:       242,837
Özellikler:     316 semptom (binary: 0/1)
Sınıflar:       527 hastalık
Accuracy:       %85.08 (Top-5: %97.68)
```

**Dosya Konumları:**
```
models/disease/
├── disease_model.pkl          # Ana model
├── label_encoder.pkl          # Etiket encoder
├── feature_columns.pkl        # Özellik isimleri
└── feature_importance.csv     # Özellik önemleri
```

---

### 2. EKG Signal Analyzer (Sinyal Analizi)

**Neden bu modeli eğittik?**
- EKG sinyallerinden aritmi tespiti için
- Gerçek zamanlı kalp ritmi değerlendirmesi için

**Model Detayları:**
```
Algoritma:      XGBoost
Veri Seti:      MIT-BIH Arrhythmia Database
Örnekler:       100,689 (SMOTE: 172,818)
Özellikler:     32 (RR intervals, peaks, morphology)
Sınıflar:       3 (N: Normal, F: Fusion, Q: Belirsiz)
Accuracy:       %92.47 (patient-level split)
```

**Sınıf Açıklamaları:**
| Sınıf | Açıklama | Aciliyet |
|-------|----------|----------|
| N | Normal Sinüs Ritmi | Düşük |
| F | Fusion Atımı | Orta-Yüksek |
| Q | Belirsiz/Gürültü | Değerlendirme Gerekli |

**Dosya Konumları:**
```
models/ekg/
├── ekg_xgboost_fixed.json     # Ana model
├── ekg_scaler_fixed.joblib    # Normalizasyon scaler
├── label_map_fixed.json       # Etiket haritası
└── urgency_levels.json        # Aciliyet seviyeleri
```

---

### 3. EKG Image Analyzer (Görüntü Analizi)

**Neden bu modeli eğittik?**
- EKG kağıdı fotoğraflarından analiz yapabilmek için
- Mobil uygulama entegrasyonu için

**Pipeline:**
```
EKG Görsel (PNG/JPG)
    ↓ OpenCV
Sinyal Çıkarma (grid temizleme, çizgi takibi)
    ↓ 
Feature Extraction (heart rate, RR intervals)
    ↓
XGBoost Model
    ↓
Tahmin + Aciliyet
```

**Desteklenen Formatlar:** PNG, JPG, JPEG

---

## 📡 API Endpoints

### 1. Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T02:00:00"
}
```

---

### 2. Disease Prediction

```http
POST /api/v1/predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "symptoms": ["fever", "cough", "headache"]
}
```

**Response:**
```json
{
  "predictions": [
    {"disease": "Common Cold", "probability": 0.85},
    {"disease": "Flu", "probability": 0.72},
    {"disease": "COVID-19", "probability": 0.45}
  ],
  "top_prediction": "Common Cold",
  "confidence": 0.85
}
```

---

### 3. EKG Signal Analysis

```http
POST /api/v1/ekg/analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "signal": [0.1, 0.3, 0.8, 0.2, ...],
  "sampling_rate": 360
}
```

**Response:**
```json
{
  "prediction": {
    "class": "N",
    "class_name": "Normal",
    "confidence": 0.87,
    "urgency": "Düşük"
  },
  "features": {
    "heart_rate": 72,
    "rr_mean": 833,
    "rr_std": 45
  },
  "recommendation": "Normal ritim. Rutin takip önerilir."
}
```

---

### 4. EKG Image Analysis

```http
POST /api/v1/ekg-image/analyze
Content-Type: multipart/form-data
```

**Request:**
- Form field: `file` (image file)

**cURL Örneği:**
```bash
curl -X POST "http://localhost:8001/api/v1/ekg-image/analyze" \
  -H "accept: application/json" \
  -F "file=@ekg_photo.jpg"
```

**Response:**
```json
{
  "status": "success",
  "signal_length": 256,
  "features": {
    "heart_rate": 78,
    "rr_mean": 769,
    "peak_count": 5
  },
  "prediction": {
    "class": "N",
    "class_name": "Normal",
    "confidence": 0.82,
    "urgency": "Düşük"
  },
  "recommendation": "Normal ritim tespit edildi."
}
```

---

### 5. EKG Image Analysis (Base64)

```http
POST /api/v1/ekg-image/analyze-base64
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

---

### 6. Model Feedback (Öğrenme Döngüsü)

```http
POST /api/v1/feedback
Content-Type: application/json
```

**Request Body:**
```json
{
  "prediction_id": "abc123",
  "predicted": "Common Cold",
  "actual": "Flu",
  "doctor_notes": "Hastada ateş yüksekti"
}
```

---

## 🔧 Entegrasyon Örnekleri

### Python

```python
import requests

# Disease Prediction
response = requests.post(
    "http://localhost:8001/api/v1/predict",
    json={"symptoms": ["fever", "cough"]}
)
print(response.json())

# EKG Image Analysis
with open("ekg.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8001/api/v1/ekg-image/analyze",
        files={"file": f}
    )
print(response.json())
```

### JavaScript/Fetch

```javascript
// Disease Prediction
const response = await fetch('http://localhost:8001/api/v1/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symptoms: ['fever', 'cough'] })
});
const data = await response.json();

// EKG Image Upload
const formData = new FormData();
formData.append('file', imageFile);
const ekgResponse = await fetch('http://localhost:8001/api/v1/ekg-image/analyze', {
  method: 'POST',
  body: formData
});
```

### Go

```go
// Disease Prediction
payload := map[string][]string{"symptoms": {"fever", "cough"}}
jsonData, _ := json.Marshal(payload)
resp, _ := http.Post(
    "http://localhost:8001/api/v1/predict",
    "application/json",
    bytes.NewBuffer(jsonData),
)
```

---

## 📊 Veri Formatları

### Semptom Listesi (Disease Classifier)

316 semptom desteklenir. Örnek:
```
fever, cough, fatigue, headache, nausea, vomiting, 
diarrhea, chest_pain, shortness_of_breath, ...
```

Tam liste: `models/disease/feature_columns.pkl`

### EKG Sinyal Formatı

- **Uzunluk:** Minimum 100, maksimum 5000 sample
- **Değer aralığı:** Normalize edilmiş (-3 ile +3 arası ideal)
- **Sampling rate:** 360 Hz önerilen

### Aciliyet Seviyeleri

| Seviye | Kod | Aksiyon |
|--------|-----|---------|
| Düşük | N | Rutin takip |
| Orta | S | Kardiyoloji konsültasyonu |
| Orta-Yüksek | F | Detaylı inceleme |
| Yüksek | V | ACİL değerlendirme |
| Belirsiz | Q | Manuel review |

---

## 🚀 Hızlı Başlangıç

```bash
# 1. Servisi başlat
cd ai-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 2. Health check
curl http://localhost:8001/api/v1/health

# 3. Test prediction
curl -X POST http://localhost:8001/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever", "cough"]}'
```

---

## 📝 Notlar

1. **Model Güvenilirliği:** Modeller klinik destek amaçlıdır, kesin tanı için değil.
2. **Patient-Level Split:** EKG modeli %92 accuracy ile gerçekçi performans gösterir.
3. **Feedback Loop:** Doktor düzeltmeleri ile model sürekli iyileşir.

---

*Son güncelleme: 2025-12-27*
