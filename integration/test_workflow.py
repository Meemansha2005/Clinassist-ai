from integration.workflow import process_patient_case


test_patient = {
    "name": "Integration Test Patient",
    "age": 30,
    "gender": "Female",
    "complaint": "Headache",
    "duration": "2 days",
    "severity": "Moderate",
    "additional_symptoms": "Nausea and fatigue",
    "past_history": "None reported",
    "medications": "None reported",
    "allergies": "None reported",
}


result = process_patient_case(test_patient)


print("\n================================")
print("CLINASSIST WORKFLOW TEST")
print("================================")

print("\nPatient ID:")
print(result["patient_id"])

print("\nDetected Symptoms:")
print(result["prediction"]["symptoms"])

print("\nPossible Conditions:")

for item in result["prediction"]["predictions"]:
    print(
        f"- {item['condition']}: "
        f"{item['score'] * 100:.2f}%"
    )

print("\n================================")
print("WORKFLOW TEST SUCCESSFUL")
print("================================")