import re


# --------------------------------------------------
# RED-FLAG PATTERNS
# --------------------------------------------------

RED_FLAGS = {
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


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(text):
    """Normalize text for reliable phrase matching."""

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# PHRASE MATCHING
# --------------------------------------------------

def phrase_exists(text, phrase):
    """Check whether a phrase exists as a complete phrase."""

    pattern = r"\b" + re.escape(phrase) + r"\b"

    return re.search(pattern, text) is not None


# --------------------------------------------------
# URGENCY ANALYSIS
# --------------------------------------------------

def detect_urgency(text):
    """
    Detect predefined red-flag indicators.

    Returns:
        {
            "urgent": True/False,
            "flags": [...],
            "matched_phrases": [...],
            "message": "..."
        }
    """

    normalized_text = normalize_text(text)

    detected_flags = []
    matched_phrases = []

    for flag_name, phrases in RED_FLAGS.items():

        for phrase in phrases:

            normalized_phrase = normalize_text(phrase)

            if phrase_exists(
                normalized_text,
                normalized_phrase
            ):
                detected_flags.append(flag_name)
                matched_phrases.append(phrase)
                break

    urgent = len(detected_flags) > 0

    if urgent:
        message = (
            "Potential urgency indicators detected. "
            "Prompt clinical assessment is advisable."
        )
    else:
        message = (
            "No predefined urgency indicators were detected "
            "by this screening module."
        )

    return {
        "urgent": urgent,
        "flags": detected_flags,
        "matched_phrases": matched_phrases,
        "message": message,
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("CLINASSIST URGENCY DETECTION TEST")
    print("=" * 50)

    test_cases = [
        (
            "Normal symptoms",
            "I have a mild headache and feel tired."
        ),

        (
            "Breathing difficulty",
            "I am having severe difficulty breathing."
        ),

        (
            "Chest discomfort",
            "I have severe chest pain and pressure in my chest."
        ),

        (
            "Loss of consciousness",
            "I fainted earlier today."
        ),

        (
            "Neurological symptoms",
            "I suddenly have difficulty speaking."
        ),

        (
            "Severe bleeding",
            "I have heavy bleeding."
        ),

        (
            "Allergic reaction indicators",
            "I have swelling of my throat and difficulty swallowing."
        ),
    ]

    for number, (name, text) in enumerate(test_cases, start=1):

        print(f"\nTest {number}: {name}")
        print(f"Input: {text}")

        result = detect_urgency(text)

        if result["urgent"]:

            print("🚨 Urgency indicators detected:")

            for flag in result["flags"]:
                print(f"- {flag}")

            print(
                "Matched phrases:",
                ", ".join(result["matched_phrases"])
            )

        else:
            print("✅ No predefined urgency indicators detected.")

        print("Message:")
        print(result["message"])

    print("\n" + "=" * 50)
    print("URGENCY TEST COMPLETED")
    print("=" * 50)