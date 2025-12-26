# 📊 Dataset Birleştirme Analizi

## Soru: Kaggle Datasetlerini Birleştirmek Mantıklı mı?

### ✅ EVET - Yapmalıyız

#### Artılar:
| Avantaj | Açıklama |
|---------|----------|
| **Daha fazla veri** | 30K → 50K+ kayıt = daha iyi generalization |
| **Feature zenginliği** | Her dataset farklı bilgiler içerir |
| **Robust model** | Çeşitli kaynak = overfitting riski ↓ |
| **Real-world benzeri** | Gerçek hastanelerde de veri çeşitlidir |

#### Riskler ve Çözümleri:
| Risk | Çözüm |
|------|-------|
| Feature uyumsuzluğu | Ortak kolonları belirle, geri kalanı impute/drop |
| Target farklılığı | Unified risk score (0-100 normalize) |
| Distribution shift | StandardScaler + EDA kontrolü |
| Duplicates | `df.drop_duplicates()` |

---

## Birleştirme Stratejisi

### Vertical Merge (Seçilen Yaklaşım)
```
Dataset A (30K rows, 15 cols)
       ↓
Dataset B (8K rows, 12 cols)
       ↓
Dataset C (10K rows, 18 cols)
       ↓
═══════════════════════════════
Merged Dataset (48K rows, ~20 cols)
```

### Ortak Feature'lar
```python
COMMON_FEATURES = [
    'age',           # Tüm datasetlerde var
    'gender',        # Tüm datasetlerde var
    'blood_pressure',# Çoğunda var (systolic/diastolic)
    'bmi',           # Çoğunda var
    'smoking',       # Çoğunda var (binary veya categorical)
    'cholesterol',   # Kalp datasetlerinde var
    'glucose',       # Diyabet datasetlerinde var
]

# Her dataset için mapping yapılacak
COLUMN_MAPPING = {
    'healthcare_risk': {'BP': 'blood_pressure', 'BMI_value': 'bmi'},
    'diabetes': {'DiabetesPedigreeFunction': 'diabetes_risk'},
    'heart_attack': {'trestbps': 'blood_pressure', 'chol': 'cholesterol'}
}
```

---

## Unified Target Variable

Farklı datasetlerdeki target'ları birleştirmek için:

```python
def create_unified_risk_score(row, dataset_source):
    """Her dataset için 0-100 arası risk skoru oluştur."""
    
    if dataset_source == 'healthcare_risk':
        # Risk level already categorical
        mapping = {'Normal': 15, 'Low': 35, 'Medium': 60, 'High': 85}
        return mapping.get(row['risk_level'], 50)
    
    elif dataset_source == 'diabetes':
        # Binary outcome → risk score
        return 75 if row['outcome'] == 1 else 25
    
    elif dataset_source == 'heart_attack':
        # Binary → risk score + factor adjustment
        base = 70 if row['target'] == 1 else 30
        # Adjust by age and cholesterol
        return min(100, base + (row['age'] - 50) * 0.5)
```

---

## Sonuç

**Birleştirme YAPILMALI** çünkü:
1. ✅ Daha güçlü model
2. ✅ Ortak kolonlar mevcut
3. ✅ Risklerin hepsi yönetilebilir
4. ✅ Feature engineering olanakları artar
