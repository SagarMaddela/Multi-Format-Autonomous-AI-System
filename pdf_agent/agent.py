# multi-agent-system/pdf_agent/agent.py
import fitz  # PyMuPDF
import re
import os
import json
import logging
from langchain.prompts import PromptTemplate
from utils.llm_utils import get_llm  # Import shared LLM
from memory.store import SharedMemory

os.makedirs("logs", exist_ok=True)

# Setup logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/action.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

pdf_prompt = PromptTemplate.from_template("""
You are an expert document analysis agent specializing in PDF content review.

Your task is to analyze the provided extracted text from a PDF and identify any relevant flags, such as:
- Invoices with a total amount
- Mentions of policies, regulations, or compliance terms (e.g., GDPR, HIPAA, FDA)
- Any other notable risks or compliance issues

For each flag you identify, provide a structured JSON response with the following fields:
- "flag": A concise description of the issue or observation
- "page": The page number(s) where the flag was found (use an integer or a list of integers)
- "confidence": A confidence score between 0 and 1 indicating your certainty
- "explanation": A brief explanation of why this flag was raised

Respond ONLY with a valid JSON object in the following format:

{{
    "flags": [
        {{
            "flag": "description of flag",
            "page": page_number,
            "confidence": confidence_score,
            "explanation": "detailed explanation"
        }}
    ]
}}

Extracted Text:
{text}
""")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        return full_text
    except Exception as e:
        logger.error("Error extracting PDF text", exc_info=True)
        return ""

def extract_valid_json(raw: str) -> dict:
    """Extract the first valid JSON object from a string, even if surrounded by extra text."""
    import json

    # Find the first '{' and last '}' to extract the largest JSON block
    start = raw.find('{')
    end = raw.rfind('}')
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response")

    raw_json = raw[start:end+1]

    # Fix common errors like page: 2-3 → page: [2, 3]
    raw_json = re.sub(r'(\d+)\s*-\s*(\d+)', r'[\1, \2]', raw_json)

    try:
        return json.loads(raw_json)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}\nExtracted: {raw_json}")

def analyze_pdf_flags(pdf_path: str) -> dict:
    """Extract text from PDF and analyze it using the LLM."""
    # try:
    # text = extract_text_from_pdf(pdf_path)
    # if not text:
    #     return {"flags": [], "error": "No text extracted from PDF."}

    safe_text = pdf_path[:3000]
    prompt = pdf_prompt.format(text=safe_text)

    logger.info("Sending PDF text to LLM for flag detection...")
    llm = get_llm()
    if not llm:
        raise ValueError("LLM is not initialized. Please check your configuration.")
    raw_response = llm.invoke(prompt)
    logger.info(f"LLM Response: {raw_response}")

    result = extract_valid_json(raw_response)
    # Save to SharedMemory
    memory = SharedMemory()
    trace_id = memory.save_trace(result)
    result["trace_id"] = trace_id
    result["agent"] = "PDFAgent"
    
    return result

    # except Exception as e:
    #     logger.error("PDF analysis failed.", exc_info=True)
    #     return {"flags": [], "error": str(e)}
