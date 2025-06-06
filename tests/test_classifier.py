
# tests/test_classifier.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifier_agent.agent import classify_input

def test_classifier():
    sample_text = """
    Dear Support,

    I am unable to access my account even after resetting the password.
    Please assist urgently as it’s affecting my work.

    Regards,
    John Doe
    """
    result = classify_input(sample_text)
    print(result)

if __name__ == "__main__":
    test_classifier()
