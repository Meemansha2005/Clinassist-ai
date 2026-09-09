import pandas as pd
from collections import Counter

df = pd.read_csv("data/Healthcare.csv")

print("=" * 60)
print("CLINASSIST - SYMPTOM COMBINATION ANALYSIS")
print("=" * 60)

# Normalize symptoms
df["Symptoms"] = df["Symptoms"].fillna("").apply(
    lambda x: tuple(sorted(
        symptom.strip().lower()
        for symptom in str(x).split(",")
        if symptom.strip()
    ))
)

# -----------------------------------------
# 1. How many symptoms does each record have?
# -----------------------------------------

symptom_counts = df["Symptoms"].apply(len)

print("\nSymptoms per record:")
print(symptom_counts.value_counts().sort_index())

print("\nAverage symptoms per record:",
      round(symptom_counts.mean(), 2))

# -----------------------------------------
# 2. Most common exact symptom combinations
# -----------------------------------------

combo_counts = Counter(df["Symptoms"])

print("\n" + "=" * 60)
print("MOST COMMON SYMPTOM COMBINATIONS")
print("=" * 60)

for combo, count in combo_counts.most_common(20):
    print(f"\n{count} records:")
    print("  " + ", ".join(combo))

# -----------------------------------------
# 3. Same symptom combination → diseases
# -----------------------------------------

print("\n" + "=" * 60)
print("SYMPTOM COMBINATION → DISEASE ANALYSIS")
print("=" * 60)

combo_diseases = {}

for combo in combo_counts:

    diseases = df[df["Symptoms"] == combo]["Disease"].value_counts()

    combo_diseases[combo] = diseases

print("\nExamples:\n")

shown = 0

for combo, diseases in combo_diseases.items():

    if len(diseases) > 1:

        print("\nSymptoms:")
        print("  " + ", ".join(combo))

        print("Diseases:")
        for disease, count in diseases.items():
            print(f"  {disease}: {count}")

        shown += 1

        if shown >= 15:
            break

# -----------------------------------------
# 4. Dataset quality check
# -----------------------------------------

print("\n" + "=" * 60)
print("DATASET QUALITY SUMMARY")
print("=" * 60)

print("\nTotal records:", len(df))
print("Total diseases:", df["Disease"].nunique())
print("Unique symptom combinations:", len(combo_counts))

print(
    "\nAverage records per disease:",
    round(len(df) / df["Disease"].nunique(), 2)
)

print("\nAnalysis complete.")