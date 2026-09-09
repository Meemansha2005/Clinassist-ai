import streamlit as st


def show_doctor_dashboard(patient=None, prediction=None):
    """
    Display the ClinAssist doctor dashboard.

    The doctor remains responsible for the final clinical assessment.
    """

    st.title("🩺 Doctor Dashboard")
    st.caption("ClinAssist — AI-Assisted Clinical Decision Support")

    st.info(
        "AI-generated information is provided only as decision support. "
        "The doctor must make the final clinical assessment."
    )

    # ---------------------------------------------------------
    # PATIENT INFORMATION
    # ---------------------------------------------------------
    st.header("👤 Patient Information")

    if patient:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Name**")
            st.write(patient.get("name", "Not provided"))

        with col2:
            st.write("**Age**")
            st.write(patient.get("age", "Not provided"))

        with col3:
            st.write("**Gender**")
            st.write(patient.get("gender", "Not provided"))
    else:
        st.warning("No patient record has been selected.")

    st.divider()

    # ---------------------------------------------------------
    # CLINICAL HISTORY
    # ---------------------------------------------------------
    st.header("📝 Clinical History")

    if patient:
        history_items = {
            "Main Complaint": patient.get("complaint"),
            "Duration": patient.get("duration"),
            "Severity": patient.get("severity"),
            "Additional Symptoms": patient.get("additional_symptoms"),
            "Past Medical History": patient.get("past_history"),
            "Medication History": patient.get("medications"),
            "Allergies": patient.get("allergies"),
        }

        for label, value in history_items.items():
            if value:
                st.write(f"**{label}:** {value}")
    else:
        st.write("Clinical history will appear here.")

    st.divider()

    # ---------------------------------------------------------
    # DETECTED SYMPTOMS
    # ---------------------------------------------------------
    st.header("🔍 Detected Symptoms")

    if prediction and prediction.get("symptoms"):

        symptoms = prediction["symptoms"]

        cols = st.columns(min(len(symptoms), 4))

        for index, symptom in enumerate(symptoms):

            with cols[index % len(cols)]:
                st.success(
                    symptom.replace("_", " ").title()
                )

    else:
        st.write("No symptoms have been processed yet.")

    st.divider()

    # ---------------------------------------------------------
    # AI SUGGESTIONS
    # ---------------------------------------------------------
    st.header("🤖 Possible Conditions to Consider")

    if prediction and prediction.get("predictions"):

        for index, item in enumerate(
            prediction["predictions"],
            start=1
        ):

            condition = item.get(
                "condition",
                "Unknown"
            )

            score = float(
                item.get("score", 0)
            )

            st.write(
                f"### {index}. {condition}"
            )

            st.progress(
                min(max(score, 0.0), 1.0)
            )

            st.caption(
                f"Model score: {score * 100:.2f}%"
            )

    else:
        st.write(
            "No AI suggestions available."
        )

    st.warning(
        "These are model-generated suggestions, "
        "not a diagnosis. They should be reviewed "
        "together with the patient's clinical history."
    )

    st.divider()

    # ---------------------------------------------------------
    # URGENCY REVIEW
    # ---------------------------------------------------------
    st.header("⚠️ Urgency Review")

    urgency_options = [
        "No immediate concern identified",
        "Needs routine clinical review",
        "Needs prompt clinical review",
        "Potentially urgent — immediate clinical assessment required",
    ]

    urgency = st.selectbox(
        "Doctor's urgency assessment",
        urgency_options,
        key="doctor_urgency"
    )

    if "urgent" in urgency.lower():
        st.error(
            "Doctor has marked this case for urgent assessment."
        )

    elif "prompt" in urgency.lower():
        st.warning(
            "Doctor has marked this case for prompt review."
        )

    else:
        st.info(
            "Urgency level selected by doctor."
        )

    st.divider()

    # ---------------------------------------------------------
    # DOCTOR ASSESSMENT
    # ---------------------------------------------------------
    st.header("👨‍⚕️ Doctor's Assessment")

    final_assessment = st.text_area(
        "Final clinical assessment",
        placeholder=(
            "Enter the doctor's assessment..."
        ),
        height=150,
        key="doctor_assessment"
    )

    final_diagnosis = st.text_input(
        "Final diagnosis / impression",
        placeholder=(
            "Enter after clinical evaluation..."
        ),
        key="final_diagnosis"
    )

    treatment_plan = st.text_area(
        "Treatment / management plan",
        placeholder=(
            "Enter the doctor's management plan..."
        ),
        height=120,
        key="treatment_plan"
    )

    # ---------------------------------------------------------
    # SAVE ASSESSMENT
    # ---------------------------------------------------------
    if st.button(
        "💾 Save Doctor Assessment",
        type="primary",
        width="stretch"
    ):

        st.session_state[
            "doctor_assessment_data"
        ] = {
            "urgency": urgency,
            "assessment": final_assessment,
            "diagnosis": final_diagnosis,
            "treatment_plan": treatment_plan,
        }

        st.success(
            "Doctor assessment captured successfully."
        )