# language/language_manager.py

from language.translations import get_translation, TRANSLATIONS


SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())


def translate(language, key):
    """
    Get translated text for a key.
    """

    return get_translation(language, key)


def get_supported_languages():
    """
    Return all supported languages.
    """

    return SUPPORTED_LANGUAGES


if __name__ == "__main__":

    print("=================================")
    print("CLINASSIST LANGUAGE TEST")
    print("=================================")

    for language in SUPPORTED_LANGUAGES:

        print(f"\nLanguage: {language}")

        print(
            "Patient Information:",
            translate(language, "patient_information")
        )

        print(
            "Presenting Complaint:",
            translate(language, "presenting_complaint")
        )

        print(
            "Possible Conditions:",
            translate(language, "possible_conditions")
        )

        print(
            "Final Report:",
            translate(language, "final_report")
        )

    print("\n=================================")
    print("LANGUAGE TEST COMPLETED")
    print("=================================")