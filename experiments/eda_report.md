# Dataset Loading & Overview
### Dataset: HEART
# - Shape: (1025, 14)
# - Columns: age, sex, cp, trestbps, chol...
# - Missing Values: 0

```
   age  sex  cp  trestbps  chol  fbs  restecg  thalach  exang  oldpeak  slope  ca  thal  target
0   52    1   0       125   212    0        1      168      0      1.0      2   2     3       0
1   53    1   0       140   203    1        0      155      1      3.1      0   0     3       0
```
### Dataset: DIABETES
# - Shape: (253680, 22)
# - Columns: Diabetes_binary, HighBP, HighChol, CholCheck, BMI...
# - Missing Values: 0

```
   Diabetes_binary  HighBP  HighChol  CholCheck   BMI  Smoker  Stroke  HeartDiseaseorAttack  PhysActivity  Fruits  Veggies  HvyAlcoholConsump  AnyHealthcare  NoDocbcCost  GenHlth  MentHlth  PhysHlth  DiffWalk  Sex  Age  Education  Income
0              0.0     1.0       1.0        1.0  40.0     1.0     0.0                   0.0           0.0     0.0      1.0                0.0            1.0          0.0      5.0      18.0      15.0       1.0  0.0  9.0        4.0     3.0
1              0.0     0.0       0.0        0.0  25.0     1.0     0.0                   0.0           1.0     0.0      0.0                0.0            0.0          1.0      3.0       0.0       0.0       0.0  0.0  7.0        6.0     1.0
```
### Dataset: STROKE
# - Shape: (5110, 12)
# - Columns: id, gender, age, hypertension, heart_disease...
# - Missing Values: 201

```
      id  gender   age  hypertension  heart_disease ever_married      work_type Residence_type  avg_glucose_level   bmi   smoking_status  stroke
0   9046    Male  67.0             0              1          Yes        Private          Urban             228.69  36.6  formerly smoked       1
1  51676  Female  61.0             0              0          Yes  Self-employed          Rural             202.21   NaN     never smoked       1
```
### Dataset: KIDNEY
# - Shape: (400, 26)
# - Columns: id, age, bp, sg, al...
# - Missing Values: 1009

```
   id   age    bp    sg   al   su  rbc      pc         pcc          ba    bgr    bu   sc  sod  pot  hemo pcv    wc   rc  htn   dm cad appet  pe ane classification
0   0  48.0  80.0  1.02  1.0  0.0  NaN  normal  notpresent  notpresent  121.0  36.0  1.2  NaN  NaN  15.4  44  7800  5.2  yes  yes  no  good  no  no            ckd
1   1   7.0  50.0  1.02  4.0  0.0  NaN  normal  notpresent  notpresent    NaN  18.0  0.8  NaN  NaN  11.3  38  6000  NaN   no   no  no  good  no  no            ckd
```
#### Cleaned Kidney Dataset (Fixed numeric parsing and tabular junk)
## Feature Overlap Analysis
| Concept | Heart | Diabetes | Stroke | Kidney |
|---|---|---|---|---|
| **Age** | `age` | `Age` | `age` | `age` | 
| **Sex/Gender** | `sex` | `Sex` | `gender` | ❌ | 
| **BMI** | ❌ | `BMI` | `bmi` | ❌ | 
| **Blood Pressure** | ❌ | `HighBP` | `hypertension` | `bp` | 
| **Glucose** | `fbs` | `Diabetes_binary` | `avg_glucose_level` | `bgr` | 
| **Cholesterol** | `chol` | `HighChol` | ❌ | ❌ | 
