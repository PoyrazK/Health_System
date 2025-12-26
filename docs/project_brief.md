# 🏥 Healthcare AI System - Comprehensive Project Design Document

**Date:** 26 December 2025
**Project Type:** AI/Health Tech Hackathon
**Duration:** 32 Hours

---

## 1. Executive Summary (Vizyon: The Ultimate Clinical Copilot 🩺)

**"Doktorun yerini alan değil, ona süper güçler kazandıran bir asistan."**

Doktorlar (özellikle acil ve dahiliye), günde yüzlerce hasta görüyor ve her biri için %100 dikkat göstermeleri bekleniyor. Bu insani olarak imkansızdır.
Bizim projemiz, doktorun **bilişsel yükünü (cognitive load)** alan, arka planda tüm verileri tarayıp **"Gözden kaçan bir şey var mı?"** diye kontrol eden profesyonel bir araçtır.

**Slogan:** "Your Second Brain in the Clinic."

---

## 2. Problem & Çözüm Analizi

### 🔴 Problem: Bilişsel Yük ve Zaman Baskısı
*   Bir doktorun hasta başına ayırabildiği süre 5-10 dakika.
*   Bu sürede Lab sonuçlarına bakmak, ilaç etkileşimini kontrol etmek, aile geçmişini sorgulamak ve doğru tanı koymak zorundalar.
*   **Sonuç:** "Tükenmişlik Sendromu" (Burnout) ve tıbbi hata riski.

### 🟢 Bizim Çözümümüz: AI Asistanı (Clinical Decision Support)
Sistemimiz doktorun ekranında **sessiz bir asistan** gibi çalışır:
1.  **Hazırlık:** Hasta odaya girmeden "Hocam, bu hastanın tansiyonu riskli ve böbrek değerleri düşüyor, dikkat!" der.
2.  **Güvenlik:** Reçete yazarken "Dikkat, Warfarin kullanıyor!" diye kolunu tutar.
3.  **Hız:** "Epikriz raporunu yaz" komutuyla saniyeler içinde çıktıyı hazırlar.

Proje artık bir "Sağlık Uygulaması" değil, bir **"Klinik İşletim Sistemi" (Clinical OS)** dir.

---

## 3. Detaylı Sistem Mimarisi

Sistem, "Separation of Concerns" (İşlerin Ayrılması) prensibine göre tasarlanmış mikroservis benzeri bir yapıdadır.

### A. Frontend (React + Vite)
Kullanıcının gördüğü yüz. Hızlı, modern ve responsive.
*   **Teknolojiler:** React 18, Tailwind CSS, Recharts (Grafikler), Framer Motion (Animasyonlar).
*   **Roller:** 
    *   **Doctor Dashboard:** Tam yetkili, detaylı veri analizi.
    *   **Patient Portal:** Kısıtlı yetki, basitleştirilmiş ve motive edici arayüz.

### B. Backend Services
İki ayrı servis birbirini tamamlar:

1.  **Core API (Golang):** 
    *   Sistemin omurgasıdır.
    *   **Görevleri:** Kimlik doğrulama (JWT), Hasta verilerini kaydetme (CRUD), İlaç ve Reçete yönetimi.
    *   **Neden Go?** Çok hızlı, type-safe ve güvenilir veri yönetimi için.

2.  **Intelligence API (Python/FastAPI):**
    *   Sistemin beynidir.
    *   **Görevleri:** 
        *   `scikit-learn`/`xgboost` modellerini çalıştırmak.
        *   Google Gemini API (LLM) ile iletişim kurmak.
        *   RAG (Retrieval-Augmented Generation) ile tıbbi veritabanından bağlam çekmek.
    *   **Neden Python?** AI/ML kütüphanelerinin ana dili olduğu için.

### C. Veri Katmanı (PostgreSQL)
Veriler ilişkisel (relational) olarak tutulur:
*   `Users`: Doktor ve Hasta profilleri.
*   `Patients`: Sağlık verileri (Vital signs).
*   `Reports`: AI ve Doktor tarafından oluşturulan tanılar.
*   `Feedbacks`: Doktorun AI raporuna yaptığı düzeltmeler (Sistemi eğitmek için).

---

## 4. Özellik Seti (Feature Breakdown)

### 👨‍⚕️ Doktor Modülü (Profesyonel Arayüz)

#### 1. AI Risk Engine & Dashboard
*   Hasta seçildiğinde 3 temel risk (Kalp, Diyabet, Metabolik) anında hesaplanır.
*   **Görsel:** Renkli "Gauge Chart"lar ile risk seviyesi (Yeşil-Sarı-Kırmızı) gösterilir.
*   **Explainability:** "Neden Riskli?" sorusuna cevap olarak en etkili faktörler (Örn: "Yaş > 50 ve Yüksek Kolesterol") listelenir.

#### 2. LLM Teşhis Asistanı (Diagnosis Co-pilot)
*   Tek tuşla ("Generate Report") detaylı bir ön teşhis raporu oluşturulur.
*   **Prompt Mühendisliği:** Sisteme "Sen uzman bir kardiyologsun" rolü verilir ve hastanın tüm sayısal verileri prompt'a eklenir. Şuna benzer bir çıktı üretir:
    > "Hastanın BMI değeri (32) obezite sınırında ve açlık şekeri (115) pre-diyabetik. Kalp riski orta seviyede olsa da, öncelikli müdahale metabolik sendromu önlemeye yönelik olmalı."

#### 3. İlaç Etkileşim Kontrolü (Drug Interaction Checker) ✨
*   Doktor reçete yazarken, sistem hastanın mevcut ilaçlarını tarar.
*   Eğer doktor *Aspirin* yazıyorsa ve hasta zaten kan sulandırıcı (*Warfarin*) kullanıyorsa, ekranda anında **"⚠️ Kritik Etkileşim Riski: Kanama ihtimali artar!"** uyarısı çıkar.

#### 4. Geri Bildirim Döngüsü (Feedback Loop) ✨
*   LLM bazen hata yapabilir. Doktor raporu düzenleyip kaydettiğinde, sistem bunu **"Doğru Cevap"** olarak işaretler. Bu veri, bir sonraki model eğitiminde kullanılır.

#### 5. Acil Durum Triyajı (Emergency Auto-Triage) 🚨
*   Afet veya yoğunluk anında "Emergency Mode" açılır.
*   Sadece hayati veriler girilir, sistem **1 saniye içinde** triyaj kodunu (🔴 / 🟡 / 🟢) belirler.

#### 6. Genetik Risk Haritası (Family History) 🧬
*   Aile geçmişini (baba, dede) analiz eder ve "Genetik olarak kalp riskiniz %40 fazla" uyarısı verir.

---

### 👤 Hasta Modülü (Empatik Arayüz)

#### 1. Lab Sonuçları Çevirmeni (AI Translator) ✨
*   Karmaşık kan tahlili PDF'lerini veya değerlerini alır.
*   Halka indirger:
    *   *Kreatinin: 1.1* → ✅ "Böbrekleriniz gayet iyi çalışıyor."
    *   *WBC: 12.000* → ⚠️ "Vücutta hafif bir enfeksiyon olabilir, endişelenmeyin ama takip edelim."

#### 2. Günlük Check-in & Trend Analizi ✨
*   Her gün "Bugün nasılsın?" bildirimi gider.
*   Hasta emoji ile cevap verir (😊 😐 😣).
*   Doktor, bir sonraki randevuda "Son 3 gündür hastanın modu düşüşte" diye uyarılır.

---

## 5. Geliştirme Yol Haritası (Timeline)

Proje 5 ana faza bölünmüştür:

1.  **Foundation (İlk 4 Saat):** Veritabanı şeması, Proje iskeleti, Git kurulumu.
2.  **Data & ML (4-12. Saat):** Datasetlerin indirilmesi, temizlenmesi (EDA) ve Modelin eğitilmesi.
3.  **Backend API (12-20. Saat):** Go API (CRUD) ve Python API (AI) endpointlerinin yazılması.
4.  **Frontend (20-28. Saat):** Ekranların tasarlanması ve API entegrasyonu.
5.  **Integration & Polish (Son 4 Saat):** Parçaların birleştirilmesi, Dockerize edilmesi ve sunum hazırlığı.

---
**Takım için Not:** Bu proje sadece kod yazmak değil, sağlıkta geleceğin nasıl olacağını göstermekle ilgili. Her satır kodda "Bu bir hayat kurtarabilir mi?" veya "Bu bir hastayı rahatlatabilir mi?" diye düşünelim. 🚀
