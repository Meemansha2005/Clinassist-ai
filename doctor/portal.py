import streamlit as st

from database.database import (
    get_all_patients,
    get_patient,
)

from doctor.dashboard import show_doctor_dashboard

from ml.prediction import predict_conditions


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="ClinAssist Doctor Portal",
    page_icon="🩺",
    layout="wide",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🩺 ClinAssist Doctor Portal")
st.caption(
    "AI-Assisted Clinical History & Decision Support System"
)

st.info(
    "ClinAssist provides AI-assisted information for clinical "
    "review. The doctor remains responsible for the final "
    "clinical assessment and diagnosis."
)


# ---------------------------------------------------------
# LOAD PATIENTS
# ---------------------------------------------------------

patients = get_all_patients()


if not patients:

    st.warning(
        "No patient records are currently available."
    )

    st.stop()


# ---------------------------------------------------------
# PATIENT SELECTION
# ---------------------------------------------------------

st.subheader("📋 Select Patient")

patient_options = {
    f"{patient['id']} — {patient['name']}": patient["id"]
    for patient in patients
}

selected_patient_label = st.selectbox(
    "Choose a patient to review",
    list(patient_options.keys()),
)

patient_id = patient_options[selected_patient_label]

patient = get_patient(patient_id)


if not patient:

    st.error(
        "Unable to load the selected patient record."
    )

    st.stop()


# ---------------------------------------------------------
# BUILD CLINICAL TEXT
# ---------------------------------------------------------

clinical_parts = [
    patient.get("complaint", ""),
    patient.get("additional_symptoms", ""),
    patient.get("past_history", ""),
]

clinical_text = " ".join(
    str(part)
    for part in clinical_parts
    if part
)


# ---------------------------------------------------------
# RUN AI PROCESSING
# ---------------------------------------------------------

prediction = predict_conditions(
    clinical_text,
    top_n=3
)


# ---------------------------------------------------------
# SHOW DOCTOR DASHBOARD
# ---------------------------------------------------------

show_doctor_dashboard(
    patient=patient,
    prediction=prediction
)