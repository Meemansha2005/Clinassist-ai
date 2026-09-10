import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

from database.database import initialize_database, save_patient, get_doctor_assessment, save_doctor_assessment
from reports.clinical_report import create_clinical_report
from reports.pdf_report import export_report_to_pdf
from language.translations import get_translation
from nlp.text_processor import extract_symptoms

try:
    from voice.speech_to_text import speech_to_text, is_successful, get_voice_language
    VOICE_AVAILABLE = True
except Exception:
    speech_to_text = None
    is_successful = None
    get_voice_language = None
    VOICE_AVAILABLE = False

try:
    from ocr.medical_document_ocr import analyze_medical_document
    OCR_AVAILABLE = True
except Exception:
    analyze_medical_document = None
    OCR_AVAILABLE = False

st.set_page_config(
    page_title="ClinAssist",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

TOTAL_STEPS = 8
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "clinassist_model.pkl"
ENCODER_PATH = BASE_DIR / "disease_encoder.pkl"
SYMPTOM_LIST_PATH = BASE_DIR / "symptom_list.pkl"

initialize_database()

DEFAULTS = {
    "current_step": 1,
    "patient": {},
    "patient_saved": False,
    "patient_id": None,
    "pdf_path": None,
    "language": "English",
    "voice_message": "",
    "ocr_uploaded_name": "",
    "ocr_extracted_text": "",
    "ocr_summary": "",
    "ocr_symptoms": [],
    "ocr_conditions": [],
    "ocr_medications": [],
    "ocr_allergies": [],
    "ocr_findings": [],
    "ocr_error": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        if isinstance(value, dict):
            st.session_state[key] = dict(value)
        elif isinstance(value, list):
            st.session_state[key] = list(value)
        else:
            st.session_state[key] = value


def t(text):
    try:
        return get_translation(text, st.session_state.language)
    except Exception:
        return text


def go_next():
    if st.session_state.current_step < TOTAL_STEPS:
        st.session_state.current_step += 1


def go_back():
    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1


def reset_application():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    for key, value in DEFAULTS.items():
        if isinstance(value, dict):
            st.session_state[key] = dict(value)
        elif isinstance(value, list):
            st.session_state[key] = list(value)
        else:
            st.session_state[key] = value


def detect_problem_types(text):
    text = str(text).lower()
    groups = {
        "head": [
            "headache", "head pain", "head hurts", "head hurting", "dizziness",
            "vertigo", "migraine", "head ache"
        ],
        "respiratory": [
            "cough", "breathing", "breathlessness", "shortness of breath", "phlegm",
            "chest congestion", "wheezing", "sputum", "breathing difficulty"
        ],
        "digestive": [
            "stomach", "abdominal", "vomiting", "nausea", "diarrhea", "constipation",
            "acidity", "indigestion", "gastric", "belly", "digestive"
        ],
        "skin": [
            "rash", "itching", "skin", "red spots", "pimples", "blisters", "itchy",
            "skin problem"
        ],
    }
    found = []
    for category, words in groups.items():
        if any(word in text for word in words):
            found.append(category)
    return found or ["general"]


def problem_label(problem):
    labels = {
        "head": "Head-related",
        "respiratory": "Respiratory",
        "digestive": "Digestive",
        "skin": "Skin-related",
        "general": "General",
    }
    return labels.get(problem, "General")


def urgency_flags(text):
    text = str(text).lower()
    rules = {
        "Severe breathing difficulty": [
            "severe difficulty breathing", "severe trouble breathing", "cannot breathe",
            "can't breathe", "unable to breathe", "extreme breathlessness"
        ],
        "Severe chest discomfort": [
            "severe chest pain", "severe chest discomfort", "crushing chest pain",
            "pressure in chest", "heavy pressure in chest"
        ],
        "Loss of consciousness": [
            "lost consciousness", "loss of consciousness", "passed out", "fainted",
            "unconscious"
        ],
        "Sudden neurological symptoms": [
            "sudden weakness", "sudden numbness", "sudden confusion", "difficulty speaking",
            "unable to speak", "sudden vision loss", "sudden severe headache"
        ],
        "Severe bleeding": [
            "severe bleeding", "heavy bleeding", "bleeding heavily", "uncontrolled bleeding"
        ],
        "Severe allergic reaction indicators": [
            "swelling of face", "swelling of throat", "throat swelling", "difficulty swallowing",
            "difficulty breathing after eating"
        ],
    }
    found = []
    for category, phrases in rules.items():
        if any(phrase in text for phrase in phrases):
            found.append(category)
    return found


@st.cache_resource

def load_ml_model():
    missing = [
        str(path.name)
        for path in [MODEL_PATH, ENCODER_PATH, SYMPTOM_LIST_PATH]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Required ML file(s) missing: " + ", ".join(missing)
        )
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    symptom_list = list(joblib.load(SYMPTOM_LIST_PATH))
    return model, encoder, symptom_list


def get_patient_text(patient):
    fields = [
        "complaint",
        "duration",
        "severity",
        "additional_symptoms",
        "pain_location",
        "head_associated",
        "cough_type",
        "breathing",
        "food_relation",
        "vomiting",
        "skin_appearance",
        "skin_duration",
        "additional_details",
        "past_history",
        "medications",
        "allergies",
        "family_history",
        "personal_history",
        "ocr_summary",
    ]
    parts = []
    for field in fields:
        value = patient.get(field, "")
        if value is not None and str(value).strip():
            parts.append(str(value).strip())
    for field in ["ocr_symptoms", "ocr_conditions", "ocr_medications", "ocr_findings"]:
        values = patient.get(field, [])
        if isinstance(values, list) and values:
            parts.extend(str(item) for item in values if str(item).strip())
    return " ".join(parts)


def run_ml_decision_support(patient_text):
    model, encoder, symptom_list = load_ml_model()
    detected = extract_symptoms(patient_text, symptom_list)
    detected = list(dict.fromkeys(detected))
    values = [1 if symptom in detected else 0 for symptom in symptom_list]
    feature_df = pd.DataFrame([values], columns=symptom_list)
    probabilities = model.predict_proba(feature_df)[0]
    positions = probabilities.argsort()[-3:][::-1]
    model_classes = getattr(model, "classes_", None)
    predictions = []
    for position in positions:
        position = int(position)
        encoded_class = model_classes[position] if model_classes is not None else position
        condition = None
        try:
            condition = encoder.inverse_transform([encoded_class])[0]
        except Exception:
            try:
                condition = encoder.inverse_transform([position])[0]
            except Exception:
                condition = str(encoded_class)
        predictions.append((str(condition), float(probabilities[position])))
    return detected, predictions


def database_patient_data(patient):
    fields = [
        "name",
        "age",
        "gender",
        "complaint",
        "duration",
        "severity",
        "additional_symptoms",
        "past_history",
        "medications",
        "allergies",
        "family_history",
        "personal_history",
        "problem_type",
        "pain_location",
        "head_associated",
        "cough_type",
        "breathing",
        "food_relation",
        "vomiting",
        "skin_appearance",
        "skin_duration",
        "additional_details",
    ]
    return {field: patient.get(field, "") for field in fields}


def save_patient_to_database():
    if st.session_state.patient_saved and st.session_state.patient_id is not None:
        return st.session_state.patient_id
    db_patient = database_patient_data(st.session_state.patient)
    patient_id = save_patient(db_patient)
    st.session_state.patient_id = patient_id
    st.session_state.patient_saved = True
    return patient_id


def process_ocr(uploaded_file):
    st.session_state.ocr_error = ""
    if not OCR_AVAILABLE:
        st.session_state.ocr_error = "OCR module is not available in this project environment."
        return
    try:
        try:
            result = analyze_medical_document(
                uploaded_file,
                symptom_list_path=SYMPTOM_LIST_PATH,
            )
        except TypeError:
            result = analyze_medical_document(uploaded_file)
        result = result or {}
        st.session_state.ocr_uploaded_name = getattr(
            uploaded_file,
            "name",
            "Medical document",
        )
        st.session_state.ocr_extracted_text = str(result.get("text", ""))
        st.session_state.ocr_summary = str(result.get("summary", ""))
        st.session_state.ocr_symptoms = list(result.get("symptoms", []) or [])
        st.session_state.ocr_conditions = list(result.get("conditions", []) or [])
        st.session_state.ocr_medications = list(result.get("medications", []) or [])
        st.session_state.ocr_allergies = list(result.get("allergies", []) or [])
        st.session_state.ocr_findings = list(result.get("findings", []) or [])
        st.session_state.patient["ocr_summary"] = st.session_state.ocr_summary
        st.session_state.patient["ocr_symptoms"] = list(st.session_state.ocr_symptoms)
        st.session_state.patient["ocr_conditions"] = list(st.session_state.ocr_conditions)
        st.session_state.patient["ocr_medications"] = list(st.session_state.ocr_medications)
        st.session_state.patient["ocr_allergies"] = list(st.session_state.ocr_allergies)
        st.session_state.patient["ocr_findings"] = list(st.session_state.ocr_findings)
    except Exception as exc:
        st.session_state.ocr_error = f"Could not analyze the document: {exc}"


def use_voice_input():
    if not VOICE_AVAILABLE:
        st.session_state.voice_message = "Voice input is unavailable. You can continue using text input."
        return
    try:
        language_code = get_voice_language(st.session_state.language)
        recognized = speech_to_text(language=language_code)
        if is_successful(recognized):
            text = str(recognized).strip()
            if text:
                st.session_state.patient["complaint"] = text
                types = detect_problem_types(text)
                st.session_state.patient["problem_types"] = types
                st.session_state.patient["problem_type"] = types[0]
                st.session_state.voice_message = "Voice input captured successfully."
            else:
                st.session_state.voice_message = "No voice text was captured."
        else:
            st.session_state.voice_message = "Could not understand the voice input."
    except Exception as exc:
        st.session_state.voice_message = f"Voice input error: {exc}"


def render_prediction_table(predictions):
    if not predictions:
        st.info("No possible conditions could be generated from the available information.")
        return
    rows = [
        {
            "Condition": str(condition),
            "Probability (%)": round(float(probability) * 100, 2),
        }
        for condition, probability in predictions
    ]
    st.dataframe(
        pd.DataFrame(rows).astype(str),
        width="stretch",
        hide_index=True,
    )


def render_ocr_results():
    if st.session_state.ocr_error:
        st.error(st.session_state.ocr_error)
    if st.session_state.ocr_uploaded_name:
        st.success(f"Analyzed document: {st.session_state.ocr_uploaded_name}")
    if st.session_state.ocr_summary:
        st.markdown("### AI-assisted document summary")
        st.info(st.session_state.ocr_summary)
    if st.session_state.ocr_symptoms:
        st.markdown("### Extracted symptoms")
        st.write(", ".join(str(item) for item in st.session_state.ocr_symptoms))
    if st.session_state.ocr_conditions:
        st.markdown("### Extracted conditions")
        st.write(", ".join(str(item) for item in st.session_state.ocr_conditions))
    if st.session_state.ocr_medications:
        st.markdown("### Medication-related information")
        for item in st.session_state.ocr_medications:
            st.write(f"• {item}")
    if st.session_state.ocr_allergies:
        st.markdown("### Extracted allergies")
        st.write(", ".join(str(item) for item in st.session_state.ocr_allergies))
    if st.session_state.ocr_findings:
        st.markdown("### Extracted findings")
        for item in st.session_state.ocr_findings:
            st.write(f"• {item}")
    if st.session_state.ocr_extracted_text:
        with st.expander("View extracted text"):
            st.text(st.session_state.ocr_extracted_text)


def render_navigation(step, next_label="Next ➡️", next_disabled=False):
    left, right = st.columns(2)
    with left:
        if step > 1:
            if st.button("⬅️ Previous", key=f"previous_{step}", width="stretch"):
                go_back()
                st.rerun()
    with right:
        if step < TOTAL_STEPS:
            if st.button(next_label, key=f"next_{step}", width="stretch", disabled=next_disabled):
                go_next()
                st.rerun()


def assessment_table(assessment):
    rows = [
        ["Doctor", assessment.get("doctor_name", "")],
        ["Confirmed Condition", assessment.get("confirmed_condition", "Not provided")],
        ["Final Assessment", assessment.get("final_assessment", "")],
        ["Doctor Notes", assessment.get("doctor_notes", "")],
        ["Follow-up", assessment.get("follow_up", "")],
    ]
    return pd.DataFrame(rows, columns=["Field", "Information"]).astype(str)


st.markdown(
    """
    <style>
    .stApp { background: #f5f8fb; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3, h4, h5, p, label, .stMarkdown, .stCaption { color: #17324d !important; }
    .main-title { background: #ffffff; border: 1px solid #d9e4ee; border-radius: 18px; padding: 22px 28px; margin-bottom: 18px; }
    .main-title h1 { margin: 0; color: #123d63 !important; font-size: 2.35rem; }
    .main-title p { margin: 6px 0 0; color: #607d94 !important; font-size: 1.05rem; }
    .step-card { background: #ffffff; border: 1px solid #d9e4ee; border-radius: 16px; padding: 18px 22px; margin: 12px 0 20px; }
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stNumberInput"] input { background: #ffffff !important; color: #17324d !important; border: 1px solid #b9cbd9 !important; }
    div[data-testid="stSelectbox"] div, div[data-testid="stSelectSlider"] div, div[data-testid="stRadio"] label { color: #17324d !important; }
    div[data-testid="stFileUploader"] { background: #ffffff; border: 1px solid #d9e4ee; border-radius: 14px; padding: 8px; }
    div.stButton > button, div.stFormSubmitButton > button { border-radius: 10px; min-height: 42px; font-weight: 600; }
    div[data-testid="stDataFrame"] { border: 1px solid #d9e4ee; border-radius: 12px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title"><h1>🏥 ClinAssist</h1><p>AI-Powered Clinical History &amp; Decision Support System</p></div>',
    unsafe_allow_html=True,
)

step_names = [
    "Patient Information",
    "Presenting Complaint",
    "Basic Details",
    "Additional Questions",
    "Medical History",
    "Review",
    "AI Analysis",
    "Final Report",
]

with st.sidebar:
    st.markdown("### 🏥 ClinAssist")
    st.caption("AI-assisted clinical history and decision-support workflow")
    st.divider()
    for index, name in enumerate(step_names, start=1):
        if index == st.session_state.current_step:
            st.markdown(f"**● {index}. {name}**")
        else:
            st.write(f"○ {index}. {name}")
    st.divider()
    st.caption("For academic/project demonstration purposes.")

language_col1, language_col2 = st.columns([5, 1])
with language_col2:
    language_options = ["English", "Hindi"]
    current_language_index = 0 if st.session_state.language == "English" else 1
    selected_language = st.selectbox(
        "Language",
        language_options,
        index=current_language_index,
        key="language_selector",
    )
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()

st.info(
    "ClinAssist provides AI-assisted clinical decision support. AI-generated results are not a final diagnosis or prescription."
)
st.progress(st.session_state.current_step / TOTAL_STEPS)
st.caption(
    f"Step {st.session_state.current_step} of {TOTAL_STEPS} • {step_names[st.session_state.current_step - 1]}"
)

if st.session_state.current_step == 1:
    st.header("👤 Patient Information")
    st.markdown(
        '<div class="step-card"><strong>Patient Registration</strong><br>Enter the basic information required for the clinical history record.</div>',
        unsafe_allow_html=True,
    )

    patient = st.session_state.patient
    saved_name = str(patient.get("name", ""))
    saved_age = int(patient.get("age", 0) or 0)
    gender_options = ["Select", "Male", "Female", "Other"]
    saved_gender = patient.get("gender", "Select")
    gender_index = gender_options.index(saved_gender) if saved_gender in gender_options else 0

    name = st.text_input(
        "Patient Name",
        value=saved_name,
        placeholder="Enter patient's name",
    )
    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=saved_age,
        step=1,
    )
    gender = st.selectbox(
        "Gender",
        gender_options,
        index=gender_index,
    )

    st.divider()
    left, right = st.columns(2)
    with left:
        st.empty()
    with right:
        if st.button("Next ➡️", key="next_1", width="stretch"):
            if not name.strip():
                st.error("Please enter the patient name.")
            elif gender == "Select":
                st.error("Please select the gender.")
            else:
                st.session_state.patient.update(
                    {
                        "name": name.strip(),
                        "age": int(age),
                        "gender": gender,
                    }
                )
                go_next()
                st.rerun()

elif st.session_state.current_step == 2:
    st.header("🩺 Presenting Complaint")
    st.write("Describe the main problem or symptom.")

    patient = st.session_state.patient
    complaint = st.text_area(
        "What is the main problem or symptom?",
        value=str(patient.get("complaint", "")),
        placeholder="Example: headache, cough, stomach pain",
        height=130,
    )

    st.markdown("### 💡 Quick examples")
    example_cols = st.columns(4)
    examples = [
        ("🤕 Headache", "Headache"),
        ("😷 Cough", "Cough and fever"),
        ("🤢 Stomach Pain", "Stomach pain"),
        ("🌡️ General", "Fever and tiredness"),
    ]
    for column, (label, value) in zip(example_cols, examples):
        with column:
            if st.button(label, key=f"example_{value}", width="stretch"):
                st.session_state.patient["complaint"] = value
                types = detect_problem_types(value)
                st.session_state.patient["problem_types"] = types
                st.session_state.patient["problem_type"] = types[0]
                st.session_state.voice_message = ""
                st.rerun()

    if st.button("🎤 Use Voice Input", key="voice_input", width="stretch"):
        use_voice_input()
        st.rerun()

    if st.session_state.voice_message:
        st.caption(st.session_state.voice_message)

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Previous", key="previous_2", width="stretch"):
            go_back()
            st.rerun()
    with right:
        if st.button("Next ➡️", key="next_2", width="stretch"):
            text = complaint.strip()
            if not text:
                st.error("Please enter the main complaint.")
            else:
                types = detect_problem_types(text)
                st.session_state.patient["complaint"] = text
                st.session_state.patient["problem_types"] = types
                st.session_state.patient["problem_type"] = types[0]
                go_next()
                st.rerun()

elif st.session_state.current_step == 3:
    st.header("📋 Basic Details")
    patient = st.session_state.patient
    duration = st.text_input(
        "How long have you had this problem?",
        value=str(patient.get("duration", "")),
        placeholder="Example: 2 days",
    )
    severity_options = ["Mild", "Moderate", "Severe"]
    saved_severity = patient.get("severity", "Mild")
    severity_index = severity_options.index(saved_severity) if saved_severity in severity_options else 0
    severity = st.select_slider(
        "Severity",
        options=severity_options,
        value=severity_options[severity_index],
    )
    additional_symptoms = st.text_area(
        "Any additional symptoms?",
        value=str(patient.get("additional_symptoms", "")),
        placeholder="Example: nausea, tiredness, dizziness",
        height=120,
    )

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Previous", key="previous_3", width="stretch"):
            go_back()
            st.rerun()
    with right:
        if st.button("Next ➡️", key="next_3", width="stretch"):
            if not duration.strip():
                st.error("Please enter the duration.")
            else:
                st.session_state.patient.update(
                    {
                        "duration": duration.strip(),
                        "severity": severity,
                        "additional_symptoms": additional_symptoms.strip(),
                    }
                )
                go_next()
                st.rerun()

elif st.session_state.current_step == 4:
    st.header("🔎 Additional Questions")
    patient = st.session_state.patient
    problem_types = patient.get("problem_types") or detect_problem_types(get_patient_text(patient))
    values = {}

    if "head" in problem_types:
        st.subheader("🤕 Head-related questions")
        values["pain_location"] = st.text_input(
            "Where is the pain located?",
            value=str(patient.get("pain_location", "")),
            placeholder="Example: forehead, back of head, one side",
        )
        values["head_associated"] = st.text_area(
            "Do you have dizziness, nausea, vision problems, or sensitivity to light?",
            value=str(patient.get("head_associated", "")),
            height=90,
        )

    if "respiratory" in problem_types:
        st.subheader("😷 Respiratory questions")
        values["cough_type"] = st.text_input(
            "What type of cough do you have?",
            value=str(patient.get("cough_type", "")),
            placeholder="Example: dry cough / cough with phlegm",
        )
        values["breathing"] = st.text_input(
            "Do you experience breathing difficulty?",
            value=str(patient.get("breathing", "")),
        )

    if "digestive" in problem_types:
        st.subheader("🤢 Digestive questions")
        values["food_relation"] = st.text_input(
            "Does it occur after eating?",
            value=str(patient.get("food_relation", "")),
        )
        values["vomiting"] = st.text_input(
            "Any vomiting or nausea?",
            value=str(patient.get("vomiting", "")),
        )

    if "skin" in problem_types:
        st.subheader("🩹 Skin-related questions")
        values["skin_appearance"] = st.text_input(
            "Describe the skin problem.",
            value=str(patient.get("skin_appearance", "")),
            placeholder="Example: red spots, itching, rash",
        )
        values["skin_duration"] = st.text_input(
            "How long has the skin problem been present?",
            value=str(patient.get("skin_duration", "")),
        )

    if problem_types == ["general"]:
        st.subheader("📝 General questions")
        values["additional_details"] = st.text_area(
            "Please provide any other relevant details.",
            value=str(patient.get("additional_details", "")),
            height=120,
        )

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Previous", key="previous_4", width="stretch"):
            go_back()
            st.rerun()
    with right:
        if st.button("Next ➡️", key="next_4", width="stretch"):
            cleaned_values = {}
            for key, value in values.items():
                cleaned_values[key] = value.strip() if isinstance(value, str) else value
            st.session_state.patient.update(cleaned_values)
            go_next()
            st.rerun()

elif st.session_state.current_step == 5:
    st.header("📚 Medical History")
    patient = st.session_state.patient

    past_history = st.text_area(
        "Past medical history",
        value=str(patient.get("past_history", "")),
        placeholder="Example: previous illnesses or surgeries",
        height=100,
    )
    medications = st.text_area(
        "Current medications",
        value=str(patient.get("medications", "")),
        placeholder="List current medications if any",
        height=100,
    )
    allergies = st.text_area(
        "Drug or other allergies",
        value=str(patient.get("allergies", "")),
        placeholder="Mention known allergies if any",
        height=100,
    )
    family_history = st.text_area(
        "Family medical history",
        value=str(patient.get("family_history", "")),
        height=100,
    )
    personal_history = st.text_area(
        "Relevant personal history",
        value=str(patient.get("personal_history", "")),
        height=100,
    )

    st.divider()
    st.subheader("📄 Previous Medical Record — OCR Analysis")
    st.write("Upload a previous medical report, prescription, or other relevant medical document.")
    uploaded_file = st.file_uploader(
        "Choose a medical document",
        type=["pdf", "png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        if st.button("🔍 Analyze Medical Document", key="analyze_ocr", width="stretch"):
            st.session_state.patient.update(
                {
                    "past_history": past_history.strip(),
                    "medications": medications.strip(),
                    "allergies": allergies.strip(),
                    "family_history": family_history.strip(),
                    "personal_history": personal_history.strip(),
                }
            )
            process_ocr(uploaded_file)
            st.rerun()

    render_ocr_results()

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Previous", key="previous_5", width="stretch"):
            st.session_state.patient.update(
                {
                    "past_history": past_history.strip(),
                    "medications": medications.strip(),
                    "allergies": allergies.strip(),
                    "family_history": family_history.strip(),
                    "personal_history": personal_history.strip(),
                }
            )
            go_back()
            st.rerun()
    with right:
        if st.button("Next ➡️", key="next_5", width="stretch"):
            st.session_state.patient.update(
                {
                    "past_history": past_history.strip(),
                    "medications": medications.strip(),
                    "allergies": allergies.strip(),
                    "family_history": family_history.strip(),
                    "personal_history": personal_history.strip(),
                }
            )
            go_next()
            st.rerun()

elif st.session_state.current_step == 6:
    st.header("📄 Review Information")
    patient = st.session_state.patient

    review_data = {
        "Patient Name": patient.get("name", ""),
        "Age": patient.get("age", ""),
        "Gender": patient.get("gender", ""),
        "Main Complaint": patient.get("complaint", ""),
        "Duration": patient.get("duration", ""),
        "Severity": patient.get("severity", ""),
        "Problem Areas": ", ".join(problem_label(item) for item in patient.get("problem_types", [])),
        "Additional Symptoms": patient.get("additional_symptoms", ""),
        "Past Medical History": patient.get("past_history", ""),
        "Medications": patient.get("medications", ""),
        "Allergies": patient.get("allergies", ""),
        "Family History": patient.get("family_history", ""),
        "Personal History": patient.get("personal_history", ""),
        "OCR Document": st.session_state.ocr_uploaded_name,
        "OCR Summary": st.session_state.ocr_summary,
    }

    review_df = pd.DataFrame(
        list(review_data.items()),
        columns=["Field", "Information"],
    ).astype(str)
    st.dataframe(review_df, width="stretch", hide_index=True)

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Previous", key="previous_6", width="stretch"):
            go_back()
            st.rerun()
    with right:
        if st.button("Continue to AI Analysis ➡️", key="next_6", width="stretch"):
            try:
                save_patient_to_database()
                go_next()
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save patient record: {exc}")

elif st.session_state.current_step == 7:
    st.header("🤖 AI Decision Support")
    patient = st.session_state.patient

    if not st.session_state.patient_saved:
        st.warning("Please complete the previous steps first.")
    else:
        patient_text = get_patient_text(patient)

        st.subheader("🔎 Detected Symptoms")
        detected_symptoms = patient.get("detected_symptoms", [])
        predictions = patient.get("predictions", [])

        try:
            if patient_text.strip():
                detected_symptoms, predictions = run_ml_decision_support(patient_text)
                st.session_state.patient["detected_symptoms"] = list(detected_symptoms)
                st.session_state.patient["predictions"] = list(predictions)
        except Exception as exc:
            st.error(f"AI analysis error: {exc}")

        if detected_symptoms:
            readable = [str(item).replace("_", " ").title() for item in detected_symptoms]
            st.success(", ".join(readable))
        else:
            st.info("No matching symptoms were detected from the provided information.")

        st.subheader("🧠 Possible Conditions to Consider")
        render_prediction_table(predictions)

        flags = urgency_flags(patient_text)
        st.session_state.patient["urgency_flags"] = flags

        st.divider()
        st.subheader("🚨 Urgency Review")
        if flags:
            for flag in flags:
                st.error(f"⚠️ {flag}")
        else:
            st.success("No predefined urgency flags were detected.")

        st.divider()
        st.subheader("👨‍⚕️ Doctor Assessment")
        st.info("The AI output is decision-support only. The doctor makes the final clinical assessment.")

        try:
            existing_assessment = (
                get_doctor_assessment(st.session_state.patient_id)
                if st.session_state.patient_id
                else None
            )
        except Exception:
            existing_assessment = None

        if existing_assessment:
            st.success("Doctor assessment has already been saved.")
            st.dataframe(
                assessment_table(existing_assessment),
                width="stretch",
                hide_index=True,
            )
        else:
            with st.form("doctor_assessment_form"):
                doctor_name = st.text_input("Doctor Name")
                confirmed_condition = st.text_input("Doctor-Confirmed Condition")
                final_assessment = st.text_area("Final Clinical Assessment", height=110)
                doctor_notes = st.text_area("Doctor Notes", height=110)
                follow_up = st.text_area("Follow-up / Recommendations", height=110)
                save_assessment = st.form_submit_button(
                    "💾 Save Doctor Assessment",
                    width="stretch",
                )

            if save_assessment:
                if not doctor_name.strip():
                    st.error("Please enter the doctor's name.")
                elif not final_assessment.strip():
                    st.error("Please enter the final clinical assessment.")
                else:
                    assessment = {
                        "doctor_name": doctor_name.strip(),
                        "confirmed_condition": confirmed_condition.strip() or None,
                        "final_assessment": final_assessment.strip(),
                        "doctor_notes": doctor_notes.strip(),
                        "follow_up": follow_up.strip(),
                    }
                    try:
                        save_doctor_assessment(
                            st.session_state.patient_id,
                            assessment,
                        )
                        st.success("Doctor assessment saved successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not save doctor assessment: {exc}")

        st.divider()
        left, right = st.columns(2)
        with left:
            if st.button("⬅️ Previous", key="previous_7", width="stretch"):
                go_back()
                st.rerun()
        with right:
            if st.button("Next ➡️", key="next_7", width="stretch"):
                go_next()
                st.rerun()

elif st.session_state.current_step == 8:
    st.header("📄 Final Clinical Report")
    patient = st.session_state.patient

    st.subheader("👤 Patient Information")
    patient_info = pd.DataFrame(
        [
            {
                "Name": patient.get("name", ""),
                "Age": patient.get("age", ""),
                "Gender": patient.get("gender", ""),
                "Patient ID": st.session_state.patient_id,
            }
        ]
    ).astype(str)
    st.dataframe(patient_info, width="stretch", hide_index=True)

    st.subheader("🩺 Clinical History")
    history_data = [
        ["Main Complaint", patient.get("complaint", "")],
        ["Duration", patient.get("duration", "")],
        ["Severity", patient.get("severity", "")],
        ["Problem Areas", ", ".join(problem_label(item) for item in patient.get("problem_types", []))],
        ["Additional Symptoms", patient.get("additional_symptoms", "")],
        ["Past Medical History", patient.get("past_history", "")],
        ["Medications", patient.get("medications", "")],
        ["Allergies", patient.get("allergies", "")],
        ["Family History", patient.get("family_history", "")],
        ["Personal History", patient.get("personal_history", "")],
    ]

    adaptive_fields = [
        ("Pain Location", "pain_location"),
        ("Head-associated Symptoms", "head_associated"),
        ("Cough Type", "cough_type"),
        ("Breathing Difficulty", "breathing"),
        ("Food Relation", "food_relation"),
        ("Vomiting/Nausea", "vomiting"),
        ("Skin Appearance", "skin_appearance"),
        ("Skin Duration", "skin_duration"),
        ("Additional Details", "additional_details"),
    ]
    for label, field in adaptive_fields:
        value = patient.get(field, "")
        if value is not None and str(value).strip():
            history_data.append([label, value])

    history_df = pd.DataFrame(
        history_data,
        columns=["Field", "Information"],
    ).astype(str)
    st.dataframe(history_df, width="stretch", hide_index=True)

    if st.session_state.ocr_uploaded_name:
        st.subheader("📄 OCR Medical Record")
        ocr_df = pd.DataFrame(
            [
                ["Document", st.session_state.ocr_uploaded_name],
                ["Summary", st.session_state.ocr_summary],
                ["Symptoms", ", ".join(str(item) for item in st.session_state.ocr_symptoms)],
                ["Conditions", ", ".join(str(item) for item in st.session_state.ocr_conditions)],
                ["Medication-related information", "; ".join(str(item) for item in st.session_state.ocr_medications)],
                ["Allergies", ", ".join(str(item) for item in st.session_state.ocr_allergies)],
                ["Findings", "; ".join(str(item) for item in st.session_state.ocr_findings)],
            ],
            columns=["Field", "Information"],
        ).astype(str)
        st.dataframe(ocr_df, width="stretch", hide_index=True)

    st.subheader("🤖 AI Analysis")
    detected_symptoms = patient.get("detected_symptoms", [])
    predictions = patient.get("predictions", [])
    if detected_symptoms:
        st.write(
            "**Detected Symptoms:**",
            ", ".join(str(item).replace("_", " ").title() for item in detected_symptoms),
        )
    render_prediction_table(predictions)

    st.subheader("🚨 Urgency Review")
    saved_flags = patient.get("urgency_flags", [])
    if saved_flags:
        for flag in saved_flags:
            st.error(f"⚠️ {flag}")
    else:
        st.success("No predefined urgency flags were detected.")

    st.subheader("👨‍⚕️ Doctor Assessment")
    try:
        assessment = (
            get_doctor_assessment(st.session_state.patient_id)
            if st.session_state.patient_id
            else None
        )
    except Exception:
        assessment = None

    if assessment:
        st.dataframe(
            assessment_table(assessment),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No doctor assessment has been added yet.")

    st.warning(
        "This report is generated by an AI-assisted decision-support prototype. AI-generated outputs must not be treated as a final diagnosis or prescription. Final clinical decisions remain the responsibility of a qualified healthcare professional."
    )

    st.divider()
    st.subheader("📥 Generate PDF Report")

    if st.button("📄 Generate PDF Report", key="generate_pdf", width="stretch"):
        try:
            patient_snapshot = dict(patient)
            if st.session_state.patient_id is not None:
                patient_snapshot["id"] = st.session_state.patient_id

            analysis = {
                "detected_symptoms": list(detected_symptoms),
                "symptoms": list(detected_symptoms),
                "predictions": list(predictions),
                "possible_conditions": list(predictions),
                "urgency_flags": list(saved_flags),
                "urgency": {
                    "urgent": bool(saved_flags),
                    "flags": list(saved_flags),
                    "matched_phrases": [],
                    "message": (
                        "Potential urgency indicators were detected."
                        if saved_flags
                        else "No predefined urgency indicators were detected."
                    ),
                },
            }

            report = create_clinical_report(
                patient_snapshot,
                analysis,
                assessment,
            )

            output_directory = BASE_DIR / "reports" / "output"
            output_directory.mkdir(parents=True, exist_ok=True)
            patient_number = st.session_state.patient_id or "draft"
            pdf_path = output_directory / f"clinassist_patient_{patient_number}.pdf"
            export_report_to_pdf(report, pdf_path)
            st.session_state.pdf_path = str(pdf_path)
            st.success("PDF report generated successfully.")
        except Exception as exc:
            st.error(f"Could not generate PDF report: {exc}")

    if st.session_state.pdf_path:
        pdf_file = Path(st.session_state.pdf_path)
        if pdf_file.exists():
            with open(pdf_file, "rb") as file:
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=file,
                    file_name=pdf_file.name,
                    mime="application/pdf",
                    width="stretch",
                )

    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("⬅️ Previous", key="previous_8", width="stretch"):
            go_back()
            st.rerun()
    with right:
        if st.button("🔄 Start New Patient", key="new_patient", width="stretch"):
            reset_application()
            st.rerun()

st.divider()
st.caption("ClinAssist | AI-Assisted Clinical History & Decision Support System")
st.caption("For academic/project demonstration purposes. AI outputs are not a substitute for professional medical judgment.")
