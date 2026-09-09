# language/translations.py

TRANSLATIONS = {
    "English": {
        "app_title": "ClinAssist",
        "subtitle": "AI-Powered Clinical History & Decision Support System",

        "patient_information": "Patient Information",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",

        "male": "Male",
        "female": "Female",
        "other": "Other",

        "presenting_complaint": "Presenting Complaint",
        "main_problem": "What is the main problem or symptom?",

        "basic_details": "Basic Symptom Details",
        "duration": "How long have you had this problem?",
        "severity": "How severe is the problem?",

        "mild": "Mild",
        "moderate": "Moderate",
        "severe": "Severe",

        "additional_symptoms": "Additional Symptoms",
        "medical_history": "Medical History",
        "past_history": "Past Medical History",
        "medications": "Current Medications",
        "allergies": "Drug or Other Allergies",

        "review": "Review",
        "ai_decision_support": "AI Decision Support",
        "possible_conditions": "Possible Conditions to Consider",
        "detected_symptoms": "Detected Symptoms",
        "urgency_review": "Urgency Review",

        "doctor_assessment": "Doctor Assessment",
        "final_report": "Final Clinical Report",

        "save_doctor": "Save & Send to Doctor Portal",
        "generate_pdf": "Generate & Prepare PDF",

        "next": "Continue",
        "back": "Back",

        "no_urgency": "No predefined urgency indicators detected.",
        "urgent": "Potential urgency indicators detected.",

        "disclaimer": (
            "AI-generated information is intended only to support "
            "clinical review and does not replace professional "
            "clinical judgment."
        ),
    },

    "Hindi": {
        "app_title": "क्लिनअसिस्ट",
        "subtitle": "AI-संचालित क्लिनिकल हिस्ट्री और निर्णय सहायता प्रणाली",

        "patient_information": "रोगी की जानकारी",
        "name": "नाम",
        "age": "आयु",
        "gender": "लिंग",

        "male": "पुरुष",
        "female": "महिला",
        "other": "अन्य",

        "presenting_complaint": "मुख्य शिकायत",
        "main_problem": "मुख्य समस्या या लक्षण क्या है?",

        "basic_details": "लक्षणों की मूल जानकारी",
        "duration": "यह समस्या आपको कितने समय से है?",
        "severity": "समस्या कितनी गंभीर है?",

        "mild": "हल्का",
        "moderate": "मध्यम",
        "severe": "गंभीर",

        "additional_symptoms": "अन्य लक्षण",
        "medical_history": "चिकित्सीय इतिहास",
        "past_history": "पिछला चिकित्सीय इतिहास",
        "medications": "वर्तमान दवाएँ",
        "allergies": "दवा या अन्य एलर्जी",

        "review": "समीक्षा",
        "ai_decision_support": "AI निर्णय सहायता",
        "possible_conditions": "विचार करने योग्य संभावित स्थितियाँ",
        "detected_symptoms": "पहचाने गए लक्षण",
        "urgency_review": "तत्कालता की समीक्षा",

        "doctor_assessment": "डॉक्टर का आकलन",
        "final_report": "अंतिम क्लिनिकल रिपोर्ट",

        "save_doctor": "सेव करें और डॉक्टर पोर्टल पर भेजें",
        "generate_pdf": "PDF तैयार करें",

        "next": "आगे बढ़ें",
        "back": "पीछे जाएँ",

        "no_urgency": "कोई पूर्वनिर्धारित तत्कालता संकेत नहीं मिले।",
        "urgent": "संभावित तत्कालता संकेत पाए गए हैं।",

        "disclaimer": (
            "AI द्वारा दी गई जानकारी केवल क्लिनिकल समीक्षा में "
            "सहायता के लिए है और पेशेवर चिकित्सकीय निर्णय का "
            "स्थान नहीं लेती।"
        ),
    },
}


def get_translation(language, key):
    """
    Return translated text for the selected language.
    Falls back to English if the key is unavailable.
    """

    language_data = TRANSLATIONS.get(
        language,
        TRANSLATIONS["English"]
    )

    return language_data.get(
        key,
        TRANSLATIONS["English"].get(key, key)
    )