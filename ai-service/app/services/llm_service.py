"""
LLM Service - Google Gemini Integration
Provides diagnosis assistance and patient-friendly health explanations
"""

from typing import Dict, Any, List, Optional
import os
import json

# Try to import Google Generative AI, but make it optional
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False
    print("⚠️ google-generativeai not installed. LLM features will use fallback mode.")

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class LLMService:
    def __init__(self):
        self.model = None
        if GENAI_AVAILABLE and GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_diagnosis_report(
        self,
        patient_data: Dict[str, Any],
        symptoms: List[str],
        ml_predictions: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate a detailed diagnosis report for doctors
        Combines ML predictions with LLM reasoning
        """
        if not self.model:
            return self._fallback_report(ml_predictions, risk_assessment)
        
        prompt = f"""
Sen deneyimli bir dahiliye uzmanısın ve doktorlara ön değerlendirme yapan bir AI asistanısın.
Aşağıdaki hasta verilerini analiz et ve doktora yardımcı bir rapor hazırla.

## Hasta Bilgileri
- Yaş: {patient_data.get('age', 'Bilinmiyor')}
- Cinsiyet: {patient_data.get('gender', 'Bilinmiyor')}
- BMI: {patient_data.get('bmi', 'Bilinmiyor')}

## Semptomlar
{', '.join(symptoms)}

## ML Model Tahminleri (Makine Öğrenimi Sonuçları)
{json.dumps(ml_predictions, ensure_ascii=False, indent=2)}

## Risk Değerlendirmesi
- Risk Skoru: {risk_assessment.get('overall_risk_score', 'N/A')}%
- Risk Seviyesi: {risk_assessment.get('risk_level', 'N/A')}
- Risk Faktörleri: {', '.join(risk_assessment.get('risk_factors', []))}

---

Lütfen aşağıdaki formatta bir rapor oluştur:

### 1. ÖN DEĞERLENDİRME
(ML sonuçlarına dayanarak en olası tanıları ve nedenlerini açıkla)

### 2. ÖNCELİKLİ MÜDAHALE ÖNERİSİ
(Acil mi, rutin takip mi, ileri tetkik mi gerekli?)

### 3. ÖNERİLEN TETKİKLER
(Tanıyı netleştirmek için hangi testler yapılmalı?)

### 4. AYIRICI TANI
(Dikkat edilmesi gereken diğer olası durumlar)

### 5. NOTLAR
(Ek dikkat edilecek hususlar)

NOT: Bu bir AI ön değerlendirmesidir, nihai tanı doktor tarafından konulmalıdır.
"""
        
        try:
            response = self.model.generate_content(prompt)
            report_text = response.text
            
            return {
                "status": "success",
                "report": report_text,
                "model_used": "gemini-1.5-flash",
                "disclaimer": "Bu rapor AI tarafından oluşturulmuştur. Nihai tanı ve tedavi kararı doktor tarafından verilmelidir."
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "report": self._fallback_report(ml_predictions, risk_assessment)["report"]
            }
    
    async def generate_patient_explanation(
        self,
        lab_results: Dict[str, Any],
        patient_language_level: str = "simple"
    ) -> Dict[str, str]:
        """
        Translate complex medical lab results into patient-friendly language
        """
        if not self.model:
            return self._fallback_patient_explanation(lab_results)
        
        prompt = f"""
Sen hastaların lab sonuçlarını anlayabilecekleri şekilde açıklayan bir sağlık danışmanısın.
Aşağıdaki lab sonuçlarını hasta için anlaşılır bir dilde açıkla.
Panik yaratmadan, sakin ve bilgilendirici bir ton kullan.

## Lab Sonuçları
{json.dumps(lab_results, ensure_ascii=False, indent=2)}

---

Lütfen her değer için şu formatta açıklama yap:
- 🟢 Normal değerler için: "Normal aralıkta" + kısa açıklama
- 🟡 Hafif anormal değerler için: "Hafif yüksek/düşük" + ne anlama geldiği + panik yapmayın mesajı
- 🔴 Önemli anormal değerler için: "Dikkat gerektiriyor" + doktorla görüşün önerisi

Sonunda genel bir özet ve sağlık tavsiyesi ekle.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "status": "success",
                "explanation": response.text,
                "model_used": "gemini-1.5-flash"
            }
        except Exception as e:
            return self._fallback_patient_explanation(lab_results)
    
    async def check_drug_interactions(
        self,
        current_medications: List[str],
        new_medication: str
    ) -> Dict[str, Any]:
        """
        Check for potential drug interactions
        """
        if not self.model:
            return {
                "status": "fallback",
                "interactions": [],
                "warning": "LLM servisi aktif değil, manuel kontrol gerekli"
            }
        
        prompt = f"""
Sen bir klinik eczacısın. Aşağıdaki ilaç etkileşimlerini kontrol et.

## Mevcut İlaçlar
{', '.join(current_medications)}

## Eklenmek İstenen İlaç
{new_medication}

---

Lütfen şu formatta yanıt ver:
1. Etkileşim var mı? (EVET/HAYIR/BELKİ)
2. Etkileşim varsa risk seviyesi (KRİTİK/ORTA/DÜŞÜK)
3. Hangi ilaçlar arasında etkileşim var?
4. Ne tür bir etkileşim? (Örn: Kanama riski artışı, Etkinlik azalması, vb.)
5. Öneri (İlaç değişikliği, doz ayarı, monitörizasyon vb.)
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "status": "success",
                "analysis": response.text,
                "model_used": "gemini-1.5-flash"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _fallback_report(
        self,
        ml_predictions: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, str]:
        """Fallback when LLM is not available"""
        top_disease = ml_predictions[0] if ml_predictions else {"disease": "Bilinmiyor", "probability": 0}
        
        report = f"""
### ÖN DEĞERLENDİRME (ML Bazlı)

**En Olası Tanı:** {top_disease.get('disease', 'Bilinmiyor')} 
**Güven Oranı:** {top_disease.get('probability', 0)}%

**Risk Seviyesi:** {risk_assessment.get('risk_level', 'N/A')}
**Risk Skoru:** {risk_assessment.get('overall_risk_score', 'N/A')}%

### RİSK FAKTÖRLERİ
{chr(10).join(['- ' + rf for rf in risk_assessment.get('risk_factors', ['Tespit edilmedi'])])}

### ÖNERİLER
{chr(10).join(['- ' + r for r in risk_assessment.get('recommendations', ['Doktor değerlendirmesi önerilir'])])}

---
⚠️ Bu basitleştirilmiş bir rapordur. LLM servisi aktif değil.
"""
        return {
            "status": "fallback",
            "report": report,
            "disclaimer": "LLM servisi aktif olmadığı için basitleştirilmiş rapor oluşturuldu."
        }
    
    def _fallback_patient_explanation(self, lab_results: Dict[str, Any]) -> Dict[str, str]:
        """Fallback patient explanation"""
        explanation = "Lab sonuçlarınız alınmıştır.\n\n"
        for key, value in lab_results.items():
            explanation += f"• {key}: {value}\n"
        explanation += "\nDetaylı açıklama için doktorunuza danışın."
        
        return {
            "status": "fallback",
            "explanation": explanation
        }


# Singleton instance
llm_service = LLMService()
