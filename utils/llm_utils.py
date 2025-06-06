# utils/llm_utils.py

from langchain.llms import Ollama

# This loads a local Ollama model like llama3, phi3, mistral etc.
llm = Ollama(model="llama3")
