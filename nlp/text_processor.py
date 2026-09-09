import re


# ---------------------------------------------------------
# Hindi / English symptom aliases
# ---------------------------------------------------------

SYMPTOM_ALIASES = {
    # Headache
    "सिर दर्द": "headache",
    "सिर में दर्द": "headache",
    "सर दर्द": "headache",
    "सर में दर्द": "headache",
    "मेरा सिर दर्द": "headache",
    "मेरा सर दर्द": "headache",
    "head pain": "headache",
    "head hurts": "headache",
    "my head hurts": "headache",
    "my head is hurting": "headache",

    # Fever
    "बुखार": "fever",
    "मुझे बुखार है": "fever",
    "तेज बुखार": "high_fever",
    "fever": "fever",

    # Cough
    "खांसी": "cough",
    "खाँसी": "cough",
    "मुझे खांसी है": "cough",
    "मुझे खाँसी है": "cough",
    "cough": "cough",

    # Cold
    "जुकाम": "cold",
    "सर्दी": "cold",
    "नाक बहना": "runny_nose",
    "बहती नाक": "runny_nose",
    "cold": "cold",
    "runny nose": "runny_nose",

    # Nausea
    "जी मिचलाना": "nausea",
    "जी मिचला रहा है": "nausea",
    "उल्टी जैसा": "nausea",
    "मितली": "nausea",
    "nausea": "nausea",

    # Vomiting
    "उल्टी": "vomiting",
    "उल्टी हो रही है": "vomiting",
    "vomiting": "vomiting",

    # Stomach pain
    "पेट दर्द": "stomach_pain",
    "पेट में दर्द": "stomach_pain",
    "मेरा पेट दर्द": "stomach_pain",
    "मेरा पेट दर्द कर रहा है": "stomach_pain",
    "पेट दुख रहा है": "stomach_pain",
    "stomach pain": "stomach_pain",
    "stomach hurts": "stomach_pain",
    "my stomach hurts": "stomach_pain",

    # Chest pain
    "सीने में दर्द": "chest_pain",
    "छाती में दर्द": "chest_pain",
    "सीने का दर्द": "chest_pain",
    "chest pain": "chest_pain",

    # Breathing difficulty
    "सांस लेने में दिक्कत": "breathlessness",
    "सांस लेने में परेशानी": "breathlessness",
    "सांस फूलना": "breathlessness",
    "सांस नहीं आ रही": "breathlessness",
    "breathing difficulty": "breathlessness",
    "difficulty breathing": "breathlessness",
    "shortness of breath": "breathlessness",

    # Fatigue
    "थकान": "fatigue",
    "बहुत थकान": "fatigue",
    "कमजोरी": "weakness",
    "बहुत कमजोरी": "weakness",
    "थका हुआ": "fatigue",
    "थकी हुई": "fatigue",
    "fatigue": "fatigue",
    "tired": "fatigue",
    "very tired": "fatigue",
    "weakness": "weakness",

    # Muscle weakness
    "मांसपेशियों में कमजोरी": "muscle_weakness",
    "मांसपेशी कमजोरी": "muscle_weakness",
    "muscle weakness": "muscle_weakness",

    # Joint pain
    "जोड़ों में दर्द": "joint_pain",
    "जोड़ का दर्द": "joint_pain",
    "जोड़ों का दर्द": "joint_pain",
    "joint pain": "joint_pain",

    # Itching
    "खुजली": "itching",
    "खुजली होना": "itching",
    "itching": "itching",

    # Skin rash
    "त्वचा पर दाने": "skin_rash",
    "शरीर पर दाने": "skin_rash",
    "दाने": "skin_rash",
    "rash": "skin_rash",
    "skin rash": "skin_rash",

    # Phlegm
    "बलगम": "phlegm",
    "कफ": "phlegm",
    "बलगम आना": "phlegm",
    "phlegm": "phlegm",

    # Loss of appetite
    "भूख नहीं लगना": "loss_of_appetite",
    "भूख नहीं लग रही": "loss_of_appetite",
    "भूख कम लगना": "loss_of_appetite",
    "भूख की कमी": "loss_of_appetite",
    "loss of appetite": "loss_of_appetite",
}


# ---------------------------------------------------------
# Normalize text
# ---------------------------------------------------------

def normalize_text(text):
    """
    Convert text into a simpler searchable form.
    Works with both Hindi and English text.
    """

    if not text:
        return ""

    text = str(text).strip().lower()

    # Remove unnecessary punctuation.
    text = re.sub(r"[.,!?;:(){}\[\]\"']", " ", text)

    # Normalize multiple spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# Translate known Hindi/English phrases
# ---------------------------------------------------------

def normalize_clinical_text(text):
    """
    Convert known Hindi/English symptom phrases
    into standard English clinical symptom names.
    """

    normalized = normalize_text(text)

    if not normalized:
        return ""

    # Longest phrases first so that
    # specific phrases are matched before shorter ones.
    aliases = sorted(
        SYMPTOM_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for phrase, symptom in aliases:
        phrase_normalized = normalize_text(phrase)

        if phrase_normalized in normalized:
            normalized = normalized.replace(
                phrase_normalized,
                f" {symptom} "
            )

    return normalize_text(normalized)


# ---------------------------------------------------------
# Extract symptoms
# ---------------------------------------------------------

def extract_symptoms(text, symptom_list=None):
    """
    Extract recognized symptoms from Hindi or English text.

    If symptom_list is supplied, only symptoms that exist
    in the ML model's symptom list are returned.
    """

    original_text = normalize_text(text)

    if not original_text:
        return []

    clinical_text = normalize_clinical_text(original_text)

    detected = set()

    # First use the alias system.
    for phrase, symptom in SYMPTOM_ALIASES.items():
        phrase_normalized = normalize_text(phrase)

        if phrase_normalized in original_text:
            detected.add(symptom)

    # Also search directly for model symptoms.
    if symptom_list:
        for symptom in symptom_list:
            symptom_normalized = normalize_text(symptom)

            if not symptom_normalized:
                continue

            if symptom_normalized in clinical_text:
                detected.add(symptom)

    return sorted(detected)


# ---------------------------------------------------------
# Readable symptom names
# ---------------------------------------------------------

def readable_symptom_name(symptom):
    """
    Convert model symptom names into readable text.
    """

    if not symptom:
        return ""

    return symptom.replace("_", " ").strip().title()


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    test_cases = [
        "मेरे सिर में दर्द है",
        "मेरा पेट दर्द कर रहा है",
        "मुझे खांसी है और बुखार है",
        "मुझे सांस लेने में दिक्कत है",
        "मुझे जी मिचला रहा है",
        "I have a headache and nausea",
        "My stomach hurts",
        "I have cough and phlegm",
    ]

    print("=================================")
    print("CLINASSIST NLP TEST")
    print("=================================")

    for text in test_cases:

        symptoms = extract_symptoms(text)

        print("\nInput:", text)
        print("Detected:", symptoms)

    print("\n=================================")
    print("NLP TEST COMPLETED")
    print("=================================")