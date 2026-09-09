# voice/speech_to_text.py

import speech_recognition as sr


def speech_to_text(language="en-IN"):
    """
    Capture speech from the microphone and convert it to text.

    Parameters:
        language (str): Speech recognition language code.
                         en-IN = Indian English
                         hi-IN = Hindi

    Returns:
        str: Recognized text.
    """

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            print("=================================")
            print("CLINASSIST VOICE INPUT")
            print("=================================")

            print(f"Recognition language: {language}")

            print("Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            print("Listening...")
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=15
            )

        print("Processing speech...")

        text = recognizer.recognize_google(
            audio,
            language=language
        )

        return text

    except sr.WaitTimeoutError:
        return "No speech detected."

    except sr.UnknownValueError:
        return "Speech could not be understood."

    except sr.RequestError:
        return "Speech recognition service is unavailable."

    except Exception as error:
        return f"Voice input error: {error}"


def is_successful(text):
    """
    Check whether speech recognition returned usable text.
    """

    if not text:
        return False

    error_messages = [
        "No speech detected.",
        "Speech could not be understood.",
        "Speech recognition service is unavailable.",
    ]

    return text not in error_messages


def get_voice_language(language):
    language = language.strip().lower()

    language_codes = {
        "english": "en-IN",
        "hindi": "hi-IN",
    }

    return language_codes.get(language, "en-IN")


if __name__ == "__main__":

    print("\nStarting ClinAssist voice test...\n")

    selected_language = input(
        "Enter language (English/Hindi): "
    ).strip()

    voice_language = get_voice_language(selected_language)

    result = speech_to_text(voice_language)

    print("\nRecognized Text:")
    print(result)

    if is_successful(result):
        print("\n✅ VOICE INPUT TEST SUCCESSFUL")
    else:
        print("\n⚠️ VOICE INPUT TEST DID NOT RECEIVE USABLE SPEECH")