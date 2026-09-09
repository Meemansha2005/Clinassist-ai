import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder


print("=" * 60)
print("CLINASSIST - ML MODEL TRAINING")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD DATASET
# ---------------------------------------------------------

print("\nLoading dataset...")

train_df = pd.read_csv("data/Training.csv")
test_df = pd.read_csv("data/Testing.csv")

print("Training records:", len(train_df))
print("Testing records :", len(test_df))


# ---------------------------------------------------------
# 2. REMOVE UNNECESSARY CSV COLUMNS
# ---------------------------------------------------------

# Remove columns created accidentally by CSV formatting
train_df = train_df.loc[
    :, ~train_df.columns.str.startswith("Unnamed")
]

test_df = test_df.loc[
    :, ~test_df.columns.str.startswith("Unnamed")
]


# ---------------------------------------------------------
# 3. FIND TARGET COLUMN
# ---------------------------------------------------------

possible_targets = [
    "prognosis",
    "Disease",
    "disease",
    "Diagnosis"
]

target_column = None

for column in possible_targets:
    if column in train_df.columns:
        target_column = column
        break

if target_column is None:
    raise ValueError(
        "Could not find the disease/target column."
    )

print("\nTarget column:", target_column)


# ---------------------------------------------------------
# 4. SEPARATE FEATURES AND TARGET
# ---------------------------------------------------------

X_train = train_df.drop(columns=[target_column])
y_train = train_df[target_column]

X_test = test_df.drop(columns=[target_column])
y_test = test_df[target_column]


# ---------------------------------------------------------
# 5. MAKE TRAINING AND TESTING FEATURES MATCH
# ---------------------------------------------------------

# If a symptom column exists in one dataset but not the
# other, add it with value 0.

X_test = X_test.reindex(
    columns=X_train.columns,
    fill_value=0
)


# ---------------------------------------------------------
# 6. CONVERT FEATURES TO NUMERIC
# ---------------------------------------------------------

X_train = X_train.apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0)

X_test = X_test.apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0)


print("\nNumber of symptom features:", len(X_train.columns))
print("Number of diseases:", y_train.nunique())


# ---------------------------------------------------------
# 7. ENCODE DISEASE NAMES
# ---------------------------------------------------------

label_encoder = LabelEncoder()

y_train_encoded = label_encoder.fit_transform(y_train)

y_test_encoded = label_encoder.transform(y_test)


# ---------------------------------------------------------
# 8. TRAIN RANDOM FOREST
# ---------------------------------------------------------

print("\nTraining Random Forest model...")
print("Please wait...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train_encoded
)


# ---------------------------------------------------------
# 9. EVALUATE MODEL
# ---------------------------------------------------------

print("\nEvaluating model...")

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test_encoded,
    predictions
)


print("\n" + "=" * 60)
print("MODEL RESULTS")
print("=" * 60)

print(f"\nAccuracy: {accuracy * 100:.2f}%")


print("\nClassification Report:")

print(
    classification_report(
        y_test_encoded,
        predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ---------------------------------------------------------
# 10. SAVE MODEL
# ---------------------------------------------------------

print("\nSaving model files...")

joblib.dump(
    model,
    "clinassist_model.pkl"
)

joblib.dump(
    label_encoder,
    "disease_encoder.pkl"
)

joblib.dump(
    list(X_train.columns),
    "symptom_list.pkl"
)


# ---------------------------------------------------------
# 11. FINAL SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print("\nCreated files:")

print("  ✓ clinassist_model.pkl")
print("  ✓ disease_encoder.pkl")
print("  ✓ symptom_list.pkl")

print("\nSymptoms/features:", len(X_train.columns))
print("Diseases:", len(label_encoder.classes_))

print("\nClinAssist ML model is ready.")
print("=" * 60)