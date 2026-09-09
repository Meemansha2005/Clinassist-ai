from datetime import datetime


# --------------------------------------------------
# CREATE DOCTOR ASSESSMENT
# --------------------------------------------------

def create_assessment(
    doctor_name,
    final_assessment,
    doctor_notes,
    follow_up,
    confirmed_condition=None,
):
    """
    Create a structured doctor assessment.

    The doctor's assessment is kept separate from
    the AI-generated suggestions.
    """

    assessment = {
        "doctor_name": doctor_name.strip(),
        "confirmed_condition": (
            confirmed_condition.strip()
            if confirmed_condition
            else ""
        ),
        "final_assessment": final_assessment.strip(),
        "doctor_notes": doctor_notes.strip(),
        "follow_up": follow_up.strip(),
        "assessed_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    return assessment


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_assessment(assessment):
    """
    Validate the minimum information required
    for a doctor assessment.
    """

    required_fields = [
        "doctor_name",
        "final_assessment",
    ]

    missing_fields = []

    for field in required_fields:

        if not assessment.get(field):
            missing_fields.append(field)

    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


# --------------------------------------------------
# FORMAT ASSESSMENT
# --------------------------------------------------

def format_assessment(assessment):
    """
    Convert the assessment into a readable format.
    """

    return {
        "Doctor": assessment.get("doctor_name", ""),
        "Doctor-confirmed condition": assessment.get(
            "confirmed_condition",
            ""
        ),
        "Final assessment": assessment.get(
            "final_assessment",
            ""
        ),
        "Doctor notes": assessment.get(
            "doctor_notes",
            ""
        ),
        "Follow-up": assessment.get(
            "follow_up",
            ""
        ),
        "Assessed at": assessment.get(
            "assessed_at",
            ""
        ),
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("CLINASSIST DOCTOR ASSESSMENT TEST")
    print("=" * 55)

    assessment = create_assessment(
        doctor_name="Dr. Test",
        confirmed_condition="Example condition",
        final_assessment=(
            "Patient history reviewed and clinical "
            "assessment completed."
        ),
        doctor_notes=(
            "Review symptoms and relevant clinical findings."
        ),
        follow_up=(
            "Follow-up according to clinical assessment."
        ),
    )

    print("\nAssessment Created:")

    formatted = format_assessment(assessment)

    for key, value in formatted.items():
        print(f"{key}: {value}")

    print("\nValidation:")

    validation = validate_assessment(assessment)

    if validation["valid"]:
        print("✅ Assessment is valid.")
    else:
        print("❌ Missing required fields:")

        for field in validation["missing_fields"]:
            print(f"- {field}")

    print("\n" + "=" * 55)
    print("DOCTOR ASSESSMENT TEST COMPLETED")
    print("=" * 55)