from pathlib import Path

import joblib
import pandas as pd

from nlp.text_processor import extract_symptoms


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "clinassist_model.pkl"
ENCODER_PATH = BASE_DIR / "disease_encoder.pkl"
SYMPTOM_PATH = BASE_DIR / "symptom_list.pkl"


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

def load_model():
    """Load the trained ML model and supporting files."""

    if not (
        MODEL_PATH.exists()
        and ENCODER_PATH.exists()
        and SYMPTOM_PATH.exists()
    ):
        raise FileNotFoundError(
            "ML model files were not found. "
            "Make sure the model training has been completed."
        )

    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    symptom_list = joblib.load(SYMPTOM_PATH)

    return model, encoder, symptom_list


# --------------------------------------------------
# CREATE ML FEATURES
# --------------------------------------------------

def create_feature_dataframe(symptoms, symptom_list):
    """
    Convert detected symptoms into the exact feature
    structure expected by the trained model.
    """

    feature_values = {
        symptom: 0
        for symptom in symptom_list
    }

    for symptom in symptoms:
        if symptom in feature_values:
            feature_values[symptom] = 1

    features = pd.DataFrame(
        [feature_values],
        columns=symptom_list
    )

    return features


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

def predict_conditions(patient_text, top_n=3):
    """
    Process natural-language patient text,
    extract symptoms and return the top possible
    conditions to consider.

    These are model suggestions only and are not
    a medical diagnosis.
    """

    # Load model and symptom list first
    model, encoder, symptom_list = load_model()

    # NLP needs the same symptom list used by the ML model
    symptoms = extract_symptoms(
        patient_text,
        symptom_list
    )

    if not symptoms:
        return {
            "symptoms": [],
            "predictions": [],
            "message": "No recognized symptoms were found."
        }

    # Convert symptoms into ML features
    features = create_feature_dataframe(
        symptoms,
        symptom_list
    )

    # Get model scores
    probabilities = model.predict_proba(features)[0]

    # Get highest-scoring conditions
    ranked_indices = probabilities.argsort()[::-1][:top_n]

    predictions = []

    for index in ranked_indices:
        condition = encoder.inverse_transform([index])[0]
        score = float(probabilities[index]) * 100

        predictions.append({
            "condition": condition,
            "score": round(score, 2)
        })

    return {
        "symptoms": symptoms,
        "predictions": predictions,
        "message": "Possible conditions generated for doctor review."
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 45)
    print("CLINASSIST NLP → ML PREDICTION TEST")
    print("=" * 45)

    patient_text = (
        "I have a severe headache, "
        "I feel nauseous and very tired."
    )

    print("\nPatient Input:")
    print(patient_text)

    result = predict_conditions(patient_text)

    print("\nRecognized Symptoms:")

    for symptom in result["symptoms"]:
        print(f"- {symptom}")

    print("\nPossible Conditions to Consider:")

    for prediction in result["predictions"]:
        print(
            f"- {prediction['condition']}: "
            f"{prediction['score']:.2f}%"
        )

    print("\n" + "=" * 45)
    print("TEST COMPLETED")
    print("=" * 45)