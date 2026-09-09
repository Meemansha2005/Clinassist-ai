import sqlite3
from pathlib import Path


# ---------------------------------------------------------
# DATABASE LOCATION
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "clinassist.db"


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    """Create and return a SQLite database connection."""
    return sqlite3.connect(DATABASE_PATH)


# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------

def initialize_database():
    """Create ClinAssist tables if they do not already exist."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            complaint TEXT,
            duration TEXT,
            severity TEXT,
            additional_symptoms TEXT,
            past_history TEXT,
            medications TEXT,
            allergies TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            urgency TEXT,
            ai_suggestions TEXT,
            doctor_assessment TEXT,
            final_diagnosis TEXT,
            treatment_plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (patient_id)
            REFERENCES patients(id)
        )
    """)

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# SAVE PATIENT
# ---------------------------------------------------------

def save_patient(patient):
    """Save a patient and return the generated patient ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO patients (
            name,
            age,
            gender,
            complaint,
            duration,
            severity,
            additional_symptoms,
            past_history,
            medications,
            allergies
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient.get("name"),
        patient.get("age"),
        patient.get("gender"),
        patient.get("complaint"),
        patient.get("duration"),
        patient.get("severity"),
        patient.get("additional_symptoms"),
        patient.get("past_history"),
        patient.get("medications"),
        patient.get("allergies"),
    ))

    patient_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return patient_id


# ---------------------------------------------------------
# SAVE DOCTOR ASSESSMENT
# ---------------------------------------------------------

def save_assessment(
    patient_id,
    urgency,
    ai_suggestions,
    doctor_assessment,
    final_diagnosis,
    treatment_plan
):
    """Save a doctor's assessment for a patient."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO assessments (
            patient_id,
            urgency,
            ai_suggestions,
            doctor_assessment,
            final_diagnosis,
            treatment_plan
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        urgency,
        ai_suggestions,
        doctor_assessment,
        final_diagnosis,
        treatment_plan,
    ))

    assessment_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return assessment_id


# ---------------------------------------------------------
# GET PATIENT
# ---------------------------------------------------------

def get_patient(patient_id):
    """Retrieve one patient by ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    columns = [
        "id",
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
        "created_at",
    ]

    return dict(zip(columns, row))


# ---------------------------------------------------------
# GET ALL PATIENTS
# ---------------------------------------------------------

def get_all_patients():
    """Retrieve all saved patients."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM patients
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    columns = [
        "id",
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
        "created_at",
    ]

    return [
        dict(zip(columns, row))
        for row in rows
    ]


# ---------------------------------------------------------
# GET PATIENT ASSESSMENTS
# ---------------------------------------------------------

def get_patient_assessments(patient_id):
    """Retrieve all assessments belonging to a patient."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM assessments
        WHERE patient_id = ?
        ORDER BY created_at DESC
    """, (patient_id,))

    rows = cursor.fetchall()

    connection.close()

    columns = [
        "id",
        "patient_id",
        "urgency",
        "ai_suggestions",
        "doctor_assessment",
        "final_diagnosis",
        "treatment_plan",
        "created_at",
    ]

    return [
        dict(zip(columns, row))
        for row in rows
    ]


# ---------------------------------------------------------
# TEST DATABASE
# ---------------------------------------------------------

if __name__ == "__main__":

    print("Initializing ClinAssist database...")

    initialize_database()

    print("Database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")
    # --------------------------------------------------
# DOCTOR ASSESSMENT
# --------------------------------------------------

def save_doctor_assessment(
    patient_id,
    assessment
):
    """
    Save a doctor's assessment for a patient.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS doctor_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            confirmed_condition TEXT,
            final_assessment TEXT NOT NULL,
            doctor_notes TEXT,
            follow_up TEXT,
            assessed_at TEXT NOT NULL,
            FOREIGN KEY (patient_id)
                REFERENCES patients(id)
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO doctor_assessments (
            patient_id,
            doctor_name,
            confirmed_condition,
            final_assessment,
            doctor_notes,
            follow_up,
            assessed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            assessment.get("doctor_name", ""),
            assessment.get("confirmed_condition", ""),
            assessment.get("final_assessment", ""),
            assessment.get("doctor_notes", ""),
            assessment.get("follow_up", ""),
            assessment.get("assessed_at", ""),
        )
    )

    assessment_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return assessment_id


# --------------------------------------------------
# GET DOCTOR ASSESSMENT
# --------------------------------------------------

def get_doctor_assessment(patient_id):
    """
    Retrieve the latest doctor assessment
    for a patient.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            patient_id,
            doctor_name,
            confirmed_condition,
            final_assessment,
            doctor_notes,
            follow_up,
            assessed_at
        FROM doctor_assessments
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "patient_id": row[1],
        "doctor_name": row[2],
        "confirmed_condition": row[3],
        "final_assessment": row[4],
        "doctor_notes": row[5],
        "follow_up": row[6],
        "assessed_at": row[7],
    }