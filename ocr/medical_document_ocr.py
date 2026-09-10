import io
import re

import fitz
from PIL import Image, ImageOps, ImageFilter
import pytesseract

from nlp.text_processor import extract_symptoms


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

# Tesseract has been added to Windows PATH, so this should work
# directly from Python.
pytesseract.pytesseract.tesseract_cmd = "tesseract"


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image):
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.filter(ImageFilter.SHARPEN)
    return image


# ============================================================
# OCR FROM IMAGE
# ============================================================

def extract_text_from_image(image_bytes):

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    image = preprocess_image(image)

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


# ============================================================
# OCR FROM PDF
# ============================================================

def extract_text_from_pdf(pdf_bytes):

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    extracted_pages = []

    for page in document:

        # First try normal PDF text extraction.
        text = page.get_text("text").strip()

        if text:
            extracted_pages.append(text)
            continue

        # If the page is scanned/image-based,
        # render it and use OCR.
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )

        image_bytes = pixmap.tobytes("png")

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image = preprocess_image(image)

        ocr_text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        if ocr_text.strip():
            extracted_pages.append(
                ocr_text.strip()
            )

    document.close()

    return "\n\n".join(
        extracted_pages
    ).strip()


# ============================================================
# DOCUMENT TEXT EXTRACTION
# ============================================================

def extract_document_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):

        return extract_text_from_pdf(
            file_bytes
        )

    if file_name.endswith(
        (".png", ".jpg", ".jpeg")
    ):

        return extract_text_from_image(
            file_bytes
        )

    raise ValueError(
        "Unsupported file type. "
        "Please upload PDF, PNG, JPG or JPEG."
    )


# ============================================================
# CLEAN OCR TEXT
# ============================================================

def clean_extracted_text(text):

    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# CATEGORY EXTRACTION
# ============================================================

def extract_items_from_text(
    text,
    keywords
):

    results = []

    lines = text.splitlines()

    for line in lines:

        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        lower_line = cleaned_line.lower()

        for keyword in keywords:

            if keyword.lower() in lower_line:

                if cleaned_line not in results:

                    results.append(
                        cleaned_line
                    )

                break

    return results


# ============================================================
# MEDICATION INFORMATION
# ============================================================

def extract_medications(text):

    medication_keywords = [

        "tablet",
        "tab.",
        "tab ",
        "capsule",
        "cap.",
        "syrup",
        "injection",
        "ointment",
        "cream",
        "drops",
        "medicine",
        "medication",
        "prescribed",
        "prescription",
        "mg",
        "mcg",
        "ml",
    ]

    return extract_items_from_text(
        text,
        medication_keywords
    )


# ============================================================
# ALLERGY INFORMATION
# ============================================================

def extract_allergies(text):

    allergy_keywords = [

        "allergy",
        "allergic",
        "drug allergy",
        "allergies",
    ]

    return extract_items_from_text(
        text,
        allergy_keywords
    )


# ============================================================
# CONDITION / HISTORY INFORMATION
# ============================================================

def extract_conditions(text):

    condition_keywords = [

        "diagnosis",
        "diagnosed",
        "condition",
        "disease",
        "impression",
        "clinical impression",
        "past history",
        "medical history",
    ]

    return extract_items_from_text(
        text,
        condition_keywords
    )


# ============================================================
# FINDINGS
# ============================================================

def extract_findings(text):

    finding_keywords = [

        "finding",
        "findings",
        "result",
        "results",
        "abnormal",
        "positive",
        "negative",
        "elevated",
        "increased",
        "decreased",
        "normal",
        "impression",
        "remark",
        "remarks",
        "recommendation",
    ]

    return extract_items_from_text(
        text,
        finding_keywords
    )


# ============================================================
# AI-ASSISTED SUMMARY
# ============================================================

def generate_summary(
    text,
    symptoms,
    conditions,
    medications,
    allergies,
    findings,
):

    if not text.strip():

        return (
            "No readable text could be extracted "
            "from the uploaded document."
        )

    summary_parts = []

    if symptoms:

        summary_parts.append(
            "Symptoms mentioned: "
            + ", ".join(symptoms)
            + "."
        )

    if conditions:

        summary_parts.append(
            "Previous conditions or clinical "
            "impressions mentioned in the document "
            "were identified."
        )

    if medications:

        summary_parts.append(
            "Medication-related information was "
            "identified in the uploaded record."
        )

    if allergies:

        summary_parts.append(
            "Allergy-related information was "
            "identified in the uploaded record."
        )

    if findings:

        summary_parts.append(
            "The document contains investigation "
            "results or clinical findings that "
            "should be reviewed by the healthcare "
            "professional."
        )

    if not summary_parts:

        summary_parts.append(
            "The document was successfully processed, "
            "but no specific medical categories could "
            "be confidently extracted from the "
            "available text."
        )

    summary_parts.append(
        "The extracted information should be "
        "verified against the original medical "
        "document."
    )

    return " ".join(
        summary_parts
    )


# ============================================================
# COMPLETE DOCUMENT ANALYSIS
# ============================================================

def analyze_medical_document(
    uploaded_file,
    symptom_list_path=None,
):

    raw_text = extract_document_text(
        uploaded_file
    )

    text = clean_extracted_text(
        raw_text
    )

    if not text:

        return {

            "text": "",

            "summary":
                "No readable text could be "
                "extracted from the uploaded document.",

            "symptoms": [],
            "conditions": [],
            "medications": [],
            "allergies": [],
            "findings": [],
        }

    symptoms = []

    if symptom_list_path is not None:

        try:

            import joblib

            symptom_list = joblib.load(
                symptom_list_path
            )

            symptoms = extract_symptoms(
                text,
                symptom_list
            )

        except Exception:

            symptoms = []

    conditions = extract_conditions(
        text
    )

    medications = extract_medications(
        text
    )

    allergies = extract_allergies(
        text
    )

    findings = extract_findings(
        text
    )

    summary = generate_summary(
        text,
        symptoms,
        conditions,
        medications,
        allergies,
        findings,
    )

    return {

        "text": text,

        "summary": summary,

        "symptoms": symptoms,

        "conditions": conditions,

        "medications": medications,

        "allergies": allergies,

        "findings": findings,
    }