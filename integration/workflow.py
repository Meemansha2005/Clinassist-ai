from ml.prediction import predict_conditions
from database.database import (
    initialize_database,
    save_patient,
    save_assessment,
)


def process_patient_case(patient):
    """
    Process a patient case through ClinAssist.

    Steps:
    1. Prepare the patient's clinical text.
    2. Run the ML prediction.
    3. Save the patient record.
    4. Return the results.

    The ML output is decision support only.
    """

    initialize_database()

    # ---------------------------------------------------------
    # BUILD CLINICAL TEXT
    # ---------------------------------------------------------

    clinical_parts = [
        patient.get("complaint", ""),
        patient.get("additional_symptoms", ""),
        patient.get("past_history", ""),
        patient.get("medications", ""),
        patient.get("allergies", ""),
    ]

    clinical_text = " ".join(
        str(part)
        for part in clinical_parts
        if part
    )

    # ---------------------------------------------------------
    # RUN ML PREDICTION
    # ---------------------------------------------------------

    prediction = predict_conditions(
        clinical_text,
        top_n=3
    )

    # ---------------------------------------------------------
    # SAVE PATIENT
    # ---------------------------------------------------------

    patient_id = save_patient(patient)

    # ---------------------------------------------------------
    # RETURN COMPLETE RESULT
    # ---------------------------------------------------------

    return {
        "patient_id": patient_id,
        "patient": patient,
        "prediction": prediction,
    }


def save_doctor_result(
    patient_id,
    urgency,
    prediction,
    doctor_assessment,
    final_diagnosis,
    treatment_plan
):
    """
    Save the doctor's assessment for an existing patient.
    """

    # Convert AI suggestions into readable text
    suggestions = []

    if prediction and prediction.get("predictions"):

        for item in prediction["predictions"]:

            condition = item.get(
                "condition",
                "Unknown"
            )

            score = float(
                item.get("score", 0)
            )

            suggestions.append(
                f"{condition} ({score * 100:.2f}%)"
            )

    ai_suggestions = ", ".join(suggestions)

    assessment_id = save_assessment(
        patient_id=patient_id,
        urgency=urgency,
        ai_suggestions=ai_suggestions,
        doctor_assessment=doctor_assessment,
        final_diagnosis=final_diagnosis,
        treatment_plan=treatment_plan,
    )

    return assessment_id