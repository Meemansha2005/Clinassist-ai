# reports/pdf_report.py

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    SimpleDocTemplate,
    KeepTogether,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _safe_text(value, default="N/A"):
    """Convert any value into safe text for the PDF."""
    if value is None:
        return default

    if isinstance(value, (list, tuple, set)):
        if not value:
            return default
        return ", ".join(_safe_text(item, "") for item in value)

    if isinstance(value, dict):
        if not value:
            return default
        return ", ".join(
            f"{key}: {_safe_text(val, '')}"
            for key, val in value.items()
        )

    text = str(value).strip()

    if not text or text.lower() in {"none", "null", "nan"}:
        return default

    return text


def _get_first(data, keys, default="N/A"):
    """Return the first meaningful value found for the supplied keys."""
    if not isinstance(data, dict):
        return default

    for key in keys:
        if key in data:
            value = data.get(key)

            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                continue

            if isinstance(value, (list, tuple, set, dict)) and not value:
                continue

            return value

    return default


def _paragraph_text(value, default="N/A"):
    """Escape text before sending it to ReportLab Paragraph."""
    return escape(_safe_text(value, default))


def _normalize_score(score):
    """Convert model score into a readable percentage."""
    try:
        score = float(score)

        # Model probabilities are normally 0-1.
        if 0 <= score <= 1:
            score *= 100

        return f"{score:.2f}%"

    except (TypeError, ValueError):
        return "N/A"


def _normalize_prediction(prediction):
    """
    Convert different prediction formats into:
    (condition, probability)
    """

    # Dictionary format
    if isinstance(prediction, dict):

        condition = _get_first(
            prediction,
            [
                "condition",
                "disease",
                "name",
                "label",
                "Disease",
                "Condition",
            ],
            "N/A",
        )

        probability = _get_first(
            prediction,
            [
                "probability",
                "confidence",
                "score",
                "Probability",
                "Confidence",
            ],
            None,
        )

        return (
            _safe_text(condition),
            _normalize_score(probability),
        )

    # Tuple/list format
    if isinstance(prediction, (tuple, list)):

        if len(prediction) >= 2:
            return (
                _safe_text(prediction[0]),
                _normalize_score(prediction[1]),
            )

        if len(prediction) == 1:
            return (
                _safe_text(prediction[0]),
                "N/A",
            )

    # Plain string
    return (
        _safe_text(prediction),
        "N/A",
    )


def _normalize_list(value):
    """Convert symptoms/flags into a clean list."""
    if value is None:
        return []

    if isinstance(value, str):

        if not value.strip():
            return []

        # Handle comma-separated strings.
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    if isinstance(value, (list, tuple, set)):
        return [
            _safe_text(item, "")
            for item in value
            if _safe_text(item, "")
        ]

    return [_safe_text(value)]


# ============================================================
# REPORT SCHEMA NORMALIZATION
# ============================================================

def _normalize_report(report):
    """
    Supports both report formats used by ClinAssist.

    New/legacy PDF format:
        {
            "patient": {...},
            "analysis": {...},
            "assessment": {...}
        }

    Clinical report format:
        {
            "patient_information": {...},
            "clinical_history": {...},
            "ai_analysis": {...},
            "urgency_review": {...},
            "doctor_assessment": {...}
        }
    """

    if not isinstance(report, dict):
        report = {}

    # --------------------------------------------------------
    # PATIENT
    # --------------------------------------------------------

    patient = report.get("patient")

    if not isinstance(patient, dict) or not patient:
        patient = report.get("patient_information", {})

    if not isinstance(patient, dict):
        patient = {}

    # --------------------------------------------------------
    # CLINICAL HISTORY
    # --------------------------------------------------------

    history = report.get("clinical_history", {})

    if not isinstance(history, dict):
        history = {}

    # Some reports keep clinical history directly inside patient.
    # Merge only missing fields.
    for key, value in patient.items():
        if key not in history:
            history[key] = value

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    analysis = report.get("analysis")

    if not isinstance(analysis, dict) or not analysis:
        analysis = report.get("ai_analysis", {})

    if not isinstance(analysis, dict):
        analysis = {}

    # --------------------------------------------------------
    # URGENCY
    # --------------------------------------------------------

    urgency = report.get("urgency_review")

    if urgency is None:
        urgency = analysis.get("urgency", {})

    if urgency is None:
        urgency = {}

    # --------------------------------------------------------
    # ASSESSMENT
    # --------------------------------------------------------

    assessment = report.get("assessment")

    if assessment is None:
        assessment = report.get("doctor_assessment")

    return {
        "title": report.get(
            "title",
            "ClinAssist - Clinical Decision Support Report",
        ),
        "generated_at": report.get("generated_at", ""),
        "patient": patient,
        "history": history,
        "analysis": analysis,
        "urgency": urgency,
        "assessment": assessment,
        "disclaimer": report.get(
            "disclaimer",
            "This report is an AI-assisted clinical decision-support "
            "document. It does not replace professional medical judgment.",
        ),
    }


# ============================================================
# PDF EXPORT
# ============================================================

def export_report_to_pdf(report, output_path):
    """
    Generate a professional ClinAssist clinical report PDF.

    Parameters
    ----------
    report : dict
        Clinical report dictionary.

    output_path : str or Path
        Destination path for the PDF.

    Returns
    -------
    str
        Generated PDF path.
    """

    normalized = _normalize_report(report)

    patient = normalized["patient"]
    history = normalized["history"]
    analysis = normalized["analysis"]
    urgency = normalized["urgency"]
    assessment = normalized["assessment"]

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # DOCUMENT
    # ========================================================

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="ClinAssist Clinical Report",
        author="ClinAssist AI",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ClinAssistTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=5 * mm,
    )

    subtitle_style = ParagraphStyle(
        "ClinAssistSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        textColor=colors.grey,
        spaceAfter=7 * mm,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=5 * mm,
        spaceAfter=3 * mm,
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
        spaceAfter=2 * mm,
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.grey,
        spaceBefore=5 * mm,
    )

    story = []

    # ========================================================
    # HEADER
    # ========================================================

    story.append(
        Paragraph(
            _paragraph_text(
                normalized["title"],
                "ClinAssist - Clinical Decision Support Report",
            ),
            title_style,
        )
    )

    generated_at = normalized["generated_at"]

    if generated_at:
        story.append(
            Paragraph(
                f"Generated: {_paragraph_text(generated_at)}",
                subtitle_style,
            )
        )

    # ========================================================
    # PATIENT INFORMATION
    # ========================================================

    story.append(
        Paragraph(
            "1. Patient Information",
            section_style,
        )
    )

    patient_id = _get_first(
        patient,
        [
            "id",
            "patient_id",
            "Patient ID",
        ],
    )

    name = _get_first(
        patient,
        [
            "name",
            "patient_name",
            "Name",
            "Patient Name",
        ],
    )

    age = _get_first(
        patient,
        [
            "age",
            "Age",
        ],
    )

    gender = _get_first(
        patient,
        [
            "gender",
            "sex",
            "Gender",
            "Sex",
        ],
    )

    patient_table_data = [
        [
            Paragraph("<b>Patient ID</b>", small_style),
            Paragraph(_paragraph_text(patient_id), small_style),
        ],
        [
            Paragraph("<b>Name</b>", small_style),
            Paragraph(_paragraph_text(name), small_style),
        ],
        [
            Paragraph("<b>Age</b>", small_style),
            Paragraph(_paragraph_text(age), small_style),
        ],
        [
            Paragraph("<b>Gender</b>", small_style),
            Paragraph(_paragraph_text(gender), small_style),
        ],
    ]

    patient_table = Table(
        patient_table_data,
        colWidths=[45 * mm, 125 * mm],
    )

    patient_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(patient_table)

    # ========================================================
    # CLINICAL HISTORY
    # ========================================================

    story.append(
        Paragraph(
            "2. Clinical History",
            section_style,
        )
    )

    presenting_complaint = _get_first(
        history,
        [
            "presenting_complaint",
            "complaint",
            "chief_complaint",
            "Presenting Complaint",
            "Complaint",
        ],
    )

    duration = _get_first(
        history,
        [
            "duration",
            "symptom_duration",
            "Duration",
        ],
    )

    severity = _get_first(
        history,
        [
            "severity",
            "Severity",
        ],
    )

    additional_symptoms = _get_first(
        history,
        [
            "additional_symptoms",
            "Additional Symptoms",
        ],
    )

    past_history = _get_first(
        history,
        [
            "past_history",
            "medical_history",
            "past_medical_history",
            "Past History",
        ],
    )

    medications = _get_first(
        history,
        [
            "medications",
            "current_medications",
            "Medication",
            "Medications",
        ],
    )

    allergies = _get_first(
        history,
        [
            "allergies",
            "drug_allergies",
            "Allergies",
        ],
    )

    history_rows = [
        [
            Paragraph("<b>Presenting Complaint</b>", small_style),
            Paragraph(
                _paragraph_text(presenting_complaint),
                small_style,
            ),
        ],
        [
            Paragraph("<b>Duration</b>", small_style),
            Paragraph(
                _paragraph_text(duration),
                small_style,
            ),
        ],
        [
            Paragraph("<b>Severity</b>", small_style),
            Paragraph(
                _paragraph_text(severity),
                small_style,
            ),
        ],
        [
            Paragraph("<b>Additional Symptoms</b>", small_style),
            Paragraph(
                _paragraph_text(additional_symptoms),
                small_style,
            ),
        ],
        [
            Paragraph("<b>Past Medical History</b>", small_style),
            Paragraph(
                _paragraph_text(past_history),
                small_style,
            ),
        ],
        [
            Paragraph("<b>Medications</b>", small_style),
            Paragraph(
                _paragraph_text(medications),
                small_style,
            ),
        ],
        [
            Paragraph("<b>Allergies</b>", small_style),
            Paragraph(
                _paragraph_text(allergies),
                small_style,
            ),
        ],
    ]

    # --------------------------------------------------------
    # Adaptive questions
    # --------------------------------------------------------

    adaptive = history.get("adaptive_questions", {})

    if not isinstance(adaptive, dict):
        adaptive = {}

    adaptive_field_map = [
        ("pain_location", "Pain Location"),
        ("head_associated", "Associated Head Symptoms"),
        ("cough_type", "Cough Type"),
        ("breathing", "Breathing"),
        ("food_relation", "Relation to Food"),
        ("vomiting", "Vomiting"),
        ("skin_appearance", "Skin Appearance"),
        ("skin_duration", "Skin Duration"),
        ("additional_details", "Additional Details"),
    ]

    for key, label in adaptive_field_map:

        value = adaptive.get(key)

        if value is None:
            value = history.get(key)

        if value is None:
            continue

        if isinstance(value, str) and not value.strip():
            continue

        history_rows.append(
            [
                Paragraph(
                    f"<b>{escape(label)}</b>",
                    small_style,
                ),
                Paragraph(
                    _paragraph_text(value),
                    small_style,
                ),
            ]
        )

    history_table = Table(
        history_rows,
        colWidths=[55 * mm, 115 * mm],
    )

    history_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(history_table)

    # ========================================================
    # AI ANALYSIS
    # ========================================================

    story.append(
        Paragraph(
            "3. AI-Assisted Analysis",
            section_style,
        )
    )

    detected_symptoms = _get_first(
        analysis,
        [
            "symptoms",
            "detected_symptoms",
            "Detected Symptoms",
        ],
        [],
    )

    detected_symptoms = _normalize_list(detected_symptoms)

    if detected_symptoms:

        symptom_text = ", ".join(
            escape(symptom)
            for symptom in detected_symptoms
        )

    else:
        symptom_text = "No symptoms detected"

    story.append(
        Paragraph(
            f"<b>Detected Symptoms:</b> {symptom_text}",
            normal_style,
        )
    )

    # ========================================================
    # POSSIBLE CONDITIONS
    # ========================================================

    predictions = _get_first(
        analysis,
        [
            "predictions",
            "possible_conditions",
            "Possible Conditions",
        ],
        [],
    )

    if predictions is None:
        predictions = []

    if not isinstance(predictions, (list, tuple)):
        predictions = [predictions]

    prediction_rows = [
        [
            Paragraph("<b>Possible Condition</b>", small_style),
            Paragraph("<b>Model Score</b>", small_style),
        ]
    ]

    for prediction in predictions:

        condition, probability = _normalize_prediction(
            prediction
        )

        prediction_rows.append(
            [
                Paragraph(
                    escape(condition),
                    small_style,
                ),
                Paragraph(
                    escape(probability),
                    small_style,
                ),
            ]
        )

    if len(prediction_rows) == 1:
        prediction_rows.append(
            [
                Paragraph(
                    "No model predictions available",
                    small_style,
                ),
                Paragraph(
                    "N/A",
                    small_style,
                ),
            ]
        )

    prediction_table = Table(
        prediction_rows,
        colWidths=[125 * mm, 45 * mm],
    )

    prediction_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(prediction_table)

    # ========================================================
    # URGENCY REVIEW
    # ========================================================

    story.append(
        Paragraph(
            "4. Urgency Review",
            section_style,
        )
    )

    urgent = False
    urgency_flags = []
    urgency_message = ""

    if isinstance(urgency, dict):

        urgent = bool(
            urgency.get(
                "urgent",
                urgency.get("is_urgent", False),
            )
        )

        urgency_flags = _normalize_list(
            urgency.get(
                "flags",
                urgency.get("urgency_flags", []),
            )
        )

        urgency_message = _safe_text(
            urgency.get(
                "message",
                urgency.get("recommendation", ""),
            ),
            "",
        )

    elif isinstance(urgency, str):

        urgency_message = urgency

    urgency_status = "Urgent review recommended" if urgent else "No urgent flag identified"

    story.append(
        Paragraph(
            f"<b>Status:</b> {escape(urgency_status)}",
            normal_style,
        )
    )

    if urgency_flags:

        story.append(
            Paragraph(
                "<b>Flags:</b> "
                + ", ".join(
                    escape(flag)
                    for flag in urgency_flags
                ),
                normal_style,
            )
        )

    if urgency_message:

        story.append(
            Paragraph(
                f"<b>Message:</b> {escape(urgency_message)}",
                normal_style,
            )
        )

    # ========================================================
    # DOCTOR ASSESSMENT
    # ========================================================

    story.append(
        Paragraph(
            "5. Doctor Assessment",
            section_style,
        )
    )

    if isinstance(assessment, dict):

        assessment_text = _get_first(
            assessment,
            [
                "assessment",
                "clinical_assessment",
                "doctor_assessment",
                "Assessment",
                "Clinical Assessment",
            ],
            "",
        )

        notes = _get_first(
            assessment,
            [
                "notes",
                "doctor_notes",
                "additional_notes",
                "Notes",
                "Doctor Notes",
            ],
            "",
        )

        impression = _get_first(
            assessment,
            [
                "impression",
                "clinical_impression",
                "Impression",
            ],
            "",
        )

        if assessment_text:
            story.append(
                Paragraph(
                    f"<b>Assessment:</b> "
                    f"{escape(_safe_text(assessment_text, 'N/A'))}",
                    normal_style,
                )
            )

        if impression:
            story.append(
                Paragraph(
                    f"<b>Clinical Impression:</b> "
                    f"{escape(_safe_text(impression, 'N/A'))}",
                    normal_style,
                )
            )

        if notes:
            story.append(
                Paragraph(
                    f"<b>Notes:</b> "
                    f"{escape(_safe_text(notes, 'N/A'))}",
                    normal_style,
                )
            )

        if not assessment_text and not impression and not notes:

            story.append(
                Paragraph(
                    "Doctor assessment not yet recorded.",
                    normal_style,
                )
            )

    elif assessment:

        story.append(
            Paragraph(
                escape(_safe_text(assessment)),
                normal_style,
            )
        )

    else:

        story.append(
            Paragraph(
                "Doctor assessment not yet recorded.",
                normal_style,
            )
        )

    # ========================================================
    # DISCLAIMER
    # ========================================================

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            f"<b>Important:</b> "
            f"{escape(_safe_text(normalized['disclaimer']))}",
            disclaimer_style,
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(story)

    return str(output_path)