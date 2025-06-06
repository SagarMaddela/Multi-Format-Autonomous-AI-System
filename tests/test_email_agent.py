import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_agent.agent import analyze_email

def test_email_analysis():
    email = """
    Hello Support,

    I’ve been charged twice for my last invoice and no one is responding to my previous tickets.
    I need this resolved immediately or I will escalate the issue.

    Regards,
    A very angry customer
    """

    result = analyze_email(email)
    print(result)

if __name__ == "__main__":
    test_email_analysis()
