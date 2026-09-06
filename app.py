import streamlit as st

st.set_page_config(
    page_title="ClinAssist",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 ClinAssist")
st.subheader("AI-Powered Clinical History & Decision Support System")

st.info(
    "ClinAssist is a decision-support prototype. "
    "Final diagnosis and treatment decisions must be made by a qualified doctor."
)

st.markdown("## 👤 Patient Information")

name = st.text_input("Patient Name")

age = st.number_input(
    "Age",
    min_value=0,
    max_value=120,
    step=1
)

gender = st.selectbox(
    "Gender",
    ["Select", "Male", "Female", "Other"]
)

st.markdown("## 📝 Clinical History")

st.markdown("### 1. Presenting Complaint")

complaint = st.text_area(
    "What is the main problem or symptom?",
    placeholder="Describe the main complaint in your own words..."
)

duration = st.text_input(
    "How long have you had this problem?"
)

severity = st.slider(
    "How severe is the problem?",
    min_value=0,
    max_value=10,
    value=5
)

st.markdown("### 2. Associated Symptoms")

associated_symptoms = st.text_area(
    "Are you experiencing any other symptoms?",
    placeholder="List any other symptoms..."
)

st.markdown("### 3. Medical History")

past_history = st.text_area(
    "Do you have any previous medical conditions?"
)

medications = st.text_area(
    "Are you currently taking any medicines?"
)

allergies = st.text_area(
    "Do you have any known allergies?"
)

st.markdown("### 4. Family & Personal History")

family_history = st.text_area(
    "Any important medical conditions in your family?"
)

personal_history = st.text_area(
    "Any relevant personal history?"
)

if st.button("Submit Clinical History"):

    if name and complaint and duration and gender != "Select":

        st.success("Clinical history recorded successfully.")

        st.markdown("## 📋 History Summary")

        st.write("**Patient Name:**", name)
        st.write("**Age:**", age)
        st.write("**Gender:**", gender)
        st.write("**Main Complaint:**", complaint)
        st.write("**Duration:**", duration)
        st.write("**Severity:**", severity, "/ 10")
        st.write("**Associated Symptoms:**", associated_symptoms)
        st.write("**Past Medical History:**", past_history)
        st.write("**Current Medications:**", medications)
        st.write("**Allergies:**", allergies)
        st.write("**Family History:**", family_history)
        st.write("**Personal History:**", personal_history)

    else:

        st.warning(
            "Please enter the patient's name, gender, main complaint, and duration."
        )