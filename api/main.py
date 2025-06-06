# multi_agent_system/api/main.py

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
import tempfile
import sys
import logging

# Setup logging
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

# Ensure root path is added for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifier_agent.agent import classify_input
from email_agent.agent import analyze_email
from memory.store import SharedMemory
from json_agent.agent import detect_json_anomaly
from pdf_agent.agent import analyze_pdf_flags
from router.action_router import ActionRouter
from pdf_agent.agent import extract_text_from_pdf

app = FastAPI()

action_router = ActionRouter()

@app.post("/classify")
async def classify_endpoint(file: UploadFile = File(...)):
    filename = file.filename
    logger.info(f"Received file for classification: {filename}")
    content = await file.read()

    try:
        if filename.endswith(".json"):
            text = json.loads(content.decode("utf-8"))
            logger.info("Parsed JSON file content")
        elif filename.endswith(".pdf"):
            # # Save PDF to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                temp_pdf_path = tmp.name
            # text = temp_pdf_path  # Pass the filename as text

            text = extract_text_from_pdf(temp_pdf_path)
            if not text:
                return {"flags": [], "error": "No text extracted from PDF."}
        else:
            text = content.decode("utf-8")
            # logger.info("Decoded text : %s", text[:100] + "...")  # Log first 100 chars for brevity

        # Run classification
        logger.info("Running classification...")
        classification = classify_input(text)
        logger.info(f"Classification result: {classification}")

        trace_id = classification.get("trace_id")
        agent_response = {}

        # Route to appropriate agent based on format
        if classification["format"] == "email":
            logger.info("Routing to Email Agent")
            agent_response = analyze_email(text)

        elif classification["format"] == "json":
            logger.info("Routing to JSON Agent")
            agent_response = detect_json_anomaly(text)

        elif classification["format"] == "pdf":
            logger.info("Routing to PDF Agent")
            agent_response = analyze_pdf_flags(text)

        else:
            logger.warning(f"Unknown format: {classification['format']}")

        logger.info(f"Agent response: {agent_response}")

        # Call action router
        logger.info("Routing to Action Router...")
        action_output = action_router.route(agent_response)
        logger.info(f"Action Output: {action_output}")

        return {
            "classification": classification,
            "agent_output": agent_response,
            "action_output": action_output
        }

    except Exception as e:
        logger.error(f"Error in /classify: {e}", exc_info=True)
        # Clean up temp PDF file if created
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to classify input: {str(e)}"}
        )

@app.get("/trace/{trace_id}")
def get_trace(trace_id: str):
    logger.info(f"Fetching trace for trace_id: {trace_id}")
    memory = SharedMemory()
    entries = memory.get_trace(trace_id)

    if not entries:
        logger.warning(f"No trace found for trace_id: {trace_id}")
        return JSONResponse(status_code=404, content={"error": "Trace ID not found"})

    logger.info(f"Trace found: {entries}")
    return {"trace_id": trace_id, "entries": entries}

@app.get("/")
def root():
    logger.info("Health check hit on '/' endpoint")
    return {"message": "Classifier API is up and running"}
