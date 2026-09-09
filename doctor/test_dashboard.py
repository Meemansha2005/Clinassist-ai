import streamlit as st

from doctor.dashboard import show_doctor_dashboard
from ml.prediction import predict_conditions


st.set_page_config(
    page_title="ClinAssist Doctor Dashboard",
    page_icon="🩺",
    layout="wide"
)


patient = {
    "name": "Test Patient",
    "age": 25,
    "gender": "Female",
    "complaint": "Headache and nausea",
    "duration": "2 days",
    "severity": "Moderate",
    "additional_symptoms": "Nausea and fatigue",
    "past_history": "No significant history",
    "medications": "None reported",
    "allergies": "None reported",
}


patient_text = """
I have a severe headache and I feel nauseous.
I am also feeling very tired.
"""


prediction = predict_conditions(
    patient_text,
    top_n=3
)


show_doctor_dashboard(
    patient=patient,
    prediction=prediction
)