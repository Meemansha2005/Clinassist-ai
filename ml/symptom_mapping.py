import re


# Exact feature names used by the trained model.
MODEL_SYMPTOMS = [
    "itching",
    "skin_rash",
    "nodal_skin_eruptions",
    "continuous_sneezing",
    "shivering",
    "chills",
    "joint_pain",
    "stomach_pain",
    "acidity",
    "ulcers_on_tongue",
    "muscle_wasting",
    "vomiting",
    "burning_micturition",
    "spotting_ urination",
    "fatigue",
    "weight_gain",
    "anxiety",
    "cold_hands_and_feets",
    "mood_swings",
    "weight_loss",
    "restlessness",
    "lethargy",
    "patches_in_throat",
    "irregular_sugar_level",
    "cough",
    "high_fever",
    "sunken_eyes",
    "breathlessness",
    "sweating",
    "dehydration",
    "indigestion",
    "headache",
    "yellowish_skin",
    "dark_urine",
    "nausea",
    "loss_of_appetite",
    "pain_behind_the_eyes",
    "back_pain",
    "constipation",
    "abdominal_pain",
    "diarrhoea",
    "mild_fever",
    "yellow_urine",
    "yellowing_of_eyes",
    "acute_liver_failure",
    "fluid_overload",
    "swelling_of_stomach",
    "swelled_lymph_nodes",
    "malaise",
    "blurred_and_distorted_vision",
    "phlegm",
    "throat_irritation",
    "redness_of_eyes",
    "sinus_pressure",
    "runny_nose",
    "congestion",
    "chest_pain",
    "weakness_in_limbs",
    "fast_heart_rate",
    "pain_during_bowel_movements",
    "pain_in_anal_region",
    "bloody_stool",
    "irritation_in_anus",
    "neck_pain",
    "dizziness",
    "cramps",
    "bruising",
    "obesity",
    "swollen_legs",
    "swollen_blood_vessels",
    "puffy_face_and_eyes",
    "enlarged_thyroid",
    "brittle_nails",
    "swollen_extremeties",
    "excessive_hunger",
    "extra_marital_contacts",
    "drying_and_tingling_lips",
    "slurred_speech",
    "knee_pain",
    "hip_joint_pain",
    "muscle_weakness",
    "stiff_neck",
    "swelling_joints",
    "movement_stiffness",
    "spinning_movements",
    "loss_of_balance",
    "unsteadiness",
    "weakness_of_one_body_side",
    "loss_of_smell",
    "bladder_discomfort",
    "foul_smell_of urine",
    "continuous_feel_of_urine",
    "passage_of_gases",
    "internal_itching",
    "toxic_look_(typhos)",
    "depression",
    "irritability",
    "muscle_pain",
    "altered_sensorium",
    "red_spots_over_body",
    "belly_pain",
    "abnormal_menstruation",
    "dischromic _patches",
    "watering_from_eyes",
    "increased_appetite",
    "polyuria",
    "family_history",
    "mucoid_sputum",
    "rusty_sputum",
    "lack_of_concentration",
    "visual_disturbances",
    "receiving_blood_transfusion",
    "receiving_unsterile_injections",
    "coma",
    "stomach_bleeding",
    "distention_of_abdomen",
    "history_of_alcohol_consumption",
    "fluid_overload.1",
    "blood_in_sputum",
    "prominent_veins_on_calf",
    "palpitations",
    "painful_walking",
    "pus_filled_pimples",
    "blackheads",
    "scurring",
    "skin_peeling",
    "silver_like_dusting",
    "small_dents_in_nails",
    "inflammatory_nails",
    "blister",
    "red_sore_around_nose",
    "yellow_crust_ooze",
]


# Natural-language expressions mapped to the exact model feature.
SYMPTOM_ALIASES = {

    "itching": [
        "itch",
        "itchy",
        "itching",
        "skin itching",
        "itchy skin",
    ],

    "skin_rash": [
        "rash",
        "rashes",
        "skin rash",
        "skin rashes",
        "skin irritation",
    ],

    "nodal_skin_eruptions": [
        "nodal skin eruptions",
        "skin eruptions",
    ],

    "continuous_sneezing": [
        "sneezing",
        "sneeze",
        "sneezing continuously",
        "continuous sneezing",
    ],

    "shivering": [
        "shivering",
        "shaking",
        "trembling",
    ],

    "chills": [
        "chills",
        "feeling cold",
        "cold feeling",
    ],

    "joint_pain": [
        "joint pain",
        "pain in joints",
        "joints hurt",
        "painful joints",
    ],

    "stomach_pain": [
        "stomach pain",
        "stomach ache",
        "pain in stomach",
        "tummy pain",
        "tummy ache",
    ],

    "acidity": [
        "acidity",
        "acid reflux",
        "heartburn",
        "burning in chest",
    ],

    "ulcers_on_tongue": [
        "tongue ulcer",
        "tongue ulcers",
        "ulcers on tongue",
        "sore tongue",
    ],

    "vomiting": [
        "vomiting",
        "vomit",
        "throwing up",
        "threw up",
    ],

    "burning_micturition": [
        "burning urination",
        "burning while urinating",
        "burning while passing urine",
        "painful urination",
        "burning urine",
    ],

    "fatigue": [
        "fatigue",
        "tired",
        "tiredness",
        "very tired",
        "extreme tiredness",
        "exhaustion",
        "exhausted",
        "feeling exhausted",
        "no energy",
        "low energy",
    ],

    "weight_gain": [
        "weight gain",
        "gaining weight",
        "gained weight",
    ],

    "anxiety": [
        "anxiety",
        "anxious",
        "nervous",
        "feeling nervous",
        "very nervous",
    ],

    "cold_hands_and_feets": [
        "cold hands",
        "cold feet",
        "cold hands and feet",
        "cold hands and feets",
    ],

    "mood_swings": [
        "mood swings",
        "mood changes",
        "changing moods",
    ],

    "weight_loss": [
        "weight loss",
        "losing weight",
        "lost weight",
    ],

    "restlessness": [
        "restlessness",
        "restless",
        "unable to sit still",
    ],

    "lethargy": [
        "lethargy",
        "sluggish",
        "sluggishness",
        "feeling sluggish",
    ],

    "patches_in_throat": [
        "patches in throat",
        "throat patches",
        "patches on throat",
    ],

    "cough": [
        "cough",
        "coughing",
    ],

    "high_fever": [
        "high fever",
        "very high temperature",
        "high temperature",
    ],

    "breathlessness": [
        "breathlessness",
        "shortness of breath",
        "difficulty breathing",
        "breathing difficulty",
        "trouble breathing",
        "breathing problem",
        "cannot breathe properly",
        "can't breathe properly",
    ],

    "sweating": [
        "sweating",
        "excessive sweating",
    ],

    "dehydration": [
        "dehydration",
        "dehydrated",
        "very thirsty",
        "dry mouth",
    ],

    "indigestion": [
        "indigestion",
        "poor digestion",
        "digestive problem",
        "difficulty digesting",
    ],

    "headache": [
        "headache",
        "head pain",
        "pain in head",
        "my head hurts",
        "head hurts",
        "head is hurting",
    ],

    "yellowish_skin": [
        "yellow skin",
        "yellowish skin",
        "skin looks yellow",
    ],

    "dark_urine": [
        "dark urine",
        "very dark urine",
        "brown urine",
    ],

    "nausea": [
        "nausea",
        "nauseous",
        "nauseated",
        "feeling nauseous",
        "feel nauseous",
        "i feel nauseous",
        "feeling sick",
        "feel sick",
        "sick to my stomach",
    ],

    "loss_of_appetite": [
        "loss of appetite",
        "no appetite",
        "not hungry",
        "reduced appetite",
        "lack of appetite",
        "don't feel hungry",
    ],

    "pain_behind_the_eyes": [
        "pain behind eyes",
        "pain behind the eyes",
        "eye pain",
    ],

    "back_pain": [
        "back pain",
        "pain in back",
        "my back hurts",
    ],

    "constipation": [
        "constipation",
        "difficulty passing stool",
        "hard stool",
        "cannot pass stool",
    ],

    "abdominal_pain": [
        "abdominal pain",
        "abdomen pain",
        "pain in abdomen",
        "abdominal ache",
    ],

    "diarrhoea": [
        "diarrhea",
        "diarrhoea",
        "loose motion",
        "loose motions",
        "loose stool",
        "loose stools",
        "frequent loose stools",
    ],

    "mild_fever": [
        "mild fever",
        "low fever",
        "slight fever",
        "little fever",
    ],

    "yellow_urine": [
        "yellow urine",
        "urine is yellow",
    ],

    "yellowing_of_eyes": [
        "yellow eyes",
        "yellowing of eyes",
        "eyes look yellow",
    ],

    "swelling_of_stomach": [
        "swollen stomach",
        "stomach swelling",
        "abdominal swelling",
    ],

    "swelled_lymph_nodes": [
        "swollen lymph nodes",
        "swelled lymph nodes",
        "enlarged lymph nodes",
        "lymph nodes are swollen",
    ],

    "malaise": [
        "malaise",
        "feeling unwell",
        "generally unwell",
        "not feeling well",
        "feel unwell",
    ],

    "blurred_and_distorted_vision": [
        "blurred vision",
        "blurry vision",
        "distorted vision",
        "vision is blurry",
        "can't see clearly",
        "cannot see clearly",
    ],

    "phlegm": [
        "phlegm",
        "mucus",
        "mucus in throat",
        "mucus while coughing",
    ],

    "throat_irritation": [
        "throat irritation",
        "irritated throat",
        "scratchy throat",
        "throat feels irritated",
    ],

    "redness_of_eyes": [
        "red eyes",
        "redness of eyes",
        "eyes are red",
    ],

    "sinus_pressure": [
        "sinus pressure",
        "pressure in sinuses",
        "face pressure",
    ],

    "runny_nose": [
        "runny nose",
        "nose running",
        "running nose",
        "nose is running",
    ],

    "congestion": [
        "congestion",
        "blocked nose",
        "stuffy nose",
        "nasal congestion",
        "nose is blocked",
    ],

    "chest_pain": [
        "chest pain",
        "pain in chest",
        "my chest hurts",
    ],

    "weakness_in_limbs": [
        "weakness in limbs",
        "weak arms",
        "weak legs",
        "limb weakness",
    ],

    "fast_heart_rate": [
        "fast heartbeat",
        "fast heart rate",
        "heart beating fast",
        "racing heart",
        "rapid heartbeat",
    ],

    "pain_during_bowel_movements": [
        "pain during bowel movement",
        "pain while passing stool",
        "pain while pooping",
        "pain during stool",
    ],

    "pain_in_anal_region": [
        "anal pain",
        "pain in anal region",
        "pain around anus",
    ],

    "bloody_stool": [
        "bloody stool",
        "blood in stool",
        "blood in poop",
    ],

    "irritation_in_anus": [
        "anal irritation",
        "irritation around anus",
        "irritation in anus",
    ],

    "neck_pain": [
        "neck pain",
        "pain in neck",
        "my neck hurts",
    ],

    "dizziness": [
        "dizziness",
        "dizzy",
        "feeling dizzy",
        "feel dizzy",
    ],

    "cramps": [
        "cramps",
        "muscle cramps",
        "stomach cramps",
    ],

    "bruising": [
        "bruising",
        "bruises",
        "easy bruising",
    ],

    "obesity": [
        "obesity",
        "obese",
    ],

    "swollen_legs": [
        "swollen legs",
        "leg swelling",
        "legs are swollen",
    ],

    "swollen_blood_vessels": [
        "swollen blood vessels",
        "enlarged blood vessels",
    ],

    "puffy_face_and_eyes": [
        "puffy face",
        "puffy eyes",
        "swollen face",
        "swollen eyes",
    ],

    "enlarged_thyroid": [
        "enlarged thyroid",
        "swollen thyroid",
        "thyroid swelling",
    ],

    "brittle_nails": [
        "brittle nails",
        "weak nails",
        "nails breaking",
    ],

    "swollen_extremeties": [
        "swollen extremities",
        "swollen hands",
        "swollen feet",
        "swollen arms",
    ],

    "excessive_hunger": [
        "excessive hunger",
        "very hungry",
        "extremely hungry",
    ],

    "drying_and_tingling_lips": [
        "dry lips",
        "tingling lips",
        "drying lips",
        "lips tingling",
    ],

    "slurred_speech": [
        "slurred speech",
        "speech is slurred",
        "difficulty speaking clearly",
    ],

    "knee_pain": [
        "knee pain",
        "pain in knee",
        "my knee hurts",
    ],

    "hip_joint_pain": [
        "hip pain",
        "hip joint pain",
        "pain in hip",
    ],

    "muscle_weakness": [
        "muscle weakness",
        "weak muscles",
        "muscles feel weak",
        "muscle feels weak",
    ],

    "stiff_neck": [
        "stiff neck",
        "neck stiffness",
        "neck feels stiff",
    ],

    "swelling_joints": [
        "swollen joints",
        "joint swelling",
        "joints are swollen",
    ],

    "movement_stiffness": [
        "movement stiffness",
        "stiffness while moving",
        "difficulty moving",
        "stiff while moving",
    ],

    "spinning_movements": [
        "spinning sensation",
        "room spinning",
        "spinning feeling",
        "everything is spinning",
    ],

    "loss_of_balance": [
        "loss of balance",
        "balance problems",
        "losing balance",
        "difficulty balancing",
    ],

    "unsteadiness": [
        "unsteady",
        "unsteadiness",
        "walking unsteadily",
        "feel unsteady",
    ],

    "weakness_of_one_body_side": [
        "weakness on one side",
        "one side feels weak",
        "weakness of one side",
        "one side is weak",
    ],

    "loss_of_smell": [
        "loss of smell",
        "cannot smell",
        "can't smell",
        "unable to smell",
    ],

    "bladder_discomfort": [
        "bladder discomfort",
        "bladder pain",
        "discomfort in bladder",
    ],

    "continuous_feel_of_urine": [
        "constant urge to urinate",
        "continuous urge to urinate",
        "always feel like urinating",
        "frequent urge to urinate",
    ],

    "passage_of_gases": [
        "gas",
        "gas in stomach",
        "passing gas",
        "excessive gas",
        "too much gas",
    ],

    "internal_itching": [
        "internal itching",
        "itching inside",
        "itching internally",
    ],

    "depression": [
        "depression",
        "feeling depressed",
        "low mood",
        "feeling very low",
    ],

    "irritability": [
        "irritable",
        "irritability",
        "easily irritated",
        "getting irritated",
    ],

    "muscle_pain": [
        "muscle pain",
        "body ache",
        "muscle aches",
        "body pain",
        "aching muscles",
    ],

    "altered_sensorium": [
        "confusion",
        "confused",
        "altered consciousness",
        "mental confusion",
    ],

    "red_spots_over_body": [
        "red spots",
        "red spots on body",
        "red spots over body",
        "spots on skin",
    ],

    "belly_pain": [
        "belly pain",
        "belly ache",
        "pain in belly",
    ],

    "abnormal_menstruation": [
        "irregular periods",
        "irregular menstruation",
        "abnormal periods",
        "periods are irregular",
    ],

    "watering_from_eyes": [
        "watery eyes",
        "watering eyes",
        "eyes watering",
        "tearing eyes",
    ],

    "increased_appetite": [
        "increased appetite",
        "very hungry",
        "increased hunger",
        "hungry all the time",
    ],

    "polyuria": [
        "frequent urination",
        "frequent urine",
        "urinating frequently",
        "passing urine frequently",
        "peeing frequently",
    ],

    "lack_of_concentration": [
        "lack of concentration",
        "difficulty concentrating",
        "poor concentration",
        "can't concentrate",
        "cannot concentrate",
    ],

    "visual_disturbances": [
        "vision problems",
        "visual disturbance",
        "vision disturbances",
        "vision problems",
    ],

    "receiving_blood_transfusion": [
        "blood transfusion",
        "received blood transfusion",
    ],

    "receiving_unsterile_injections": [
        "unsterile injections",
        "unsafe injections",
        "received unsterile injection",
    ],

    "coma": [
        "unconscious",
        "unresponsive",
    ],

    "stomach_bleeding": [
        "stomach bleeding",
        "blood from stomach",
    ],

    "distention_of_abdomen": [
        "distended abdomen",
        "abdominal distension",
        "bloated abdomen",
        "abdomen feels bloated",
        "stomach is bloated",
    ],

    "blood_in_sputum": [
        "blood in sputum",
        "blood in mucus",
        "coughing blood",
        "blood while coughing",
    ],

    "prominent_veins_on_calf": [
        "prominent veins on calf",
        "visible veins on calf",
        "veins on calf",
    ],

    "palpitations": [
        "palpitations",
        "heart pounding",
        "heart fluttering",
        "heart racing",
        "pounding heartbeat",
    ],

    "painful_walking": [
        "painful walking",
        "walking is painful",
        "pain while walking",
        "pain when walking",
    ],

    "pus_filled_pimples": [
        "pus filled pimples",
        "pus-filled pimples",
        "pimples with pus",
        "pimples filled with pus",
    ],

    "blackheads": [
        "blackheads",
        "black heads",
    ],

    "scurring": [
        "scarring",
        "scars",
        "skin scars",
    ],

    "skin_peeling": [
        "skin peeling",
        "peeling skin",
        "skin is peeling",
    ],

    "silver_like_dusting": [
        "silver like scales",
        "silvery scales",
        "silver dusting on skin",
    ],

    "small_dents_in_nails": [
        "small dents in nails",
        "nail dents",
        "dents in nails",
        "small pits in nails",
    ],

    "inflammatory_nails": [
        "inflamed nails",
        "nail inflammation",
        "inflamed fingernails",
    ],

    "blister": [
        "blister",
        "blisters",
    ],

    "red_sore_around_nose": [
        "red sore around nose",
        "sore around nose",
        "red sore near nose",
    ],

    "yellow_crust_ooze": [
        "yellow crust",
        "yellow ooze",
        "yellow crust on skin",
        "yellow discharge from skin",
    ],
}


def normalize_text(text):
    """
    Normalize patient text so that different writing styles
    can be compared more reliably.
    """

    if not text:
        return ""

    text = str(text).lower()

    # Handle common contractions.
    text = text.replace("can't", "cannot")
    text = text.replace("don't", "do not")
    text = text.replace("i'm", "i am")
    text = text.replace("i've", "i have")

    # Underscores behave like spaces.
    text = text.replace("_", " ")

    # Remove punctuation.
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove repeated whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def phrase_exists(text, phrase):
    """
    Check whether a phrase occurs as a complete phrase,
    rather than accidentally matching part of another word.
    """

    if not phrase:
        return False

    pattern = r"\b" + re.escape(phrase) + r"\b"

    return re.search(pattern, text) is not None


def extract_symptoms(text):
    """
    Extract model-compatible symptoms from natural-language
    patient input.

    Returns:
        list[str]: detected model symptom names.
    """

    normalized = normalize_text(text)

    if not normalized:
        return []

    found_symptoms = []

    for symptom in MODEL_SYMPTOMS:

        # Check the model's own feature name.
        readable_name = normalize_text(symptom)

        if phrase_exists(normalized, readable_name):
            found_symptoms.append(symptom)
            continue

        # Check natural-language aliases.
        aliases = SYMPTOM_ALIASES.get(symptom, [])

        for alias in aliases:

            normalized_alias = normalize_text(alias)

            if phrase_exists(normalized, normalized_alias):
                found_symptoms.append(symptom)
                break

    return found_symptoms


def create_feature_vector(symptoms, symptom_list=None):
    """
    Convert detected symptoms into the binary format expected
    by the trained model.
    """

    if symptom_list is None:
        symptom_list = MODEL_SYMPTOMS

    symptom_set = set(symptoms)

    return [
        1 if symptom in symptom_set else 0
        for symptom in symptom_list
    ]


def get_readable_symptom_name(symptom):
    """
    Convert a dataset-style symptom name into a
    human-readable name.
    """

    name = symptom.replace("_", " ")
    name = name.replace(".1", "")
    name = re.sub(r"\s+", " ", name).strip()

    return name.capitalize()