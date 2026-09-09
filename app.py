import streamlit as st
import pandas as pd
import joblib
import re
from pathlib import Path

from database.database import (
    initialize_database,
    save_patient,
    get_doctor_assessment,
)

from reports.pdf_report import export_report_to_pdf

from voice.speech_to_text import (
    speech_to_text,
    is_successful,
    get_voice_language,
)

from language.translations import get_translation


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ClinAssist",
    page_icon="🩺",
    layout="wide",
)


# ============================================================
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# CONSTANTS
# ============================================================

TOTAL_STEPS = 8

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "clinassist_model.pkl"
ENCODER_PATH = BASE_DIR / "disease_encoder.pkl"
SYMPTOM_PATH = BASE_DIR / "symptom_list.pkl"


# ============================================================
# SESSION STATE
# ============================================================

if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "patient" not in st.session_state:
    st.session_state.patient = {}

if "complaint_box" not in st.session_state:
    st.session_state.complaint_box = ""

if "patient_saved" not in st.session_state:
    st.session_state.patient_saved = False

if "patient_id" not in st.session_state:
    st.session_state.patient_id = None

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

if "voice_message" not in st.session_state:
    st.session_state.voice_message = ""

if "language" not in st.session_state:
    st.session_state.language = "English"


# ============================================================
# TRANSLATION HELPER
# ============================================================

def t(key):
    return get_translation(
        st.session_state.language,
        key,
    )


# ============================================================
# NAVIGATION FUNCTIONS
# ============================================================

def go_next():

    if st.session_state.current_step < TOTAL_STEPS:
        st.session_state.current_step += 1


def go_previous():

    if st.session_state.current_step > 1:
        st.session_state.current_step -= 1


def reset_app():

    language = st.session_state.get(
        "language",
        "English",
    )

    st.session_state.clear()

    st.session_state.current_step = 1
    st.session_state.patient = {}
    st.session_state.complaint_box = ""
    st.session_state.patient_saved = False
    st.session_state.patient_id = None
    st.session_state.pdf_path = None
    st.session_state.voice_message = ""
    st.session_state.language = language


# ============================================================
# COMPLAINT EXAMPLES
# ============================================================

def set_complaint(example):

    st.session_state.complaint_box = example


# ============================================================
# VOICE INPUT
# ============================================================

def use_voice_input():

    voice_language = get_voice_language(
        st.session_state.language
    )

    text = speech_to_text(
        language=voice_language
    )

    if is_successful(text):

        st.session_state.complaint_box = text

        if st.session_state.language == "English":

            st.session_state.voice_message = (
                "Voice input captured successfully."
            )

        else:

            st.session_state.voice_message = (
                "वॉइस इनपुट सफलतापूर्वक दर्ज किया गया।"
            )

    else:

        st.session_state.voice_message = text


# ============================================================
# PROBLEM TYPE DETECTION
# ============================================================

def detect_problem_type(complaint):

    text = complaint.lower()

    # HEAD
    if any(
        word in text
        for word in [
            "headache",
            "head pain",
            "migraine",
            "dizziness",
            "vertigo",
            "head",
        ]
    ):
        return "head"

    # RESPIRATORY
    if any(
        word in text
        for word in [
            "cough",
            "breathing",
            "breath",
            "cold",
            "throat",
            "chest",
        ]
    ):
        return "respiratory"

    # DIGESTIVE
    if any(
        word in text
        for word in [
            "stomach",
            "abdomen",
            "abdominal",
            "vomit",
            "nausea",
            "diarrhea",
            "loose motion",
            "gas",
        ]
    ):
        return "digestive"

    # SKIN
    if any(
        word in text
        for word in [
            "skin",
            "rash",
            "itch",
            "redness",
            "pimple",
        ]
    ):
        return "skin"

    return "general"


# ============================================================
# MACHINE LEARNING
# ============================================================

@st.cache_resource
def load_ml_model():

    if not (
        MODEL_PATH.exists()
        and ENCODER_PATH.exists()
        and SYMPTOM_PATH.exists()
    ):

        return None, None, None

    model = joblib.load(
        MODEL_PATH
    )

    encoder = joblib.load(
        ENCODER_PATH
    )

    symptom_list = joblib.load(
        SYMPTOM_PATH
    )

    return model, encoder, symptom_list


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):

    text = str(text).lower()

    text = text.replace(
        "_",
        " ",
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# PATIENT TEXT
# ============================================================

def get_patient_text(patient):

    parts = [

        patient.get(
            "complaint",
            "",
        ),

        patient.get(
            "duration",
            "",
        ),

        patient.get(
            "severity",
            "",
        ),

        patient.get(
            "additional_symptoms",
            "",
        ),

        patient.get(
            "past_history",
            "",
        ),

        patient.get(
            "medications",
            "",
        ),

        patient.get(
            "allergies",
            "",
        ),
    ]

    return " ".join(
        str(part)
        for part in parts
        if part
    )


# ============================================================
# SYMPTOM MATCHING
# ============================================================

def match_symptoms(
    text,
    symptom_list,
):

    normalized_text = normalize_text(
        text
    )

    matched = []

    for symptom in symptom_list:

        readable = normalize_text(
            symptom
        )

        if not readable:
            continue

        if readable in normalized_text:

            matched.append(
                symptom
            )

    return matched


# ============================================================
# ML DECISION SUPPORT
# ============================================================

def run_ml_decision_support(patient):

    model, encoder, symptom_list = (
        load_ml_model()
    )

    if model is None:

        return {
            "symptoms": [],
            "predictions": [],
            "message": (
                "ML model files were not found."
            ),
        }

    patient_text = get_patient_text(
        patient
    )

    matched_symptoms = match_symptoms(
        patient_text,
        symptom_list,
    )

    feature_vector = [

        1 if symptom in matched_symptoms
        else 0

        for symptom in symptom_list
    ]

    feature_df = pd.DataFrame(
        [feature_vector],
        columns=symptom_list,
    )

    probabilities = (
        model.predict_proba(
            feature_df
        )[0]
    )

    top_indices = (
        probabilities
        .argsort()[-3:][::-1]
    )

    predictions = []

    for index in top_indices:

        condition = (
            encoder
            .inverse_transform(
                [index]
            )[0]
        )

        score = (
            float(
                probabilities[index]
            ) * 100
        )

        predictions.append(
            {
                "condition": condition,
                "score": score,
            }
        )

    return {
        "symptoms": matched_symptoms,
        "predictions": predictions,
        "message": "Analysis completed.",
    }


# ============================================================
# URGENCY FLAGS
# ============================================================

def urgency_flags(text):

    normalized = normalize_text(
        text
    )

    flags = []

    red_flags = {

        "Severe breathing difficulty": [

            "severe difficulty breathing",
            "severe trouble breathing",
            "cannot breathe",
            "can't breathe",
            "unable to breathe",
            "extreme breathlessness",
        ],

        "Severe chest discomfort": [

            "severe chest pain",
            "severe chest discomfort",
            "crushing chest pain",
            "pressure in chest",
            "heavy pressure in chest",
        ],

        "Loss of consciousness": [

            "lost consciousness",
            "loss of consciousness",
            "passed out",
            "fainted",
            "unconscious",
        ],

        "Sudden neurological symptoms": [

            "sudden weakness",
            "sudden numbness",
            "sudden confusion",
            "difficulty speaking",
            "unable to speak",
            "sudden vision loss",
            "sudden severe headache",
        ],

        "Severe bleeding": [

            "severe bleeding",
            "heavy bleeding",
            "bleeding heavily",
            "uncontrolled bleeding",
        ],

        "Severe allergic reaction indicators": [

            "swelling of face",
            "swelling of throat",
            "throat swelling",
            "difficulty swallowing",
            "difficulty breathing after eating",
        ],
    }

    for category, phrases in red_flags.items():

        for phrase in phrases:

            if phrase in normalized:

                flags.append(
                    category
                )

                break

    return {
        "urgent": len(flags) > 0,
        "flags": flags,
    }


# ============================================================
# SAVE PATIENT
# ============================================================

def save_current_patient():

    if st.session_state.patient_saved:

        return st.session_state.patient_id

    patient = (
        st.session_state.patient
    )

    patient_id = save_patient(
        patient
    )

    st.session_state.patient_saved = True

    st.session_state.patient_id = (
        patient_id
    )

    return patient_id


# ============================================================
# LANGUAGE SELECTOR
# ============================================================

language_col1, language_col2 = st.columns(
    [5, 1]
)

with language_col2:

    selected_language = st.selectbox(
        "Language",
        [
            "English",
            "Hindi",
        ],
        index=[
            "English",
            "Hindi",
        ].index(
            st.session_state.language
        ),
    )

    if selected_language != st.session_state.language:

        st.session_state.language = (
            selected_language
        )

        st.rerun()


# ============================================================
# HEADER
# ============================================================

with language_col1:

    st.title(
        f"🩺 {t('app_title')}"
    )

    st.subheader(
        t("subtitle")
    )


if st.session_state.language == "English":

    st.info(
        "ClinAssist is a decision-support prototype. "
        "Final diagnosis and treatment decisions must be made "
        "by a qualified doctor."
    )

else:

    st.info(
        "ClinAssist एक निर्णय-सहायता प्रोटोटाइप है। "
        "अंतिम निदान और उपचार संबंधी निर्णय योग्य डॉक्टर द्वारा "
        "लिए जाने चाहिए।"
    )


st.divider()


# ============================================================
# PROGRESS
# ============================================================

st.progress(
    st.session_state.current_step
    / TOTAL_STEPS
)

st.caption(
    (
        f"Step {st.session_state.current_step} "
        f"of {TOTAL_STEPS}"
    )
    if st.session_state.language == "English"
    else
    (
        f"चरण {st.session_state.current_step} "
        f"/ {TOTAL_STEPS}"
    )
)


# ============================================================
# STEP 1 — PATIENT INFORMATION
# ============================================================

if st.session_state.current_step == 1:

    st.header(
        f"👤 {t('patient_information')}"
    )

    col1, col2 = st.columns(2)

    with col1:

        name = st.text_input(
            t("name"),
            value=st.session_state.patient.get(
                "name",
                "",
            ),
            placeholder=(
                "Enter patient name"
                if st.session_state.language == "English"
                else "रोगी का नाम दर्ज करें"
            ),
        )

        age = st.number_input(
            t("age"),
            min_value=0,
            max_value=120,
            value=int(
                st.session_state.patient.get(
                    "age",
                    20,
                )
            ),
        )

    with col2:

        gender_values = [
            "Male",
            "Female",
            "Other",
        ]

        gender_labels = [
            t("male"),
            t("female"),
            t("other"),
        ]

        saved_gender = (
            st.session_state.patient.get(
                "gender",
                "Male",
            )
        )

        if saved_gender in gender_values:

            gender_index = (
                gender_values.index(
                    saved_gender
                )
            )

        else:

            gender_index = 0

        selected_gender_label = (
            st.selectbox(
                t("gender"),
                gender_labels,
                index=gender_index,
            )
        )

        selected_gender = gender_values[
            gender_labels.index(
                selected_gender_label
            )
        ]

    st.divider()

    col1, col2 = st.columns(2)

    with col2:

        if st.button(
            f"{t('next')} ➡️",
            width="stretch",
        ):

            if not name.strip():

                st.warning(
                    "Please enter the patient's name."
                    if st.session_state.language == "English"
                    else "कृपया रोगी का नाम दर्ज करें।"
                )

            else:

                st.session_state.patient.update(
                    {
                        "name": name.strip(),
                        "age": age,
                        "gender": selected_gender,
                    }
                )

                go_next()

                st.rerun()


# ============================================================
# STEP 2 — PRESENTING COMPLAINT
# ============================================================

elif st.session_state.current_step == 2:

    st.header(
        f"📝 {t('presenting_complaint')}"
    )

    # --------------------------------------------------------
    # VOICE INFORMATION
    # --------------------------------------------------------

    if st.session_state.language == "English":

        st.info(
            "🎙️ You can type the complaint or use voice input."
        )

    else:

        st.info(
            "🎙️ आप शिकायत टाइप कर सकते हैं या वॉइस इनपुट का उपयोग कर सकते हैं।"
        )

    # --------------------------------------------------------
    # SPEAK BUTTON
    # --------------------------------------------------------

    if st.button(
        "🎙️ Speak",
        width="stretch",
    ):

        with st.spinner(
            "Listening..."
            if st.session_state.language == "English"
            else "सुन रहा है..."
        ):

            use_voice_input()

        st.rerun()

    # --------------------------------------------------------
    # VOICE MESSAGE
    # --------------------------------------------------------

    if st.session_state.voice_message:

        st.success(
            st.session_state.voice_message
        )

    # --------------------------------------------------------
    # COMPLAINT TEXT
    # --------------------------------------------------------

    complaint = st.text_input(
        t("main_problem"),
        placeholder=(
            "Example: headache"
            if st.session_state.language == "English"
            else "उदाहरण: सिरदर्द"
        ),
        key="complaint_box",
    )

    # --------------------------------------------------------
    # QUICK EXAMPLES
    # --------------------------------------------------------

    st.write(
        "Quick examples:"
        if st.session_state.language == "English"
        else "त्वरित उदाहरण:"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.button(
            "🤕 Headache",
            width="stretch",
            on_click=set_complaint,
            args=("Headache",),
        )

    with col2:

        st.button(
            "😷 Cough",
            width="stretch",
            on_click=set_complaint,
            args=("Cough",),
        )

    with col3:

        st.button(
            "🤢 Stomach Pain",
            width="stretch",
            on_click=set_complaint,
            args=("Stomach pain",),
        )

    with col4:

        st.button(
            "🤒 Fever",
            width="stretch",
            on_click=set_complaint,
            args=("Fever",),
        )

    st.divider()

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(
            f"{t('next')} →",
            width="stretch",
        ):

            if not complaint.strip():

                st.warning(
                    "Please enter the main complaint."
                    if st.session_state.language == "English"
                    else "कृपया मुख्य शिकायत दर्ज करें।"
                )

            else:

                problem_type = (
                    detect_problem_type(
                        complaint
                    )
                )

                st.session_state.patient.update(
                    {
                        "complaint":
                            complaint.strip(),

                        "problem_type":
                            problem_type,
                    }
                )

                st.session_state.voice_message = ""

                go_next()

                st.rerun()


# ============================================================
# STEP 3 — BASIC DETAILS
# ============================================================

elif st.session_state.current_step == 3:

    st.header(
        f"📋 {t('basic_details')}"
    )

    patient = (
        st.session_state.patient
    )

    duration = st.text_input(
        t("duration"),
        value=patient.get(
            "duration",
            "",
        ),
        placeholder=(
            "Example: 2 days"
            if st.session_state.language == "English"
            else "उदाहरण: 2 दिन"
        ),
    )

    severity_values = [
        "Mild",
        "Moderate",
        "Severe",
    ]

    severity_labels = [
        t("mild"),
        t("moderate"),
        t("severe"),
    ]

    saved_severity = patient.get(
        "severity",
        "Moderate",
    )

    severity_index = (
        severity_values.index(
            saved_severity
        )
        if saved_severity in severity_values
        else 1
    )

    severity_label = st.selectbox(
        t("severity"),
        severity_labels,
        index=severity_index,
    )

    severity = severity_values[
        severity_labels.index(
            severity_label
        )
    ]

    additional_symptoms = st.text_area(
        t("additional_symptoms"),
        value=patient.get(
            "additional_symptoms",
            "",
        ),
        placeholder=(
            "Example: nausea, weakness, dizziness"
            if st.session_state.language == "English"
            else "उदाहरण: मतली, कमजोरी, चक्कर"
        ),
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(
            f"{t('next')} →",
            width="stretch",
        ):

            st.session_state.patient.update(
                {
                    "duration":
                        duration,

                    "severity":
                        severity,

                    "additional_symptoms":
                        additional_symptoms,
                }
            )

            go_next()

            st.rerun()


# ============================================================
# STEP 4 — ADAPTIVE QUESTIONS
# ============================================================

elif st.session_state.current_step == 4:

    st.header(
        "🧠 Adaptive Clinical Questions"
        if st.session_state.language == "English"
        else "🧠 अनुकूलित क्लिनिकल प्रश्न"
    )

    patient = (
        st.session_state.patient
    )

    problem_type = patient.get(
        "problem_type",
        "general",
    )

    st.info(
        "Questions are adapted according to the reported complaint."
        if st.session_state.language == "English"
        else "प्रश्न बताई गई शिकायत के अनुसार अनुकूलित किए गए हैं।"
    )

    # --------------------------------------------------------
    # HEAD
    # --------------------------------------------------------

    if problem_type == "head":

        dizziness = st.selectbox(
            "Are you experiencing dizziness?"
            if st.session_state.language == "English"
            else "क्या आपको चक्कर आ रहे हैं?",
            [
                "No",
                "Yes",
            ],
        )

        vision = st.selectbox(
            "Are you experiencing any vision changes?"
            if st.session_state.language == "English"
            else "क्या आपकी दृष्टि में कोई बदलाव आया है?",
            [
                "No",
                "Yes",
            ],
        )

        nausea = st.selectbox(
            "Are you experiencing nausea or vomiting?"
            if st.session_state.language == "English"
            else "क्या आपको मतली या उल्टी हो रही है?",
            [
                "No",
                "Yes",
            ],
        )

        patient.update(
            {
                "dizziness":
                    dizziness,

                "vision_changes":
                    vision,

                "nausea":
                    nausea,
            }
        )

    # --------------------------------------------------------
    # RESPIRATORY
    # --------------------------------------------------------

    elif problem_type == "respiratory":

        breathing = st.selectbox(
            "Are you having difficulty breathing?"
            if st.session_state.language == "English"
            else "क्या आपको सांस लेने में कठिनाई हो रही है?",
            [
                "No",
                "Yes",
            ],
        )

        phlegm = st.selectbox(
            "Are you experiencing phlegm?"
            if st.session_state.language == "English"
            else "क्या आपको बलगम हो रहा है?",
            [
                "No",
                "Yes",
            ],
        )

        chest = st.selectbox(
            "Are you experiencing chest discomfort?"
            if st.session_state.language == "English"
            else "क्या आपको सीने में असुविधा हो रही है?",
            [
                "No",
                "Yes",
            ],
        )

        patient.update(
            {
                "breathing_difficulty":
                    breathing,

                "phlegm":
                    phlegm,

                "chest_discomfort":
                    chest,
            }
        )

    # --------------------------------------------------------
    # DIGESTIVE
    # --------------------------------------------------------

    elif problem_type == "digestive":

        vomiting = st.selectbox(
            "Are you experiencing vomiting?"
            if st.session_state.language == "English"
            else "क्या आपको उल्टी हो रही है?",
            [
                "No",
                "Yes",
            ],
        )

        appetite = st.selectbox(
            "Has your appetite changed?"
            if st.session_state.language == "English"
            else "क्या आपकी भूख में बदलाव आया है?",
            [
                "No",
                "Yes",
            ],
        )

        diarrhea = st.selectbox(
            "Are you experiencing diarrhea or loose motions?"
            if st.session_state.language == "English"
            else "क्या आपको दस्त या पतले मल की समस्या है?",
            [
                "No",
                "Yes",
            ],
        )

        patient.update(
            {
                "vomiting":
                    vomiting,

                "appetite_change":
                    appetite,

                "diarrhea":
                    diarrhea,
            }
        )

    # --------------------------------------------------------
    # SKIN
    # --------------------------------------------------------

    elif problem_type == "skin":

        itching = st.selectbox(
            "Is the affected area itchy?"
            if st.session_state.language == "English"
            else "क्या प्रभावित स्थान पर खुजली हो रही है?",
            [
                "No",
                "Yes",
            ],
        )

        rash = st.selectbox(
            "Is there a visible rash?"
            if st.session_state.language == "English"
            else "क्या त्वचा पर दाने दिखाई दे रहे हैं?",
            [
                "No",
                "Yes",
            ],
        )

        redness = st.selectbox(
            "Is there redness?"
            if st.session_state.language == "English"
            else "क्या त्वचा पर लालिमा है?",
            [
                "No",
                "Yes",
            ],
        )

        patient.update(
            {
                "itching":
                    itching,

                "rash":
                    rash,

                "redness":
                    redness,
            }
        )

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    else:

        weakness = st.selectbox(
            "Are you experiencing weakness or tiredness?"
            if st.session_state.language == "English"
            else "क्या आपको कमजोरी या थकान महसूस हो रही है?",
            [
                "No",
                "Yes",
            ],
        )

        appetite = st.selectbox(
            "Has your appetite changed?"
            if st.session_state.language == "English"
            else "क्या आपकी भूख में बदलाव आया है?",
            [
                "No",
                "Yes",
            ],
        )

        sleep = st.selectbox(
            "Has your sleep been affected?"
            if st.session_state.language == "English"
            else "क्या आपकी नींद प्रभावित हुई है?",
            [
                "No",
                "Yes",
            ],
        )

        patient.update(
            {
                "weakness":
                    weakness,

                "appetite_change":
                    appetite,

                "sleep_change":
                    sleep,
            }
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(
            f"{t('next')} →",
            width="stretch",
        ):

            go_next()

            st.rerun()


# ============================================================
# STEP 5 — MEDICAL HISTORY
# ============================================================

elif st.session_state.current_step == 5:

    st.header(
        f"🏥 {t('medical_history')}"
    )

    patient = (
        st.session_state.patient
    )

    past_history = st.text_area(
        t("past_history"),
        value=patient.get(
            "past_history",
            "",
        ),
        placeholder=(
            "Example: No major previous illness"
            if st.session_state.language == "English"
            else "उदाहरण: कोई प्रमुख पिछली बीमारी नहीं"
        ),
    )

    medications = st.text_area(
        t("medications"),
        value=patient.get(
            "medications",
            "",
        ),
        placeholder=(
            "Enter current medications if known"
            if st.session_state.language == "English"
            else "यदि ज्ञात हो तो वर्तमान दवाएँ दर्ज करें"
        ),
    )

    allergies = st.text_area(
        t("allergies"),
        value=patient.get(
            "allergies",
            "",
        ),
        placeholder=(
            "Example: No known allergies"
            if st.session_state.language == "English"
            else "उदाहरण: कोई ज्ञात एलर्जी नहीं"
        ),
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(
            f"{t('next')} →",
            width="stretch",
        ):

            st.session_state.patient.update(
                {
                    "past_history":
                        past_history,

                    "medications":
                        medications,

                    "allergies":
                        allergies,
                }
            )

            go_next()

            st.rerun()


# ============================================================
# STEP 6 — REVIEW
# ============================================================

elif st.session_state.current_step == 6:

    st.header(
        f"🔎 {t('review')}"
    )

    patient = (
        st.session_state.patient
    )

    st.subheader(
        t("patient_information")
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            t("name"),
            patient.get(
                "name",
                "N/A",
            ),
        )

    with col2:

        st.metric(
            t("age"),
            patient.get(
                "age",
                "N/A",
            ),
        )

    with col3:

        gender_display = {

            "Male":
                t("male"),

            "Female":
                t("female"),

            "Other":
                t("other"),
        }

        st.metric(
            t("gender"),
            gender_display.get(
                patient.get(
                    "gender",
                    "Other",
                ),
                patient.get(
                    "gender",
                    "N/A",
                ),
            ),
        )

    st.divider()

    review_data = {

        "Field": [

            t("presenting_complaint"),
            t("duration"),
            t("severity"),
            t("additional_symptoms"),
            t("past_history"),
            t("medications"),
            t("allergies"),
        ],

        "Information": [

            patient.get(
                "complaint",
                "",
            ),

            patient.get(
                "duration",
                "",
            ),

            patient.get(
                "severity",
                "",
            ),

            patient.get(
                "additional_symptoms",
                "",
            ),

            patient.get(
                "past_history",
                "",
            ),

            patient.get(
                "medications",
                "",
            ),

            patient.get(
                "allergies",
                "",
            ),
        ],
    }

    st.table(
        pd.DataFrame(
            review_data
        )
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(
            f"{t('next')} →",
            width="stretch",
        ):

            go_next()

            st.rerun()


# ============================================================
# STEP 7 — AI DECISION SUPPORT
# ============================================================

elif st.session_state.current_step == 7:

    st.header(
        f"🤖 {t('ai_decision_support')}"
    )

    patient = (
        st.session_state.patient
    )

    with st.spinner(
        "Analyzing clinical information..."
        if st.session_state.language == "English"
        else "क्लिनिकल जानकारी का विश्लेषण किया जा रहा है..."
    ):

        analysis = (
            run_ml_decision_support(
                patient
            )
        )

        patient_text = (
            get_patient_text(
                patient
            )
        )

        urgency = (
            urgency_flags(
                patient_text
            )
        )

    # --------------------------------------------------------
    # DETECTED SYMPTOMS
    # --------------------------------------------------------

    st.subheader(
        f"🧠 {t('detected_symptoms')}"
    )

    symptoms = analysis.get(
        "symptoms",
        []
    )

    if symptoms:

        for symptom in symptoms:

            st.write(
                f"• {symptom.replace('_', ' ').title()}"
            )

    else:

        st.info(
            "No model symptoms were directly matched."
            if st.session_state.language == "English"
            else "कोई सीधे मेल खाने वाले लक्षण नहीं मिले।"
        )

    # --------------------------------------------------------
    # CONDITIONS
    # --------------------------------------------------------

    st.subheader(
        f"🩺 {t('possible_conditions')}"
    )

    predictions = analysis.get(
        "predictions",
        []
    )

    if predictions:

        for index, prediction in enumerate(
            predictions,
            start=1,
        ):

            condition = prediction[
                "condition"
            ]

            score = prediction[
                "score"
            ]

            st.write(
                f"**{index}. {condition}**"
            )

            st.progress(
                min(
                    score / 100,
                    1.0,
                )
            )

            st.caption(
                f"Model score: {score:.2f}%"
            )

    else:

        st.info(
            "No predictions available."
            if st.session_state.language == "English"
            else "कोई संभावित स्थिति उपलब्ध नहीं है।"
        )

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    st.subheader(
        f"🚨 {t('urgency_review')}"
    )

    if urgency["urgent"]:

        st.error(
            t("urgent")
        )

        for flag in urgency["flags"]:

            st.write(
                f"• {flag}"
            )

    else:

        st.success(
            t("no_urgency")
        )

    st.divider()

    st.caption(
        t("disclaimer")
    )

    # --------------------------------------------------------
    # DOCTOR PORTAL
    # --------------------------------------------------------

    st.subheader(
        "💾 Doctor Portal"
        if st.session_state.language == "English"
        else "💾 डॉक्टर पोर्टल"
    )

    if st.session_state.patient_saved:

        st.success(

            (
                f"Patient already saved. "
                f"Patient ID: "
                f"{st.session_state.patient_id}"
            )

            if st.session_state.language == "English"

            else

            (
                f"रोगी पहले से सेव है। "
                f"रोगी ID: "
                f"{st.session_state.patient_id}"
            )
        )

    else:

        if st.button(
            f"💾 {t('save_doctor')}",
            width="stretch",
        ):

            try:

                patient_id = (
                    save_current_patient()
                )

                st.success(

                    (
                        f"Patient saved successfully! "
                        f"Patient ID: {patient_id}"
                    )

                    if st.session_state.language == "English"

                    else

                    (
                        f"रोगी सफलतापूर्वक सेव हो गया! "
                        f"रोगी ID: {patient_id}"
                    )
                )

            except Exception as error:

                st.error(
                    f"Could not save patient: {error}"
                )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(
            f"{t('next')} →",
            width="stretch",
        ):

            go_next()

            st.rerun()


# ============================================================
# STEP 8 — FINAL REPORT
# ============================================================

elif st.session_state.current_step == 8:

    st.header(
        f"📄 {t('final_report')}"
    )

    patient = (
        st.session_state.patient
    )

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    with st.spinner(
        "Preparing final clinical report..."
        if st.session_state.language == "English"
        else "अंतिम क्लिनिकल रिपोर्ट तैयार की जा रही है..."
    ):

        analysis = (
            run_ml_decision_support(
                patient
            )
        )

        patient_text = (
            get_patient_text(
                patient
            )
        )

        urgency = (
            urgency_flags(
                patient_text
            )
        )

    # --------------------------------------------------------
    # PATIENT INFORMATION
    # --------------------------------------------------------

    st.subheader(
        f"👤 {t('patient_information')}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            f"**{t('name')}:** "
            f"{patient.get('name', 'N/A')}"
        )

    with col2:

        st.write(
            f"**{t('age')}:** "
            f"{patient.get('age', 'N/A')}"
        )

    with col3:

        gender_display = {

            "Male":
                t("male"),

            "Female":
                t("female"),

            "Other":
                t("other"),
        }

        gender_text = gender_display.get(
            patient.get(
                "gender",
                "Other",
            ),
            "N/A",
        )

        st.write(
            f"**{t('gender')}:** "
            f"{gender_text}"
        )

    if st.session_state.patient_id:

        st.info(
            f"Patient ID: "
            f"{st.session_state.patient_id}"
        )

    st.divider()

    # --------------------------------------------------------
    # CLINICAL HISTORY
    # --------------------------------------------------------

    st.subheader(
        f"📋 {t('medical_history')}"
    )

    clinical_history = pd.DataFrame(
        {

            "Field": [

                t("presenting_complaint"),
                t("duration"),
                t("severity"),
                t("additional_symptoms"),
                t("past_history"),
                t("medications"),
                t("allergies"),
            ],

            "Information": [

                patient.get(
                    "complaint",
                    "",
                ),

                patient.get(
                    "duration",
                    "",
                ),

                patient.get(
                    "severity",
                    "",
                ),

                patient.get(
                    "additional_symptoms",
                    "",
                ),

                patient.get(
                    "past_history",
                    "",
                ),

                patient.get(
                    "medications",
                    "",
                ),

                patient.get(
                    "allergies",
                    "",
                ),
            ],
        }
    )

    st.table(
        clinical_history
    )

    st.divider()

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    st.subheader(
        f"🤖 {t('ai_decision_support')}"
    )

    st.write(
        f"**{t('detected_symptoms')}:**"
    )

    if analysis["symptoms"]:

        for symptom in analysis["symptoms"]:

            st.write(
                f"• {symptom.replace('_', ' ').title()}"
            )

    else:

        st.write(
            "No directly matched symptoms."
            if st.session_state.language == "English"
            else "कोई सीधे मेल खाने वाले लक्षण नहीं मिले।"
        )

    st.write(
        f"**{t('possible_conditions')}:**"
    )

    for index, prediction in enumerate(
        analysis["predictions"],
        start=1,
    ):

        st.write(
            f"{index}. "
            f"{prediction['condition']} "
            f"({prediction['score']:.2f}%)"
        )

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    st.subheader(
        f"🚨 {t('urgency_review')}"
    )

    if urgency["urgent"]:

        st.error(
            t("urgent")
        )

        for flag in urgency["flags"]:

            st.write(
                f"• {flag}"
            )

    else:

        st.success(
            t("no_urgency")
        )

    # --------------------------------------------------------
    # DOCTOR ASSESSMENT
    # --------------------------------------------------------

    st.subheader(
        f"👨‍⚕️ {t('doctor_assessment')}"
    )

    assessment = None

    if st.session_state.patient_id:

        try:

            assessment = (
                get_doctor_assessment(
                    st.session_state.patient_id
                )
            )

        except Exception:

            assessment = None

    if assessment:

        st.write(
            f"**Doctor:** "
            f"{assessment.get('doctor_name', 'N/A')}"
        )

        if assessment.get(
            "confirmed_condition"
        ):

            st.write(
                f"**Doctor-confirmed condition:** "
                f"{assessment.get('confirmed_condition')}"
            )

        st.write(
            f"**Final Assessment:** "
            f"{assessment.get('final_assessment', 'N/A')}"
        )

        st.write(
            f"**Doctor Notes:** "
            f"{assessment.get('doctor_notes', 'N/A')}"
        )

        st.write(
            f"**Follow-up:** "
            f"{assessment.get('follow_up', 'N/A')}"
        )

    else:

        st.info(

            "No doctor assessment has been added yet."
            if st.session_state.language == "English"

            else

            "अभी तक कोई डॉक्टर आकलन नहीं जोड़ा गया है।"
        )

    st.divider()

    # --------------------------------------------------------
    # REPORT OBJECT
    # --------------------------------------------------------

    clinical_report = {

        "patient_id":
            st.session_state.patient_id,

        "patient":
            patient,

        "analysis": {

            "symptoms":
                analysis.get(
                    "symptoms",
                    [],
                ),

            "predictions":
                analysis.get(
                    "predictions",
                    [],
                ),
        },

        "urgency":
            urgency,

        "assessment":
            assessment,
    }

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    st.subheader(
        "📄 PDF Report"
        if st.session_state.language == "English"
        else "📄 PDF रिपोर्ट"
    )

    if st.button(
        f"📄 {t('generate_pdf')}",
        width="stretch",
    ):

        try:

            output_directory = (
                BASE_DIR
                / "reports"
                / "output"
            )

            output_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            if st.session_state.patient_id:

                filename = (
                    f"clinassist_patient_"
                    f"{st.session_state.patient_id}"
                    f"_report.pdf"
                )

            else:

                filename = (
                    "clinassist_patient_report.pdf"
                )

            pdf_file = (
                output_directory
                / filename
            )

            export_report_to_pdf(
                clinical_report,
                pdf_file,
            )

            st.session_state.pdf_path = (
                str(pdf_file)
            )

            st.success(

                "PDF report generated successfully!"
                if st.session_state.language == "English"

                else

                "PDF रिपोर्ट सफलतापूर्वक तैयार हो गई!"
            )

        except Exception as error:

            st.error(
                f"Could not generate PDF: {error}"
            )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    if st.session_state.pdf_path:

        pdf_path = Path(
            st.session_state.pdf_path
        )

        if pdf_path.exists():

            with open(
                pdf_path,
                "rb",
            ) as file:

                pdf_data = file.read()

            st.download_button(

                label=(

                    "⬇️ Download Clinical Report"

                    if st.session_state.language == "English"

                    else

                    "⬇️ क्लिनिकल रिपोर्ट डाउनलोड करें"
                ),

                data=pdf_data,

                file_name=pdf_path.name,

                mime="application/pdf",

                width="stretch",
            )

    st.divider()

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            f"← {t('back')}",
            width="stretch",
        ):

            go_previous()

            st.rerun()

    with col2:

        if st.button(

            "🔄 Start New Patient"
            if st.session_state.language == "English"
            else "🔄 नया रोगी शुरू करें",

            width="stretch",
        ):

            reset_app()

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ClinAssist | AI-assisted clinical history and decision support"
)

st.caption(
    t("disclaimer")
)