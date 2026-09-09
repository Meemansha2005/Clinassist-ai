from doctor.assessment import create_assessment, validate_assessment
from database.database import (
    save_doctor_assessment,
    get_doctor_assessment,
)


print("=" * 55)
print("CLINASSIST DOCTOR ASSESSMENT DATABASE TEST")
print("=" * 55)


# Create a sample assessment
assessment = create_assessment(
    doctor_name="Dr. Test",
    confirmed_condition="Example condition",
    final_assessment=(
        "Patient history reviewed and clinical "
        "assessment completed."
    ),
    doctor_notes=(
        "Doctor reviewed the patient's reported symptoms."
    ),
    follow_up=(
        "Follow-up according to clinical assessment."
    ),
)


# Validate assessment
validation = validate_assessment(assessment)

if not validation["valid"]:
    print("❌ Assessment validation failed.")

    for field in validation["missing_fields"]:
        print(f"- Missing: {field}")

    raise SystemExit(1)


print("\n✅ Assessment validation successful.")


# Use an existing patient ID
patient_id = 1

print(f"\nSaving assessment for Patient ID: {patient_id}")

assessment_id = save_doctor_assessment(
    patient_id,
    assessment
)

print(f"✅ Assessment saved.")
print(f"Assessment ID: {assessment_id}")


# Retrieve assessment
saved_assessment = get_doctor_assessment(
    patient_id
)

print("\nRetrieved Assessment:")

if saved_assessment:

    for key, value in saved_assessment.items():
        print(f"{key}: {value}")

else:

    print("❌ Assessment could not be retrieved.")
    raise SystemExit(1)


print("\n" + "=" * 55)
print("ASSESSMENT DATABASE TEST COMPLETED")
print("=" * 55)