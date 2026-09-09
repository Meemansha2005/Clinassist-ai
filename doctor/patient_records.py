import streamlit as st

from database.database import (
    get_all_patients,
    get_patient,
    get_patient_assessments,
)


def show_patient_records():
    """Display saved ClinAssist patient records."""

    st.title("📋 Patient Records")
    st.caption("View saved patient histories and previous assessments.")

    patients = get_all_patients()

    if not patients:
        st.info("No patient records have been saved yet.")
        return

    # ---------------------------------------------------------
    # PATIENT LIST
    # ---------------------------------------------------------

    st.subheader("Saved Patients")

    patient_options = {
        f"{patient['id']} — {patient['name']}": patient["id"]
        for patient in patients
    }

    selected_patient = st.selectbox(
        "Select a patient",
        list(patient_options.keys()),
    )

    patient_id = patient_options[selected_patient]

    patient = get_patient(patient_id)

    if not patient:
        st.error("Patient record could not be found.")
        return

    st.divider()

    # ---------------------------------------------------------
    # PATIENT INFORMATION
    # ---------------------------------------------------------

    st.subheader("👤 Patient Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Name**")
        st.write(patient["name"] or "Not provided")

    with col2:
        st.write("**Age**")
        st.write(patient["age"] or "Not provided")

    with col3:
        st.write("**Gender**")
        st.write(patient["gender"] or "Not provided")

    # ---------------------------------------------------------
    # CLINICAL HISTORY
    # ---------------------------------------------------------

    st.subheader("📝 Clinical History")

    history = {
        "Main Complaint": patient["complaint"],
        "Duration": patient["duration"],
        "Severity": patient["severity"],
        "Additional Symptoms": patient["additional_symptoms"],
        "Past Medical History": patient["past_history"],
        "Medications": patient["medications"],
        "Allergies": patient["allergies"],
    }

    for label, value in history.items():
        if value:
            st.write(f"**{label}:** {value}")

    # ---------------------------------------------------------
    # PREVIOUS ASSESSMENTS
    # ---------------------------------------------------------

    st.divider()
    st.subheader("🩺 Previous Doctor Assessments")

    assessments = get_patient_assessments(patient_id)

    if not assessments:
        st.info("No doctor assessments have been recorded yet.")
        return

    for index, assessment in enumerate(assessments, start=1):

        with st.expander(
            f"Assessment {index} — {assessment['created_at']}"
        ):

            st.write(
                f"**Urgency:** "
                f"{assessment['urgency'] or 'Not recorded'}"
            )

            st.write(
                f"**AI Suggestions:** "
                f"{assessment['ai_suggestions'] or 'Not recorded'}"
            )

            st.write(
                f"**Doctor Assessment:** "
                f"{assessment['doctor_assessment'] or 'Not recorded'}"
            )

            st.write(
                f"**Final Diagnosis / Impression:** "
                f"{assessment['final_diagnosis'] or 'Not recorded'}"
            )

            st.write(
                f"**Treatment / Management Plan:** "
                f"{assessment['treatment_plan'] or 'Not recorded'}"
            )


# ---------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    st.set_page_config(
        page_title="ClinAssist Patient Records",
        page_icon="📋",
        layout="wide",
    )

    show_patient_records()