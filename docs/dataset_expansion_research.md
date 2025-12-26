# 📊 Dataset Expansion Research

**Amaç:** Mevcut "Kalp" ve "Diyabet" odağını genişleterek, sistemin "Hibrit Zeka" yeteneğini artırmak.

## 1. Bulunan Aday Datasetler

Kaggle üzerinde yaptığımız taramada şu 3 dataset öne çıktı:

### A. Stroke Prediction Dataset (İnme Riski) 🧠
Bu dataset bizim için **altın değerinde** çünkü mevcut feature'larımızla %80+ örtüşüyor.
*   **Ortak Kolonlar:** `age`, `gender`, `bmi`, `avg_glucose_level`, `hypertension`, `heart_disease`, `smoking_status`.
*   **Yeni Target:** `stroke` (0/1).
*   **Strateji:** Mevcut havuza direkt eklenebilir. (High Overlap)

### B. Chronic Kidney Disease (Böbrek Yetmezliği) 🫘
Böbrek hastalığı, Diyabet ve Hipertansiyonun en yaygın komplikasyonudur. Bağlantı kurmak için harika.
*   **Ortak Kolonlar:** `age`, `bp` (blood pressure), `bgr` (glucose), `htn` (hypertension), `dm` (diabetes).
*   **Önemli Eksik Parçalar:** `sc` (Creatinine), `bu` (Blood Urea).
*   **Strateji:** Bu verileri "Lab Results" ekranından alabiliriz. Eğer kullanıcı girmezse, Age+BP+Diabetes üzerinden "Risk Tahmini" yapabiliriz.

### C. Indian Liver Patient (Karaciğer) 🫁
Bu dataset mevcut yapıdan biraz uzak.
*   **Ortak Kolonlar:** Sadece `Age` ve `Gender`.
*   **Sorun:** Bilirubin, Albumin, SGPT gibi çok spesifik enzim değerleri istiyor.
*   **Karar:** ML modeline dahil etmek veriyi çok seyreltebilir (sparse matrix). Bunu sadece **LLM (Lab Translator)** kısmında tutmak daha mantıklı.

### D. Mendeley Disease & Symptoms (Genel Tarama) 🦠
**Durum:** ~246K satır, 773 Hastalık, 377 Semptom.
**Potansiyel:** Sadece Kalp/Diyabet değil, "Grip", "Allerji", "Migren" gibi 700+ hastalığı tahmin edebilir.
**Strateji:** Mevcut risk modelinden AYRI, hafif bir NLP sınıflandırıcı (Symptom Checker) olarak çalışacak.
*   *Input:* "Kaşıntı, döküntü, ateş"
*   *Output:* "Su Çiçeği (%85)"

---

## 2. Genişletilmiş Birleştirme Stratejisi (The "Super-Merge")

Verileri şöyle birleştirmeyi öneriyorum:

| Feature | Heart Data | Diabetes Data | Stroke Data | Kidney Data | Symptoms Data (Mendeley) |
|:--------|:----------:|:-------------:|:-----------:|:-----------:|:-----------------------:|
| **Age** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Vitals**| ✅ | ✅ | ✅ | ✅ | ❌ |
| **Symptom**| ❌ | ❌ | ❌ | ❌ | ✅ (Text) |
| **TARGET** | `heart_risk`| `diabetes` | `stroke` | `ckd` | `disease_name` |

### Nasıl Yapacağız?
1.  **Risk Engine (Core):** Kalp + Diyabet + İnme + Böbrek (Sayısal Veri).
2.  **Symptom Checker (Expansion):** Mendeley datasını kullanarak 700+ hastalık için ayrı bir "NLP/Classification Modeli" eğiteceğiz.

## 3. Sonuç ve Öneri

**Kesinlikle Yapalım:**
*   [x] **Stroke & Kidney:** Ana modele eklenecek.
*   [x] **Mendeley Dataset:** "Genel Semptom Kontrolü" modülü olarak eklenecek.

Bu hamle ile sistem hem **Uzman (Kardiyoloji)** hem de **Pratisyen (Genel Dahiliye)** yeteneği kazanır.

