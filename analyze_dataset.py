import pandas as pd
from collections import Counter

df = pd.read_csv("data/Healthcare.csv")

print("=" * 60)
print("CLINASSIST DATASET ANALYSIS")
print("=" * 60)

print(f"\nTotal records: {len(df)}")
print(f"Total diseases: {df['Disease'].nunique()}")

symptom_counter = Counter()

for symptoms in df["Symptoms"].fillna(""):
    for symptom in str(symptoms).split(","):
        symptom = symptom.strip().lower()
        if symptom:
            symptom_counter[symptom] += 1

print("\nTotal unique symptoms:", len(symptom_counter))

print("\nMost common symptoms:")

for symptom, count in symptom_counter.most_common():
    print(f"{symptom:<30} {count}")

print("\n" + "=" * 60)
print("DISEASE → COMMON SYMPTOMS")
print("=" * 60)

for disease in sorted(df["Disease"].unique()):

    disease_data = df[df["Disease"] == disease]

    disease_symptoms = Counter()

    for symptoms in disease_data["Symptoms"].fillna(""):
        for symptom in str(symptoms).split(","):
            symptom = symptom.strip().lower()

            if symptom:
                disease_symptoms[symptom] += 1

    print(f"\n{disease}")
    print("-" * len(disease))

    for symptom, count in disease_symptoms.most_common(8):
        print(f"  {symptom}: {count}")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)