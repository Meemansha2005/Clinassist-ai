import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


print("=" * 60)
print("CLINASSIST - MODEL VALIDATION")
print("=" * 60)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\nLoading training dataset...")

df = pd.read_csv("data/Training.csv")

# Remove accidental CSV columns
df = df.loc[
    :,
    ~df.columns.str.startswith("Unnamed")
]

print("Total records:", len(df))


# ============================================================
# 2. FIND TARGET COLUMN
# ============================================================

possible_targets = [
    "prognosis",
    "Disease",
    "disease",
    "Diagnosis"
]

target_column = None

for column in possible_targets:
    if column in df.columns:
        target_column = column
        break

if target_column is None:
    raise ValueError(
        "Could not find the disease/target column."
    )

print("Target column:", target_column)


# ============================================================
# 3. PREPARE FEATURES
# ============================================================

X = df.drop(columns=[target_column])
y = df[target_column]

X = X.apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0)

print("Number of features:", X.shape[1])
print("Number of diseases:", y.nunique())


# ============================================================
# 4. LOAD EXISTING MODEL
# ============================================================

print("\nLoading trained ClinAssist model...")

model = joblib.load(
    "clinassist_model.pkl"
)

encoder = joblib.load(
    "disease_encoder.pkl"
)

print("Model loaded successfully.")


# ============================================================
# 5. CREATE VALIDATION SPLIT
# ============================================================

print("\nCreating validation split...")

X_train, X_validation, y_train, y_validation = (
    train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
)

print("Training portion:", len(X_train))
print("Validation portion:", len(X_validation))


# ============================================================
# 6. TRAIN A VALIDATION MODEL
# ============================================================

print("\nTraining validation model...")
print("Please wait...")

from sklearn.ensemble import RandomForestClassifier

validation_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

y_train_encoded = encoder.transform(
    y_train
)

y_validation_encoded = encoder.transform(
    y_validation
)

validation_model.fit(
    X_train,
    y_train_encoded
)


# ============================================================
# 7. MAKE PREDICTIONS
# ============================================================

print("\nMaking predictions...")

predictions = validation_model.predict(
    X_validation
)


# ============================================================
# 8. OVERALL PERFORMANCE
# ============================================================

accuracy = accuracy_score(
    y_validation_encoded,
    predictions
)

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

print(
    f"\nValidation Accuracy: "
    f"{accuracy * 100:.2f}%"
)


# ============================================================
# 9. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_validation_encoded,
        predictions,
        target_names=encoder.classes_,
        zero_division=0
    )
)


# ============================================================
# 10. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_validation_encoded,
    predictions
)

print("\nConfusion Matrix Shape:")
print(cm.shape)


# Count correctly classified samples
correct = predictions == y_validation_encoded

print(
    "\nCorrect predictions:",
    correct.sum()
)

print(
    "Incorrect predictions:",
    (~correct).sum()
)


# ============================================================
# 11. ORIGINAL TEST SET CHECK
# ============================================================

print("\n" + "=" * 60)
print("ORIGINAL TEST SET CHECK")
print("=" * 60)

test_df = pd.read_csv(
    "data/Testing.csv"
)

test_df = test_df.loc[
    :,
    ~test_df.columns.str.startswith("Unnamed")
]

X_test = test_df.drop(
    columns=[target_column]
)

y_test = test_df[target_column]

X_test = X_test.reindex(
    columns=X.columns,
    fill_value=0
)

X_test = X_test.apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0)

y_test_encoded = encoder.transform(
    y_test
)

test_predictions = model.predict(
    X_test
)

test_accuracy = accuracy_score(
    y_test_encoded,
    test_predictions
)

print(
    f"\nOriginal 42-record test accuracy: "
    f"{test_accuracy * 100:.2f}%"
)


# ============================================================
# 12. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

print(
    "\nDataset:"
)

print(
    "  Training records :",
    len(df)
)

print(
    "  Validation records:",
    len(X_validation)
)

print(
    "  Original test records:",
    len(test_df)
)

print(
    "  Symptoms/features:",
    X.shape[1]
)

print(
    "  Diseases:",
    y.nunique()
)

print(
    "\nValidation accuracy:",
    f"{accuracy * 100:.2f}%"
)

print(
    "Original test accuracy:",
    f"{test_accuracy * 100:.2f}%"
)

print(
    "\nValidation complete."
)

print("=" * 60)