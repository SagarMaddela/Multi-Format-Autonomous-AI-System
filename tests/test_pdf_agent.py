import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_agent.agent import analyze_pdf_flags

if __name__ == "__main__":
    pdf_path = "samples/invoice_sample.pdf"
    result = analyze_pdf_flags(pdf_path)
    print("PDF Analysis Result:")
    print(result)
