from ml.prediction import predict_conditions
from risk.urgency import detect_urgency


def analyze_patient(patient_text, top_n=3):
    """
    Run the complete ClinAssist analysis pipeline.

    Pipeline:
        Patient text
            ↓
        NLP symptom extraction
            ↓
        ML condition ranking
            ↓
        Urgency screening

    The returned conditions are suggestions for
    doctor review, not diagnoses.
    """

    if not patient_text or not str(patient_text).strip():
        return {
            "symptoms": [],
            "predictions": [],
            "urgency": {
                "urgent": False,
                "flags": [],
                "matched_phrases": [],
                "message": "No patient text was provided."
            }
        }

    # ----------------------------------------------
    # NLP + ML
    # ----------------------------------------------

    prediction_result = predict_conditions(
        patient_text,
        top_n=top_n
    )

    # ----------------------------------------------
    # URGENCY SCREENING
    # ----------------------------------------------

    urgency_result = detect_urgency(patient_text)

    # ----------------------------------------------
    # COMBINED RESULT
    # ----------------------------------------------

    return {
        "symptoms": prediction_result["symptoms"],
        "predictions": prediction_result["predictions"],
        "urgency": urgency_result
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("CLINASSIST COMPLETE CLINICAL ANALYSIS TEST")
    print("=" * 55)

    patient_text = (
        "I have a severe headache and I feel nauseous. "
        "I am also having severe difficulty breathing."
    )

    print("\nPatient Input:")
    print(patient_text)

    result = analyze_patient(patient_text)

    print("\nRecognized Symptoms:")

    for symptom in result["symptoms"]:
        print(f"- {symptom}")

    print("\nPossible Conditions to Consider:")

    for prediction in result["predictions"]:
        print(
            f"- {prediction['condition']}: "
            f"{prediction['score']:.2f}%"
        )

    print("\nUrgency Review:")

    if result["urgency"]["urgent"]:

        print("🚨 Potential urgency indicators detected.")

        for flag in result["urgency"]["flags"]:
            print(f"- {flag}")

        print("\nMessage:")
        print(result["urgency"]["message"])

    else:

        print("✅ No predefined urgency indicators detected.")

    print("\n" + "=" * 55)
    print("CLINICAL ANALYSIS TEST COMPLETED")
    print("=" * 55)