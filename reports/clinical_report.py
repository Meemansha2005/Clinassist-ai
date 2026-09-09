from datetime import datetime


# --------------------------------------------------
# CREATE CLINICAL REPORT
# --------------------------------------------------

def create_clinical_report(
    patient,
    analysis,
    assessment=None
):
    """
    Combine patient information, AI-assisted analysis,
    urgency screening, and doctor assessment into one
    structured clinical report.

    AI suggestions are kept separate from the doctor's
    final assessment.
    """

    urgency = analysis.get(
        "urgency",
        {
            "urgent": False,
            "flags": [],
            "matched_phrases": [],
            "message": "",
        }
    )

    report = {
        "report_title": "ClinAssist Clinical Assessment Report",

        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        # ------------------------------------------
        # PATIENT INFORMATION
        # ------------------------------------------

        "patient_information": {
            "patient_id": patient.get("id", ""),
            "name": patient.get("name", ""),
            "age": patient.get("age", ""),
            "gender": patient.get("gender", ""),
        },

        # ------------------------------------------
        # CLINICAL HISTORY
        # ------------------------------------------

        "clinical_history": {
            "presenting_complaint": patient.get(
                "complaint",
                ""
            ),
            "duration": patient.get(
                "duration",
                ""
            ),
            "severity": patient.get(
                "severity",
                ""
            ),
            "additional_symptoms": patient.get(
                "additional_symptoms",
                ""
            ),
            "past_history": patient.get(
                "past_history",
                ""
            ),
            "medications": patient.get(
                "medications",
                ""
            ),
            "allergies": patient.get(
                "allergies",
                ""
            ),
        },

        # ------------------------------------------
        # AI-ASSISTED ANALYSIS
        # ------------------------------------------

        "ai_analysis": {
            "detected_symptoms": analysis.get(
                "symptoms",
                []
            ),
            "possible_conditions": analysis.get(
                "predictions",
                []
            ),
        },

        # ------------------------------------------
        # URGENCY REVIEW
        # ------------------------------------------

        "urgency_review": {
            "urgent": urgency.get(
                "urgent",
                False
            ),
            "flags": urgency.get(
                "flags",
                []
            ),
            "matched_phrases": urgency.get(
                "matched_phrases",
                []
            ),
            "message": urgency.get(
                "message",
                ""
            ),
        },

        # ------------------------------------------
        # DOCTOR ASSESSMENT
        # ------------------------------------------

        "doctor_assessment": assessment or {},

        # ------------------------------------------
        # DISCLAIMER
        # ------------------------------------------

        "disclaimer": (
            "AI-generated information is intended only "
            "to support clinical review and does not "
            "replace professional clinical judgment."
        ),
    }

    return report


# --------------------------------------------------
# FORMAT REPORT
# --------------------------------------------------

def format_clinical_report(report):
    """
    Convert the structured report into readable text.
    """

    lines = []

    lines.append("=" * 60)
    lines.append("CLINASSIST")
    lines.append("Clinical Assessment Report")
    lines.append("=" * 60)

    lines.append(
        f"\nGenerated: {report.get('generated_at', '')}"
    )

    # ------------------------------------------
    # PATIENT INFORMATION
    # ------------------------------------------

    lines.append("\nPATIENT INFORMATION")
    lines.append("-" * 60)

    patient = report.get(
        "patient_information",
        {}
    )

    lines.append(
        f"Patient ID: {patient.get('patient_id', '')}"
    )

    lines.append(
        f"Name: {patient.get('name', '')}"
    )

    lines.append(
        f"Age: {patient.get('age', '')}"
    )

    lines.append(
        f"Gender: {patient.get('gender', '')}"
    )

    # ------------------------------------------
    # CLINICAL HISTORY
    # ------------------------------------------

    lines.append("\nCLINICAL HISTORY")
    lines.append("-" * 60)

    history = report.get(
        "clinical_history",
        {}
    )

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

        lines.append(
            f"{label}: {history.get(key, '')}"
        )

    # ------------------------------------------
    # AI ANALYSIS
    # ------------------------------------------

    lines.append("\nAI-ASSISTED ANALYSIS")
    lines.append("-" * 60)

    ai_analysis = report.get(
        "ai_analysis",
        {}
    )

    symptoms = ai_analysis.get(
        "detected_symptoms",
        []
    )

    lines.append("Detected Symptoms:")

    if symptoms:

        for symptom in symptoms:
            lines.append(f"- {symptom}")

    else:

        lines.append("- None detected")

    lines.append("\nPossible Conditions to Consider:")

    predictions = ai_analysis.get(
        "possible_conditions",
        []
    )

    if predictions:

        for number, prediction in enumerate(
            predictions,
            start=1
        ):

            lines.append(
                f"{number}. "
                f"{prediction.get('condition', '')} "
                f"({prediction.get('score', 0):.2f}%)"
            )

    else:

        lines.append("- None")

    # ------------------------------------------
    # URGENCY REVIEW
    # ------------------------------------------

    lines.append("\nURGENCY REVIEW")
    lines.append("-" * 60)

    urgency = report.get(
        "urgency_review",
        {}
    )

    if urgency.get("urgent", False):

        lines.append(
            "🚨 Potential urgency indicators detected."
        )

        flags = urgency.get(
            "flags",
            []
        )

        for flag in flags:
            lines.append(f"- {flag}")

    else:

        lines.append(
            "No predefined urgency indicators detected."
        )

    lines.append(
        f"Message: {urgency.get('message', '')}"
    )

    # ------------------------------------------
    # DOCTOR ASSESSMENT
    # ------------------------------------------

    lines.append("\nDOCTOR ASSESSMENT")
    lines.append("-" * 60)

    assessment = report.get(
        "doctor_assessment",
        {}
    )

    if assessment:

        lines.append(
            f"Doctor: "
            f"{assessment.get('doctor_name', '')}"
        )

        lines.append(
            f"Doctor-confirmed condition: "
            f"{assessment.get('confirmed_condition', '')}"
        )

        lines.append(
            f"Final assessment: "
            f"{assessment.get('final_assessment', '')}"
        )

        lines.append(
            f"Doctor notes: "
            f"{assessment.get('doctor_notes', '')}"
        )

        lines.append(
            f"Follow-up: "
            f"{assessment.get('follow_up', '')}"
        )

        lines.append(
            f"Assessed at: "
            f"{assessment.get('assessed_at', '')}"
        )

    else:

        lines.append(
            "Doctor assessment has not been completed."
        )

    # ------------------------------------------
    # DISCLAIMER
    # ------------------------------------------

    lines.append("\n" + "=" * 60)
    lines.append("IMPORTANT")
    lines.append("=" * 60)

    lines.append(
        report.get("disclaimer", "")
    )

    lines.append("=" * 60)

    return "\n".join(lines)


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("CLINASSIST CLINICAL REPORT TEST")
    print("=" * 60)

    # Sample patient
    patient = {
        "id": 1,
        "name": "Test Patient",
        "age": 25,
        "gender": "Female",
        "complaint": "Headache",
        "duration": "2 days",
        "severity": "Moderate",
        "additional_symptoms": "Nausea and fatigue",
        "past_history": "None",
        "medications": "None",
        "allergies": "None",
    }

    # Sample AI analysis
    analysis = {
        "symptoms": [
            "headache",
            "nausea",
            "fatigue",
        ],

        "predictions": [
            {
                "condition": "Example Condition 1",
                "score": 35.50,
            },
            {
                "condition": "Example Condition 2",
                "score": 22.30,
            },
            {
                "condition": "Example Condition 3",
                "score": 12.80,
            },
        ],

        "urgency": {
            "urgent": False,
            "flags": [],
            "matched_phrases": [],
            "message": (
                "No predefined urgency indicators "
                "were detected by this screening module."
            ),
        },
    }

    # Sample doctor assessment
    assessment = {
        "doctor_name": "Dr. Test",
        "confirmed_condition": "Example Condition 1",
        "final_assessment": (
            "Patient history reviewed and clinical "
            "assessment completed."
        ),
        "doctor_notes": (
            "Patient should be reviewed based on "
            "clinical findings."
        ),
        "follow_up": (
            "Follow-up according to clinical assessment."
        ),
        "assessed_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    # Create report
    report = create_clinical_report(
        patient,
        analysis,
        assessment
    )

    # Format report
    formatted_report = format_clinical_report(
        report
    )

    print("\n")
    print(formatted_report)

    print("\n")
    print("=" * 60)
    print("CLINICAL REPORT TEST COMPLETED")
    print("=" * 60)