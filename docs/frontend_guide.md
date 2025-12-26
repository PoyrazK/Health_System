# 📘 API-Driven Frontend Developer Guide

Bu web uygulaması iki ana backend servisi ile haberleşir. Frontend geliştiricisinin görevi, bu API'lardan dönen **spesifik JSON datalarını** ilgili UI komponentlerine bağlamaktır.

---

## 🏗 Data Models (TypeScript Interfaces)

Frontend projesinde `types.ts` dosyasında bu interface'leri tanımlamalısın.

### 1. Patient (Hasta)
**Source:** Go Backend (`GET /api/patients/:id`)

```typescript
interface Patient {
  id: string; // UUID
  full_name: string;
  age: number;
  gender: 'Male' | 'Female';
  blood_type: string; // e.g., 'A+'
  contact_info: {
    phone: string;
    email: string;
  };
  // ML Modeli için gerekli vitals (Son ölçümler)
  current_vitals: {
    systolic_bp: number;  // Büyük tansiyon (e.g. 120)
    diastolic_bp: number; // Küçük tansiyon (e.g. 80)
    heart_rate: number;   // Nabız (e.g. 72)
    bmi: number;          // Vücut kitle indeksi (24.5)
    glucose_level: number;// Şeker (e.g. 95)
    cholesterol: number;  // (e.g. 180)
    smoking_status: 'smoker' | 'non-smoker' | 'ex-smoker';
  };
  history?: string[]; // Kronik rahatsızlıklar
}
```

### 2. Risk Analysis (ML Output)
**Source:** Python FastAPI (`POST /predict`)

```typescript
interface RiskAnalysis {
  risk_score: number;       // 0-100 arası (Gauge Chart'ta gösterilecek)
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  confidence_score: number; // 0.0 - 1.0 (Modelin kendine güveni)
  
  // Önemli faktörler (UI'da highlight edilecek)
  key_factors: string[];    // e.g. ["High Blood Pressure", "Obesity"]
  
  // Önerilen müdahale süresi
  urgent_action_required: boolean;
  recommended_intervention_time: string; // "Immediate" | "Within 24h" | "Routine"
}
```

### 3. Diagnosis Report (LLM Output)
**Source:** Python FastAPI (`POST /diagnose`)

```typescript
interface DiagnosisReport {
  report_id: string;
  created_at: string; // ISO Date
  
  // LLM Tarafından Üretilen İçerik
  summary: string;           // Kısa özet (Card header için)
  detailed_analysis: string; // Markdown formatında detaylı rapor
  
  // Tavsiyeler (Madde madde gösterilecek)
  recommendations: {
    category: 'Lifestyle' | 'Medication' | 'Diet';
    text: string;
    priority: 'High' | 'Medium' | 'Low';
  }[];
  
  // Doktorun düzenleyebileceği alan
  doctor_notes?: string; 
}
```

---

## 🖥 Ekran & Data Mapping

Aşağıda her ekranın hangi API'yi çağıracağı ve dönen veriyi **nasıl görselleştireceği** detaylandırılmıştır.

### 1. 🩺 Doctor Dashboard (Patient Detail)

Bu ekran **en kritik** ekrandır. 3 aşamalı veri akışı vardır.

#### **Bölge A: Sol Panel (Hasta Profili)**
- **Data:** `Patient` objesi.
- **UI:** Avatar, İsim, Yaş, Kan Grubu kartları.
- **Aksiyon:** Yok (Statik gösterim).

#### **Bölge B: Orta Panel (AI Risk Analizi)**
- **Trigger:** Sayfa yüklendiğinde veya "Analyze Now" butonuna basıldığında.
- **Request:** `POST http://localhost:8000/predict` body: `{ vitals: patient.current_vitals }`
- **Response Handling:**
  - `risk_score` verisi alınır.
  - **Component:** `<RiskGauge score={data.risk_score} />`
    - Score < 30: **Yeşil** (Safe)
    - Score 30-70: **Sarı** (Warning)
    - Score > 70: **Kırmızı** (Danger - Yanıp sönme efekti ekle!)
  - **Component:** `<RiskFactorList factors={data.key_factors} />`
    - Gelen string array'i "tag" veya "badge" olarak listele.

#### **Bölge C: Sağ Panel (LLM Tanı & Chat)**
- **Trigger:** Risk analizi tamamlandıktan sonra otomatik veya manuel.
- **Request:** `POST http://localhost:8000/diagnose` body: `{ patient: patient, risk: riskAnalysis }`
- **Response Handling:**
  - `detailed_analysis` (Markdown) alınır.
  - **Component:** `<MarkdownRenderer content={data.detailed_analysis} />`
  - **Component:** `<RecommendationCards items={data.recommendations} />`
    - Her bir öneri kart şeklinde gösterilir. Kartın kenar rengi `priority` değerine göre değişir (High=Kırmızı, Low=Mavi).

---

### 2. 👤 Patient Portal (Hasta Arayüzü)

Hastalar sadece kendi verilerini okuyabilir (Read-Only).

#### **Bölge A: "Sağlığım" Özeti**
- **Data:** `DiagnosisReport` (En son tarihli rapor).
- **UI:** 
  - Tıbbi terimlerden arındırılmış `summary` alanı gösterilir.
  - Risk skoru SADECE renk olarak gösterilir (Rakam gösterme, hasta panikleyebilir).
    - High -> "Doktorunuzla görüşmelisiniz"
    - Low -> "Durumunuz iyi görünüyor"
- **Component:** `<PatientFriendlySummary report={latestReport} />`

#### **Bölge B: Tavsiyelerim**
- **Data:** `DiagnosisReport.recommendations`.
- **UI:** Basit, checklist benzeri kartlar.
  - Örnek: "Bugün 2Lt su iç" (Checkbox ile işaretlenebilir - sadece lokal state).

---

## 🔌 API Endpoint Detayları (Swagger/OpenAPI Özeti)

### 1. Go Backend (Port 8080)
| Endpoint | Method | Request Body | Response (Success) |
|----------|--------|--------------|-------------------|
| `/auth/login` | POST | `{email, password}` | `{token: "jwt...", user: {...}}` |
| `/patients` | GET | (Auth Header) | `[Patient, Patient, ...]` |
| `/reports` | POST | `DiagnosisReport` | `{id: "123", status: "saved"}` |

### 2. ML & LLM Service (Port 8000)
| Endpoint | Method | Request Body | Response (Success) |
|----------|--------|--------------|-------------------|
| `/predict` | POST | `{age, bmi, bp, ...}` | `RiskAnalysis` (Yukarıdaki model) |
| `/diagnose` | POST | `{risk_data: {...}, history: [...]}` | `DiagnosisReport` (Yukarıdaki model) |

---

## 🎨 UI Component Gereksinimleri

Frontend geliştirici aşağıdaki componentleri bu props yapılarına göre hazırlamalıdır:

1.  **`<RiskGauge score={number} loading={boolean} />`**
    *   D3.js veya Recharts ile yarım daire grafik.
    *   Animasyonlu dolum.

2.  **`<VitalsCard vital={string} value={number} unit={string} status={'normal'|'warning'} />`**
    *   Örnek: Tansiyon için kart. Eğer değer referans aralığı dışındaysa (backend söyleyecek) kart kırmızılaşır.

3.  **`<ChatInterface messages={Message[]} onSend={fn} />`**
    *   Doktorun LLM ile sohbet edip tanıyı rafine etmesi için (Opsiyonel özellik).

## ⚠️ Error Handling
- **401 Unauthorized:** Login sayfasına yönlendir.
- **500 Server Error:** "Servis şu an cevap vermiyor, lütfen daha sonra tekrar deneyin" (Toast mesajı).
- **Model Loading:** ML servisi 1-2 saniye sürebilir. Mutlaka "Analiz yapılıyor..." skeleton loader kullan.
