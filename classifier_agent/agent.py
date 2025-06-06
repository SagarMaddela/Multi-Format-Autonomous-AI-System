# classifier_agent/agent.py

import os
import re
import json
from langchain.prompts import PromptTemplate
from utils.llm_utils import llm  
import logging
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

# Prepare a prompt template for classification
prompt_template = PromptTemplate.from_template("""
You are a business content classification agent.

Given the following input text, identify and classify:
- format: email / pdf / json
- intent: invoice / support / complaint / lead / query / notification / unknown
- confidence: (between 0.0 and 1.0)

Respond in the following JSON format:
{{
  "format": "...",
  "intent": "...",
  "confidence": ...
}}

Input:
{text}
""")

def classify_input(text: str) -> dict:
    try:
        # safe_text = text[:2000]
        prompt = prompt_template.format(text=text)
        logger.info("Sending text to LLM for classification...")

        raw_response = llm.invoke(prompt)
        logger.info(f"LLM response: {raw_response}")

        # Extract the first JSON object from the text
        match = re.search(r"\{.*?\}", raw_response, re.DOTALL)
        if match:
            result = json.loads(match.group())
            memory = SharedMemory()
            trace_id = memory.save_trace(result)
            result["trace_id"] = trace_id
            return result
        else:
            raise ValueError("No JSON object found in LLM response")

    except Exception as e:
        logger.error("Error during classification", exc_info=True)
        return {
            "format": "unknown",
            "intent": "unknown",
            "confidence": 0.0,
            "error": str(e)
        }
