import re


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize English clinical text for symptom matching.
    """

    text = str(text).lower().strip()

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# HINDI / HINGLISH → ENGLISH SYMPTOM MAPPING
# ============================================================

HINDI_SYMPTOM_MAP = {

    # --------------------------------------------------------
    # HEAD
    # --------------------------------------------------------

    "सिर में दर्द": "headache",
    "सिर दर्द": "headache",
    "सिरदर्द": "headache",
    "सर में दर्द": "headache",
    "सर दर्द": "headache",
    "सरदर्द": "headache",
    "सिर दुख रहा": "headache",
    "सर दुख रहा": "headache",
    "मेरे सिर में दर्द": "headache",
    "मेरे सर में दर्द": "headache",

    "सिर घूमना": "dizziness",
    "सिर घूम रहा": "dizziness",
    "चक्कर": "dizziness",
    "चक्कर आना": "dizziness",
    "चक्कर आ रहे": "dizziness",
    "मुझे चक्कर": "dizziness",

    # Hinglish
    "sar mein dard": "headache",
    "sir mein dard": "headache",
    "sar dard": "headache",
    "sir dard": "headache",
    "sir dukh raha": "headache",
    "sar dukh raha": "headache",
    "chakkar": "dizziness",
    "chakkar aa raha": "dizziness",

    # --------------------------------------------------------
    # NAUSEA / VOMITING
    # --------------------------------------------------------

    "मतली": "nausea",
    "जी मिचलाना": "nausea",
    "जी मिचला रहा": "nausea",
    "मितली": "nausea",
    "उल्टी": "vomiting",
    "उल्टी होना": "vomiting",
    "उल्टी हो रही": "vomiting",
    "उल्टी आना": "vomiting",

    "matli": "nausea",
    "ji michlana": "nausea",
    "ji michla raha": "nausea",
    "ulti": "vomiting",
    "ulti ho rahi": "vomiting",
    "ulti aa rahi": "vomiting",

    # --------------------------------------------------------
    # RESPIRATORY
    # --------------------------------------------------------

    "खांसी": "cough",
    "खाँसी": "cough",
    "खांसी हो रही": "cough",
    "खांसना": "cough",

    "सांस लेने में कठिनाई": "breathlessness",
    "सांस लेने में दिक्कत": "breathlessness",
    "सांस लेने में परेशानी": "breathlessness",
    "सांस फूलना": "breathlessness",
    "सांस फूल रही": "breathlessness",
    "सांस की तकलीफ": "breathlessness",
    "सांस नहीं आ रही": "breathlessness",

    "बलगम": "phlegm",
    "बलगम आना": "phlegm",
    "कफ": "phlegm",

    "खराश": "sore_throat",
    "गले में खराश": "sore_throat",
    "गले में दर्द": "sore_throat",

    "खांसी और बुखार": "cough fever",

    # Hinglish
    "khansi": "cough",
    "saans lene mein dikkat": "breathlessness",
    "saans lene mein pareshani": "breathlessness",
    "saans phoolna": "breathlessness",
    "balgam": "phlegm",
    "gale mein dard": "sore_throat",
    "gale mein kharash": "sore_throat",

    # --------------------------------------------------------
    # CHEST
    # --------------------------------------------------------

    "सीने में दर्द": "chest_pain",
    "सीने में भारीपन": "chest_pain",
    "सीने में तकलीफ": "chest_pain",
    "छाती में दर्द": "chest_pain",

    "seene mein dard": "chest_pain",
    "seene mein takleef": "chest_pain",
    "chhati mein dard": "chest_pain",

    # --------------------------------------------------------
    # STOMACH / DIGESTIVE
    # --------------------------------------------------------

    "पेट में दर्द": "stomach_pain",
    "पेट दर्द": "stomach_pain",
    "पेट दुखना": "stomach_pain",
    "पेट दुख रहा": "stomach_pain",
    "पेट की समस्या": "stomach_pain",
    "पेट में तकलीफ": "stomach_pain",

    "पेट खराब": "stomach_pain",
    "पेट की परेशानी": "stomach_pain",

    "भूख कम लगना": "loss_of_appetite",
    "भूख नहीं लगना": "loss_of_appetite",
    "भूख नहीं लग रही": "loss_of_appetite",
    "भूख कम है": "loss_of_appetite",
    "भूख में कमी": "loss_of_appetite",

    "दस्त": "diarrhea",
    "पतले दस्त": "diarrhea",
    "पतला मल": "diarrhea",
    "लूज मोशन": "diarrhea",

    "पेट में गैस": "gas",
    "गैस": "gas",

    # Hinglish
    "pet mein dard": "stomach_pain",
    "pet dard": "stomach_pain",
    "pet dukh raha": "stomach_pain",
    "bhookh kam lagna": "loss_of_appetite",
    "bhookh nahi lagna": "loss_of_appetite",
    "dast": "diarrhea",
    "loose motion": "diarrhea",
    "gas": "gas",

    # --------------------------------------------------------
    # FEVER
    # --------------------------------------------------------

    "बुखार": "fever",
    "तेज बुखार": "fever",
    "बुखार है": "fever",
    "बुखार हो रहा": "fever",

    "bukhar": "fever",
    "tez bukhar": "fever",

    # --------------------------------------------------------
    # FATIGUE / WEAKNESS
    # --------------------------------------------------------

    "थकान": "fatigue",
    "बहुत थकान": "fatigue",
    "थका हुआ": "fatigue",
    "थकावट": "fatigue",

    "कमजोरी": "weakness",
    "बहुत कमजोरी": "weakness",
    "कमजोर महसूस": "weakness",
    "शरीर में कमजोरी": "weakness",

    "thakan": "fatigue",
    "thakawat": "fatigue",
    "kamzori": "weakness",
    "bahut kamzori": "weakness",

    # --------------------------------------------------------
    # SKIN
    # --------------------------------------------------------

    "खुजली": "itching",
    "खुजली होना": "itching",
    "बहुत खुजली": "itching",

    "त्वचा पर दाने": "skin_rash",
    "शरीर पर दाने": "skin_rash",
    "दाने": "skin_rash",
    "चकत्ते": "skin_rash",
    "लाल चकत्ते": "red_spots_over_body",
    "शरीर पर लाल दाने": "red_spots_over_body",

    "खुजली और दाने": "itching skin_rash",

    "khujli": "itching",
    "daane": "skin_rash",
    "chakatte": "skin_rash",

    # --------------------------------------------------------
    # JOINT / MUSCLE
    # --------------------------------------------------------

    "जोड़ों में दर्द": "joint_pain",
    "जोड़ों का दर्द": "joint_pain",
    "जोड़ दर्द": "joint_pain",

    "मांसपेशियों में दर्द": "muscle_pain",
    "मांसपेशियों का दर्द": "muscle_pain",
    "मांसपेशियों में कमजोरी": "muscle_weakness",

    "jodon mein dard": "joint_pain",
    "jodon ka dard": "joint_pain",
    "muscle pain": "muscle_pain",
    "muscles mein dard": "muscle_pain",
    "muscles mein kamzori": "muscle_weakness",

    # --------------------------------------------------------
    # COLD / NOSE
    # --------------------------------------------------------

    "नाक बहना": "runny_nose",
    "नाक से पानी आना": "runny_nose",
    "छींक": "sneezing",
    "छींक आना": "sneezing",
    "बार बार छींक": "sneezing",

    "naak behna": "runny_nose",
    "chheenk": "sneezing",

    # --------------------------------------------------------
    # VISION
    # --------------------------------------------------------

    "धुंधला दिखाई देना": "blurred_and_distorted_vision",
    "धुंधला दिखना": "blurred_and_distorted_vision",
    "दृष्टि धुंधली": "blurred_and_distorted_vision",

    "dhundhla dikhna": "blurred_and_distorted_vision",
}


# ============================================================
# ENGLISH CLINICAL ALIASES
# ============================================================

ENGLISH_ALIASES = {

    "headache": [
        "headache",
        "head pain",
        "pain in head",
        "pain in my head",
        "my head hurts",
        "my head has been hurting",
        "my head is hurting",
        "head is hurting",
        "head has been hurting",
        "head hurts",
        "head hurting",
   ],

    "dizziness": [
        "dizziness",
        "dizzy",
        "feeling dizzy",
        "lightheaded",
    ],

    "nausea": [
        "nausea",
        "feeling nauseous",
        "feeling sick",
        "sick feeling",
    ],

    "vomiting": [
        "vomiting",
        "vomit",
        "throwing up",
        "threw up",
    ],

    "cough": [
        "cough",
        "coughing",
    ],

    "breathlessness": [
        "breathlessness",
        "difficulty breathing",
        "trouble breathing",
        "shortness of breath",
        "breathing difficulty",
    ],

    "phlegm": [
        "phlegm",
        "mucus",
        "sputum",
        "mucus in chest",
    ],

    "chest_pain": [
        "chest pain",
        "pain in chest",
        "chest discomfort",
        "chest pressure",
    ],

    "stomach_pain": [
        "stomach pain",
        "abdominal pain",
        "belly pain",
        "pain in stomach",
        "pain in abdomen",
        "my stomach hurts",
        "stomach hurts",
    ],

    "fever": [
        "fever",
        "high temperature",
        "temperature",
    ],

    "fatigue": [
        "fatigue",
        "tired",
        "tiredness",
        "very tired",
        "exhausted",
    ],

    "weakness": [
        "weakness",
        "weak",
        "feeling weak",
    ],

    "itching": [
        "itching",
        "itchy",
        "itch",
    ],

    "skin_rash": [
        "skin rash",
        "rash",
        "skin rashes",
    ],

    "red_spots_over_body": [
        "red spots",
        "red spots over body",
        "red spots on body",
    ],

    "joint_pain": [
        "joint pain",
        "pain in joints",
        "joints hurt",
    ],

    "muscle_pain": [
        "muscle pain",
        "muscle ache",
        "muscles hurt",
    ],

    "muscle_weakness": [
        "muscle weakness",
        "weak muscles",
    ],

    "loss_of_appetite": [
        "loss of appetite",
        "low appetite",
        "poor appetite",
        "no appetite",
        "not feeling hungry",
    ],

    "diarrhea": [
        "diarrhea",
        "diarrhoea",
        "loose motion",
        "loose motions",
        "loose stool",
    ],

    "gas": [
        "gas",
        "gas problem",
        "bloating",
    ],

    "runny_nose": [
        "runny nose",
        "nose running",
        "running nose",
    ],

    "sneezing": [
        "sneezing",
        "sneeze",
        "sneezes",
    ],

    "sore_throat": [
        "sore throat",
        "throat pain",
        "pain in throat",
        "throat irritation",
    ],

    "blurred_and_distorted_vision": [
        "blurred vision",
        "blurry vision",
        "distorted vision",
        "vision is blurry",
    ],
}


# ============================================================
# HINDI NORMALIZATION
# ============================================================

def normalize_hindi_text(text):
    """
    Convert common Hindi/Hinglish symptom phrases
    into English clinical symptom terms.
    """

    text = str(text).lower().strip()

    # Longest phrases first so smaller phrases do not
    # interfere with larger clinical expressions.
    replacements = sorted(
        HINDI_SYMPTOM_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for hindi_phrase, english_term in replacements:

        text = text.replace(
            hindi_phrase.lower(),
            f" {english_term} "
        )

    return text


# ============================================================
# CLINICAL TEXT NORMALIZATION
# ============================================================

def normalize_clinical_text(text):
    """
    Prepare English, Hindi and Hinglish patient text
    for symptom extraction.
    """

    text = str(text)

    # First convert Hindi/Hinglish symptom expressions
    # into English clinical terms.
    text = normalize_hindi_text(text)

    # Then normalize English text.
    text = normalize_text(text)

    return text


# ============================================================
# PHRASE MATCHING
# ============================================================

def phrase_exists(text, phrase):
    """
    Check whether a clinical phrase exists as a
    complete phrase rather than a partial word.
    """

    text = normalize_clinical_text(text)
    phrase = normalize_text(phrase)

    if not phrase:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(phrase)
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        text
    ) is not None


# ============================================================
# SYMPTOM EXTRACTION
# ============================================================

def extract_symptoms(text, symptom_list):
    """
    Extract symptoms from patient text.

    Supports:
    - English
    - Hindi
    - common Hinglish
    - common patient wording
    """

    normalized_text = normalize_clinical_text(
        text
    )

    matched = []

    for symptom in symptom_list:

        canonical = normalize_text(
            symptom
        )

        if not canonical:
            continue

        candidates = [
            canonical
        ]

        # Add English aliases.
        aliases = ENGLISH_ALIASES.get(
            canonical.replace(" ", "_"),
            []
        )

        for alias in aliases:

            alias_normalized = normalize_text(
                alias
            )

            if alias_normalized:
                candidates.append(
                    alias_normalized
                )

        found = False

        for candidate in candidates:

            pattern = (
                r"(?<!\w)"
                + re.escape(candidate)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized_text
            ):

                found = True
                break

        if found:

            matched.append(
                symptom
            )

    return matched


# ============================================================
# READABLE SYMPTOM NAME
# ============================================================

def readable_symptom_name(symptom):
    """
    Convert model symptom names into readable text.
    """

    text = str(symptom)

    text = text.replace(
        "_",
        " "
    )

    return text.strip().title()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_cases = [

        "मेरे सिर में दर्द है",

        "मुझे चक्कर आ रहे हैं",

        "मुझे उल्टी और मतली हो रही है",

        "मुझे सांस लेने में कठिनाई हो रही है",

        "मेरे पेट में दर्द है",

        "मुझे खांसी और बुखार है",

        "मेरे जोड़ों में दर्द है",

        "My head has been hurting",

        "My stomach hurts",

        "I have cough and fever",
    ]

    sample_symptoms = [
        "headache",
        "dizziness",
        "nausea",
        "vomiting",
        "breathlessness",
        "stomach_pain",
        "cough",
        "fever",
        "joint_pain",
    ]

    print("=" * 60)
    print("CLINASSIST MULTILINGUAL NLP TEST")
    print("=" * 60)

    for text in test_cases:

        symptoms = extract_symptoms(
            text,
            sample_symptoms
        )

        print("\nInput:")
        print(text)

        print("Detected:")
        print(
            [
                readable_symptom_name(
                    symptom
                )
                for symptom in symptoms
            ]
        )

    print("\n" + "=" * 60)
    print("NLP TEST COMPLETED")
    print("=" * 60)