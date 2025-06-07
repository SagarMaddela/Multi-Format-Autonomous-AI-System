# utils/llm_utils.py
import requests
from langchain_community.llms import Ollama

# This loads a local Ollama model like llama3, phi3, mistral etc.

def get_llm():
    try:
        # response = requests.get("http://localhost:11434/api/tags", timeout=3)
        response = requests.get("http://host.docker.internal:11434/api/tags", timeout=3)
        if response.status_code != 200:
            raise ConnectionError("Ollama is not reachable or model not loaded.")
    except Exception as e:
        raise RuntimeError(f"LLM connection failed: {e}")
    
    return Ollama(model="llama3", base_url="http://host.docker.internal:11434")
