from datetime import datetime


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize_prediction(prediction):
    """Convert tuple/list/dict prediction formats into one format."""
    if isinstance(prediction, dict):
        condition = prediction.get("condition", "")
        score = prediction.get(
            "score",
            prediction.get("probability", 0)
        )
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        # App predictions store probability as 0-1.
        if 0 <= score <= 1:
            score *= 100

        return {
            "condition": str(condition),
            "score": score,
        }

    if isinstance(prediction, (tuple, list)) and len(prediction) >= 2:
        condition = prediction[0]
        score = prediction[1]
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        if 0 <= score <= 1:
            score *= 100

        return {
            "condition": str(condition),
            "score": score,
        }

    return {
        "condition": str(prediction),
        "score": 0.0,
    }


def get_analysis_symptoms(analysis):
    """Support both the old and current analysis key names."""
    symptoms = analysis.get("detected_symptoms")
    if symptoms is None:
        symptoms = analysis.get("symptoms", [])
    return list(symptoms or [])


def get_analysis_urgency(analysis):
    """Support both the old urgency object and current flag list."""
    urgency = analysis.get("urgency")

    if isinstance(urgency, dict):
        return {
            "urgent": bool(urgency.get("urgent", False)),
            "flags": list(urgency.get("flags", []) or []),
            "matched_phrases": list(
                urgency.get("matched_phrases", []) or []
            ),
            "message": str(urgency.get("message", "")),
        }

    flags = analysis.get("urgency_flags", []) or []

    return {
        "urgent": bool(flags),
        "flags": list(flags),
        "matched_phrases": [],
        "message": (
            "Potential urgency indicators were detected."
            if flags
            else
            "No predefined urgency indicators were detected."
        ),
    }


def build_adaptive_history(patient):
    """Collect every adaptive Step 4 answer that exists."""
    fields = [
        ("Pain Location", "pain_location"),
        ("Head-related Associated Symptoms", "head_associated"),
        ("Cough Type", "cough_type"),
        ("Breathing Difficulty", "breathing"),
        ("Occurs After Eating", "food_relation"),
        ("Vomiting or Nausea", "vomiting"),
        ("Skin Problem Description", "skin_appearance"),
        ("Skin Problem Duration", "skin_duration"),
        ("Additional Details", "additional_details"),
    ]

    result = {}
    for label, key in fields:
        value = patient.get(key, "")
        if value is not None and str(value).strip():
            result[label] = str(value).strip()

    return result


# --------------------------------------------------
# CREATE CLINICAL REPORT
# --------------------------------------------------

def create_clinical_report(patient, analysis, assessment=None):
    """
    Build the structured ClinAssist report from the exact
    patient/session data shown in the application.

    The function accepts both the older analysis schema and
    the current Streamlit schema so report generation does
    not silently turn valid data into N/A/blank fields.
    """

    patient = dict(patient or {})
    analysis = dict(analysis or {})

    # The app stores the patient ID separately in session state.
    # If it has already been copied into patient, keep it.
    patient_id = patient.get("id", patient.get("patient_id", ""))

    symptoms = get_analysis_symptoms(analysis)
    raw_predictions = analysis.get("predictions", []) or analysis.get(
        "possible_conditions", []
    )
    predictions = [
        normalize_prediction(prediction)
        for prediction in raw_predictions
    ]
    urgency = get_analysis_urgency(analysis)

    report = {
        "report_title": "ClinAssist Clinical Assessment Report",
        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "patient_information": {
            "patient_id": patient_id,
            "name": patient.get("name", ""),
            "age": patient.get("age", ""),
            "gender": patient.get("gender", ""),
        },

        "clinical_history": {
            "presenting_complaint": patient.get("complaint", ""),
            "duration": patient.get("duration", ""),
            "severity": patient.get("severity", ""),
            "additional_symptoms": patient.get(
                "additional_symptoms", ""
            ),
            "past_history": patient.get("past_history", ""),
            "medications": patient.get("medications", ""),
            "allergies": patient.get("allergies", ""),
            "adaptive_questions": build_adaptive_history(patient),
        },

        "ai_analysis": {
            "detected_symptoms": symptoms,
            "possible_conditions": predictions,
        },

        "urgency_review": urgency,

        "doctor_assessment": dict(assessment or {}),

        "disclaimer": (
            "AI-generated information is intended only to support "
            "clinical review and does not replace professional "
            "clinical judgment. Final clinical decisions remain "
            "the responsibility of a qualified healthcare professional."
        ),
    }

    return report


# --------------------------------------------------
# FORMAT REPORT
# --------------------------------------------------

def format_clinical_report(report):
    """Convert the structured report into readable text."""

    lines = []
    lines.append("=" * 60)
    lines.append("CLINASSIST")
    lines.append("Clinical Assessment Report")
    lines.append("=" * 60)
    lines.append(
        f"\nGenerated: {report.get('generated_at', '')}"
    )

    patient = report.get("patient_information", {})
    lines.append("\nPATIENT INFORMATION")
    lines.append("-" * 60)
    lines.append(f"Patient ID: {patient.get('patient_id', '')}")
    lines.append(f"Name: {patient.get('name', '')}")
    lines.append(f"Age: {patient.get('age', '')}")
    lines.append(f"Gender: {patient.get('gender', '')}")

    history = report.get("clinical_history", {})
    lines.append("\nCLINICAL HISTORY")
    lines.append("-" * 60)

    history_fields = [
        ("Presenting Complaint", "presenting_complaint"),
        ("Duration", "duration"),
        ("Severity", "severity"),
        ("Additional Symptoms", "additional_symptoms"),
        ("Past History", "past_history"),
        ("Medications", "medications"),
        ("Allergies", "allergies"),
    ]

    for label, key in history_fields:
        value = history.get(key, "")
        lines.append(f"{label}: {value}")

    adaptive = history.get("adaptive_questions", {})
    if adaptive:
        lines.append("\nADAPTIVE QUESTIONS")
        lines.append("-" * 60)
        for label, value in adaptive.items():
            lines.append(f"{label}: {value}")

    ai_analysis = report.get("ai_analysis", {})
    lines.append("\nAI-ASSISTED ANALYSIS")
    lines.append("-" * 60)
    symptoms = ai_analysis.get("detected_symptoms", [])
    lines.append("Detected Symptoms:")
    if symptoms:
        for symptom in symptoms:
            lines.append(f"- {symptom}")
    else:
        lines.append("- None detected")

    lines.append("\nPossible Conditions to Consider:")
    predictions = ai_analysis.get("possible_conditions", [])
    if predictions:
        for number, prediction in enumerate(predictions, start=1):
            normalized = normalize_prediction(prediction)
            lines.append(
                f"{number}. {normalized['condition']} "
                f"({normalized['score']:.2f}%)"
            )
    else:
        lines.append("- None")

    urgency = report.get("urgency_review", {})
    lines.append("\nURGENCY REVIEW")
    lines.append("-" * 60)
    if urgency.get("urgent", False):
        lines.append("Potential urgency indicators detected.")
        for flag in urgency.get("flags", []):
            lines.append(f"- {flag}")
    else:
        lines.append("No predefined urgency indicators detected.")
    lines.append(f"Message: {urgency.get('message', '')}")

    assessment = report.get("doctor_assessment", {})
    lines.append("\nDOCTOR ASSESSMENT")
    lines.append("-" * 60)
    if assessment:
        lines.append(f"Doctor: {assessment.get('doctor_name', '')}")
        lines.append(
            "Doctor-confirmed condition: "
            f"{assessment.get('confirmed_condition', '')}"
        )
        lines.append(
            f"Final assessment: {assessment.get('final_assessment', '')}"
        )
        lines.append(
            f"Doctor notes: {assessment.get('doctor_notes', '')}"
        )
        lines.append(f"Follow-up: {assessment.get('follow_up', '')}")
        lines.append(
            f"Assessed at: {assessment.get('assessed_at', '')}"
        )
    else:
        lines.append("Doctor assessment has not been completed.")

    lines.append("\n" + "=" * 60)
    lines.append("IMPORTANT")
    lines.append("=" * 60)
    lines.append(report.get("disclaimer", ""))
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    sample_patient = {
        "id": 1,
        "name": "Test Patient",
        "age": 25,
        "gender": "Female",
        "complaint": "My head has been hurting",
        "duration": "2 days",
        "severity": "Moderate",
        "additional_symptoms": "Nausea and fatigue",
        "pain_location": "Forehead",
        "head_associated": "Nausea",
        "past_history": "None",
        "medications": "None",
        "allergies": "None",
    }

    sample_analysis = {
        "detected_symptoms": ["headache", "nausea", "fatigue"],
        "predictions": [
            ("Example Condition 1", 0.355),
            ("Example Condition 2", 0.223),
            ("Example Condition 3", 0.128),
        ],
        "urgency_flags": [],
    }

    report = create_clinical_report(
        sample_patient,
        sample_analysis,
        {
            "doctor_name": "Dr. Test",
            "confirmed_condition": "Example Condition 1",
            "final_assessment": "Assessment completed.",
            "doctor_notes": "Review according to clinical findings.",
            "follow_up": "As advised by the clinician.",
            "assessed_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        },
    )

    print(format_clinical_report(report))
