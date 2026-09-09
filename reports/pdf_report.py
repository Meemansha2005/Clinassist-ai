from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def export_report_to_pdf(report, output_path):
    """
    Convert a ClinAssist clinical report dictionary into a PDF file.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=15,
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=10,
        spaceAfter=7,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=14,
        spaceAfter=4,
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    )

    story = []

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    story.append(Paragraph("CLINASSIST", title_style))
    story.append(
        Paragraph(
            "Clinical Assessment Report",
            subtitle_style,
        )
    )

    generated = report.get(
        "generated_at",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    story.append(
        Paragraph(
            f"<b>Generated:</b> {generated}",
            normal_style,
        )
    )

    story.append(Spacer(1, 5))

    # ---------------------------------------------------------
    # PATIENT INFORMATION
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "1. PATIENT INFORMATION",
            heading_style,
        )
    )

    patient = report.get("patient", {})

    patient_data = [
        ["Patient ID", str(patient.get("id", patient.get("patient_id", "N/A")))],
        ["Name", str(patient.get("name", "N/A"))],
        ["Age", str(patient.get("age", "N/A"))],
        ["Gender", str(patient.get("gender", "N/A"))],
    ]

    patient_table = Table(
        patient_data,
        colWidths=[45 * mm, 120 * mm],
    )

    patient_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(patient_table)

    # ---------------------------------------------------------
    # CLINICAL HISTORY
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "2. CLINICAL HISTORY",
            heading_style,
        )
    )

    history_data = [
        [
            "Presenting Complaint",
            str(patient.get("complaint", "N/A")),
        ],
        [
            "Duration",
            str(patient.get("duration", "N/A")),
        ],
        [
            "Severity",
            str(patient.get("severity", "N/A")),
        ],
        [
            "Additional Symptoms",
            str(patient.get("additional_symptoms", "N/A")),
        ],
        [
            "Past History",
            str(patient.get("past_history", "N/A")),
        ],
        [
            "Medications",
            str(patient.get("medications", "N/A")),
        ],
        [
            "Allergies",
            str(patient.get("allergies", "N/A")),
        ],
    ]

    history_table = Table(
        history_data,
        colWidths=[50 * mm, 115 * mm],
    )

    history_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(history_table)

    # ---------------------------------------------------------
    # AI ANALYSIS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "3. AI-ASSISTED ANALYSIS",
            heading_style,
        )
    )

    analysis = report.get("analysis", {})

    detected_symptoms = analysis.get("symptoms", [])

    story.append(
        Paragraph(
            "<b>Detected Symptoms</b>",
            normal_style,
        )
    )

    if detected_symptoms:
        for symptom in detected_symptoms:
            story.append(
                Paragraph(
                    f"- {symptom}",
                    normal_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "No symptoms were automatically detected.",
                normal_style,
            )
        )

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "<b>Possible Conditions to Consider</b>",
            normal_style,
        )
    )

    predictions = analysis.get("predictions", [])

    if predictions:
        prediction_data = [
            ["Rank", "Condition", "Model Score"]
        ]

        for index, prediction in enumerate(predictions, start=1):
            condition = prediction.get(
                "condition",
                prediction.get("name", "Unknown"),
            )

            score = prediction.get(
                "score",
                prediction.get("probability", 0),
            )

            try:
                score_text = f"{float(score):.2f}%"
            except (TypeError, ValueError):
                score_text = str(score)

            prediction_data.append(
                [
                    str(index),
                    str(condition),
                    score_text,
                ]
            )

        prediction_table = Table(
            prediction_data,
            colWidths=[20 * mm, 105 * mm, 40 * mm],
        )

        prediction_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (-1, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(prediction_table)

    else:
        story.append(
            Paragraph(
                "No model predictions available.",
                normal_style,
            )
        )

    # ---------------------------------------------------------
    # URGENCY REVIEW
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "4. URGENCY REVIEW",
            heading_style,
        )
    )

    urgency = analysis.get("urgency", {})

    urgent = urgency.get("urgent", False)
    flags = urgency.get("flags", [])

    if urgent:
        story.append(
            Paragraph(
                "<b>Potential urgency indicators detected.</b>",
                normal_style,
            )
        )

        for flag in flags:
            story.append(
                Paragraph(
                    f"- {flag}",
                    normal_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "No predefined urgency indicators detected.",
                normal_style,
            )
        )

    message = urgency.get("message")

    if message:
        story.append(
            Spacer(1, 3)
        )
        story.append(
            Paragraph(
                f"<b>Review message:</b> {message}",
                normal_style,
            )
        )

    # ---------------------------------------------------------
    # DOCTOR ASSESSMENT
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "5. DOCTOR ASSESSMENT",
            heading_style,
        )
    )

    assessment = report.get("assessment")

    if assessment:
        assessment_data = [
            [
                "Doctor",
                str(assessment.get("doctor_name", "N/A")),
            ],
            [
                "Confirmed Condition",
                str(
                    assessment.get(
                        "confirmed_condition",
                        "Not specified",
                    )
                ),
            ],
            [
                "Final Assessment",
                str(
                    assessment.get(
                        "final_assessment",
                        "N/A",
                    )
                ),
            ],
            [
                "Doctor Notes",
                str(
                    assessment.get(
                        "doctor_notes",
                        "N/A",
                    )
                ),
            ],
            [
                "Follow-up",
                str(
                    assessment.get(
                        "follow_up",
                        "N/A",
                    )
                ),
            ],
        ]

        assessment_table = Table(
            assessment_data,
            colWidths=[50 * mm, 115 * mm],
        )

        assessment_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(assessment_table)

    else:
        story.append(
            Paragraph(
                "Doctor assessment has not been completed.",
                normal_style,
            )
        )

    # ---------------------------------------------------------
    # DISCLAIMER
    # ---------------------------------------------------------

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "IMPORTANT",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "AI-generated information is intended only to support "
            "clinical review and does not replace professional "
            "clinical judgment, diagnosis, or treatment decisions.",
            small_style,
        )
    )

    # ---------------------------------------------------------
    # BUILD PDF
    # ---------------------------------------------------------

    document.build(story)

    return output_path


# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    sample_report = {
        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "patient": {
            "id": 1,
            "name": "Test Patient",
            "age": 25,
            "gender": "Female",
            "complaint": "Headache",
            "duration": "2 days",
            "severity": "Moderate",
            "additional_symptoms": "Nausea and fatigue",
            "past_history": "None",
            "medications": "None",
            "allergies": "None",
        },

        "analysis": {
            "symptoms": [
                "headache",
                "nausea",
                "fatigue",
            ],

            "predictions": [
                {
                    "condition": "Example Condition 1",
                    "score": 35.50,
                },
                {
                    "condition": "Example Condition 2",
                    "score": 22.30,
                },
                {
                    "condition": "Example Condition 3",
                    "score": 12.80,
                },
            ],

            "urgency": {
                "urgent": False,
                "flags": [],
                "message": "No predefined urgency indicators detected.",
            },
        },

        "assessment": {
            "doctor_name": "Dr. Test",
            "confirmed_condition": "Example Condition 1",
            "final_assessment": (
                "Patient history reviewed and clinical "
                "assessment completed."
            ),
            "doctor_notes": (
                "Doctor reviewed the patient's reported symptoms."
            ),
            "follow_up": (
                "Follow-up according to clinical assessment."
            ),
        },
    }

    output_file = (
        Path(__file__).parent
        / "output"
        / "clinassist_test_report.pdf"
    )

    export_report_to_pdf(
        sample_report,
        output_file,
    )

    print("=================================")
    print("CLINASSIST PDF REPORT TEST")
    print("=================================")
    print()
    print("PDF generated successfully!")
    print(f"Location: {output_file}")
    print()
    print("PDF REPORT TEST COMPLETED")