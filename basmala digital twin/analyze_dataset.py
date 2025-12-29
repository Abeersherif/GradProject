"""
Custom Dataset Analysis for the Diabetes Dataset
"""
import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('diabetes_dataset.csv')

print("="*70)
print("DIABETES DATASET ANALYSIS FOR DIGITAL TWIN")
print("="*70)

# Basic Info
print(f"\n📊 DATASET OVERVIEW")
print(f"Total Records: {len(df):,}")
print(f"Total Columns: {len(df.columns)}")
print(f"\n📋 AVAILABLE FIELDS:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

# Check for missing data
print(f"\n🔍 DATA QUALITY CHECK")
missing_summary = df.isnull().sum()
if missing_summary.sum() == 0:
    print("  ✓ No missing values detected!")
else:
    print("  Missing values found:")
    for col in missing_summary[missing_summary > 0].index:
        pct = (missing_summary[col] / len(df)) * 100
        print(f"    - {col}: {missing_summary[col]} ({pct:.2f}%)")

# Key Statistics for Digital Twin
print(f"\n📈 KEY DIABETES METRICS")

# Fasting Blood Glucose
if 'Fasting_Blood_Glucose' in df.columns:
    fbg = df['Fasting_Blood_Glucose']
    print(f"\n  Fasting Blood Glucose (mg/dL):")
    print(f"    Mean: {fbg.mean():.1f}")
    print(f"    Range: {fbg.min():.1f} - {fbg.max():.1f}")
    print(f"    Diabetic (≥126): {(fbg >= 126).sum()} ({(fbg >= 126).sum()/len(df)*100:.1f}%)")
    print(f"    Pre-diabetic (100-125): {((fbg >= 100) & (fbg < 126)).sum()} ({((fbg >= 100) & (fbg < 126)).sum()/len(df)*100:.1f}%)")
    print(f"    Normal (<100): {(fbg < 100).sum()} ({(fbg < 100).sum()/len(df)*100:.1f}%)")

# HbA1c
if 'HbA1c' in df.columns:
    hba1c = df['HbA1c']
    print(f"\n  HbA1c (%):")
    print(f"    Mean: {hba1c.mean():.1f}")
    print(f"    Range: {hba1c.min():.1f} - {hba1c.max():.1f}")
    print(f"    Diabetic (≥6.5%): {(hba1c >= 6.5).sum()} ({(hba1c >= 6.5).sum()/len(df)*100:.1f}%)")
    print(f"    Pre-diabetic (5.7-6.4%): {((hba1c >= 5.7) & (hba1c < 6.5)).sum()} ({((hba1c >= 5.7) & (hba1c < 6.5)).sum()/len(df)*100:.1f}%)")

# BMI
if 'BMI' in df.columns:
    bmi = df['BMI']
    print(f"\n  BMI:")
    print(f"    Mean: {bmi.mean():.1f}")
    print(f"    Obese (≥30): {(bmi >= 30).sum()} ({(bmi >= 30).sum()/len(df)*100:.1f}%)")
    print(f"    Overweight (25-29.9): {((bmi >= 25) & (bmi < 30)).sum()} ({((bmi >= 25) & (bmi < 30)).sum()/len(df)*100:.1f}%)")

# Demographics
print(f"\n👥 DEMOGRAPHICS")
if 'Age' in df.columns:
    print(f"  Age Range: {df['Age'].min()}-{df['Age'].max()} years (Mean: {df['Age'].mean():.1f})")
if 'Sex' in df.columns:
    print(f"  Gender Distribution:")
    for gender, count in df['Sex'].value_counts().items():
        print(f"    {gender}: {count} ({count/len(df)*100:.1f}%)")

# Suitability Assessment
print(f"\n" + "="*70)
print("SUITABILITY FOR DIGITAL TWIN")
print("="*70)

score = 0
max_score = 100

# Criterion 1: Dataset Size (30 points)
if len(df) >= 5000:
    score += 30
    print(f"✓ Dataset Size: EXCELLENT ({len(df):,} records) [+30 points]")
elif len(df) >= 1000:
    score += 20
    print(f"○ Dataset Size: GOOD ({len(df):,} records) [+20 points]")
else:
    score += 10
    print(f"⚠ Dataset Size: FAIR ({len(df):,} records) [+10 points]")

# Criterion 2: Key Diabetes Fields (40 points)
diabetes_fields = ['Fasting_Blood_Glucose', 'HbA1c', 'BMI', 'Age']
present_fields = [f for f in diabetes_fields if f in df.columns]
field_score = (len(present_fields) / len(diabetes_fields)) * 40
score += field_score
print(f"✓ Key Diabetes Fields: {len(present_fields)}/{len(diabetes_fields)} present [+{field_score:.0f} points]")

# Criterion 3: Complication Indicators (20 points)
complication_fields = ['Blood_Pressure_Systolic', 'Cholesterol_Total', 'GGT']
present_comp = [f for f in complication_fields if f in df.columns]
comp_score = (len(present_comp) / len(complication_fields)) * 20
score += comp_score
print(f"✓ Complication Indicators: {len(present_comp)}/{len(complication_fields)} present [+{comp_score:.0f} points]")

# Criterion 4: Data Quality (10 points)
if df.isnull().sum().sum() == 0:
    score += 10
    print(f"✓ Data Quality: No missing values [+10 points]")
else:
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if missing_pct < 5:
        score += 7
        print(f"○ Data Quality: Minimal missing data ({missing_pct:.1f}%) [+7 points]")
    else:
        score += 3
        print(f"⚠ Data Quality: Some missing data ({missing_pct:.1f}%) [+3 points]")

print(f"\n{'='*70}")
print(f"FINAL QUALITY SCORE: {score:.0f}/100")
print(f"{'='*70}")

if score >= 80:
    verdict = "EXCELLENT ✓"
    recommendation = "This dataset is ideal for Digital Twin development!"
    color = "🟢"
elif score >= 60:
    verdict = "GOOD ○"
    recommendation = "This dataset is suitable for Digital Twin development."
    color = "🟡"
else:
    verdict = "FAIR ⚠"
    recommendation = "This dataset can work but may need supplementation."
    color = "🟠"

print(f"\n{color} VERDICT: {verdict}")
print(f"📝 RECOMMENDATION: {recommendation}")

# What can be built
print(f"\n{'='*70}")
print("WHAT YOU CAN BUILD WITH THIS DATASET")
print(f"{'='*70}")

print(f"\n✓ POSSIBLE FEATURES:")
print(f"  1. Diabetes Risk Prediction Model")
print(f"     - Input: Age, BMI, Family History, Lifestyle")
print(f"     - Output: Diabetes Risk Score")
print(f"\n  2. HbA1c Prediction")
print(f"     - Input: Fasting Glucose, BMI, Age")
print(f"     - Output: Estimated HbA1c")
print(f"\n  3. Complication Risk Assessment")
print(f"     - Input: HbA1c, BP, Cholesterol, GGT")
print(f"     - Output: Risk levels for:")
print(f"       • Cardiovascular disease")
print(f"       • Kidney disease (based on GGT)")
print(f"       • Hypertension")
print(f"\n  4. Patient Clustering")
print(f"     - Group patients by risk profiles")
print(f"     - Personalized treatment recommendations")

# Limitations
print(f"\n⚠ LIMITATIONS:")
print(f"  • No time-series data (single snapshot per patient)")
print(f"  • No continuous glucose monitoring (CGM) data")
print(f"  • No medication history")
print(f"  • No food intake logs")
print(f"\n💡 WORKAROUND:")
print(f"  Use this as the 'static profile' layer of your Digital Twin.")
print(f"  You can simulate time-series data or add synthetic CGM data later.")

print(f"\n{'='*70}")
print("NEXT STEPS")
print(f"{'='*70}")
print(f"\n1. ✓ Dataset validated - Ready to use!")
print(f"2. → Create patient twin JSON schema (use this data as baseline)")
print(f"3. → Build prediction models (HbA1c, Risk Assessment)")
print(f"4. → Set up database to store patient profiles")
print(f"5. → Build API endpoints for twin queries")

print(f"\n")
