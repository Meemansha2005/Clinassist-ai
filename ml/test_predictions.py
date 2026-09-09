from ml.prediction import predict_conditions


TEST_CASES = [
    {
        "name": "Headache and nausea",
        "text": "I have a severe headache and I feel nauseous."
    },
    {
        "name": "Cough and breathing problem",
        "text": "I have a cough, phlegm and difficulty breathing."
    },
    {
        "name": "Skin problem",
        "text": "I have an itchy skin rash and red spots on my body."
    },
    {
        "name": "Stomach problem",
        "text": "I have stomach pain, vomiting and loss of appetite."
    },
    {
        "name": "Joint problem",
        "text": "I have joint pain, muscle weakness and stiffness."
    },
]


def run_tests():

    print("=" * 60)
    print("CLINASSIST - SYMPTOM & ML PREDICTION TEST")
    print("=" * 60)

    for number, case in enumerate(TEST_CASES, start=1):

        print(f"\nTEST {number}: {case['name']}")
        print("-" * 60)

        print("Patient input:")
        print(case["text"])

        try:
            result = predict_conditions(case["text"], top_n=3)

            print("\nRecognized symptoms:")
            print(result["symptoms"])

            print("\nPossible conditions to consider:")

            if result["predictions"]:

                for prediction in result["predictions"]:
                    print(
                        f"  • {prediction['condition']}"
                        f" — Model score: "
                        f"{prediction['score']:.2%}"
                    )

            else:
                print("  No predictions available.")

        except Exception as error:

            print("\nERROR:")
            print(error)

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()