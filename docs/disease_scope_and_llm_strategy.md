# 🩺 Disease Scope & LLM Strategy

Bu döküman, sistemimizin hangi sağlık sorunlarına odaklanacağını ve LLM'in (Gemini) bu süreci nasıl "akıllı" hale getireceğini detaylandırır.

---

## 1. Hastalık Kapsamı (Disease Scope)

Elimizdeki veriler (`Yaş`, `Cinsiyet`, `Tansiyon`, `BMI`, `Şeker`, `Kolesterol`, `Sigara`) ile hangi hastalıkları yakalayabiliriz?

### A. Doğrudan ML ile Tespit Edilecekler (Core Scope)
Bu hastalıklar için elimizde *ground truth* (etiketli) veri var. ML modelimiz kesin bir risk yüzdesi (%85 Risk) verecek.

1.  **Kalp Krizi (Heart Attack Risk):**
    *   *Girdiler:* Tansiyon, Kolesterol, Yaş, Sigara.
    *   *Çıktı:* 10 Yıllık Kalp Krizi Riski (High/Medium/Low).
2.  **Tip 2 Diyabet (Diabetes Risk):**
    *   *Girdiler:* Glukoz, BMI, Yaş.
    *   *Çıktı:* Diyabet olasılığı.
3.  **Hipertansiyon (Hypertension):**
    *   *Girdiler:* Sistolik/Diastolik Tansiyon.
    *   *Çıktı:* Evre 1/2 Hipertansiyon sınıflandırması.

### B. LLM ile Çıkarım Yapılacaklar (Expanded Scope)
Bu hastalıklar için özel ML modelimiz yok, ancak LLM elimizdeki parametreleri ve tıbbi bilgiyi birleştirerek **"Şüphe"** uyarısı verecek.

1.  **Metabolik Sendrom:**
    *   *Mantık:* Eğer (Bel Çevresi geniş) + (Tansiyon yüksek) + (Şeker sınırda) ise → LLM: "Metabolik sendrom riski yüksek, endokrinolojiye yönlendir."
2.  **İnme (Stroke) Riski:**
    *   *Mantık:* ML Kalp riski yüksek dedi + Tansiyon çok yüksek → LLM: "Bu tablo aynı zamanda yüksek İNME riski taşıyor."
3.  **KOAH & Akciğer Sorunları:**
    *   *Mantık:* Uzun süre sigara içimi + Yaş > 50 → LLM: "Solunum fonksiyon testi önerilir."
4.  **Böbrek Yetmezliği Riski:**
    *   *Mantık:* Kontrolsüz Hipertansiyon + Diyabet → LLM: "Böbrek fonksiyonları (Kreatinin) kontrol edilmeli."

---

## 2. LLM Geliştirme Stratejisi (Gemini API)

Basit bir metin üretimi yerine, LLM'i gerçek bir "Doktor Asistanı" gibi kullanacağız.

### Strateji A: "Context-Aware" Prompting
LLM'e sadece hasta verisini değil, **ML modelinin bulgularını** da vereceğiz.

**Prompt Taslağı:**
```text
Role: You are an expert AI medical assistant assisting a doctor.
Patient Data: 
- Age: 55, Male, Smoker
- BP: 150/95 (High), Glucose: 110 (Pre-diabetic)

ML Model Analysis:
- Heart Attack Risk: 78% (HIGH)
- Diabetes Risk: 45% (MEDIUM)

Task:
1. Explain WHY the heart risk is high (link BP and Smoking).
2. Identify warning signs for OTHER related conditions (e.g. Stroke, Kidney).
3. Suggest a prioritized treatment plan (Lifestyle first, then medication check).
4. Output JSON for frontend cards + Markdown for detailed report.
```

### Strateji B: Tıbbi Kılavuz Entegrasyonu (RAG-lite)
Prompt'un içine güncel tıbbi kılavuz özetlerini (System Prompt olarak) gömeceğiz. Böylece LLM "kafadan atmaz", standarda uyar.

*   *Hipertansiyon için:* JNC 8 veya ESC/ESH kılavuz kuralları.
*   *Diyabet için:* ADA (American Diabetes Association) kriterleri.

### Strateji C: Semptom Analizi (Chatbot)
Doktor veya hasta panele manuel bir şikayet girdiğinde, LLM bunu vitallerle birleştirecek.

*   *Senaryo:* Hasta "Başım dönüyor" yazdı.
*   *Sistem:* Vitallere baktı → Tansiyon 90/60 (Düşük).
*   *LLM Çıktısı:* "Hipotansiyon (düşük tansiyon) kaynaklı baş dönmesi olabilir. Tuzlu ayran içilmesi ve uzanılması önerilir."

---

## 3. Somut Çıktılar (Ne Göreceğiz?)

### Doktor Ekranında:
1.  **Risk Göstergesi:** "Kalp: %78 (Kırmızı)"
2.  **LLM "Second Opinion":** 
    > "Hastanın yüksek tansiyonu ve sigara geçmişi kalp riskini domine ediyor. Ancak diyabet riski de sınırda. Statin tedavisi ve sigara bırakma programı öncelikli olmalı. Ayrıca böbrek fonksiyon testleri isteyebilirsiniz."

### Hasta Ekranında:
1.  **Basitleştirilmiş Durum:** "Kalp sağlığınız dikkat istiyor."
2.  **Aksiyon Kartları:**
    *   [ ] "Günde 30 dk tempolu yürüyüş yap"
    *   [ ] "Tuzu azalt (Günde <5g)"
    *   [ ] "Sigarayı bırakmak için destek hattını ara"

---

## Karar Noktası 🚦

Bu kapsam (ML ile 3 temel hastalık + LLM ile türetilmiş 4+ hastalık) hackathon için hem etkileyici hem de yapılabilir duruyor. 

Onaylıyorsanız kodlamaya geçelim mi?
