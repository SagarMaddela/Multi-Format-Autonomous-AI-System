# 🤖 Multi-Format Autonomous AI System with Contextual Decisioning & Chained Actions

This project implements a multi-agent system capable of processing inputs from **Email**, **JSON**, and **PDF** formats. It classifies both the format and business intent, routes the data to specialized agents, and dynamically chains follow-up actions based on extracted information (e.g., triggering alerts, generating summaries, flagging risks).

## 🚀 Features

### 🔍 Classifier Agent

* Detects input format: `Email`, `PDF`, or `JSON`.
* Identifies business intent: `RFQ`, `Complaint`, `Invoice`, `Regulation`, `Fraud Risk`.
* Utilizes few-shot examples and schema matching.
* Stores metadata in shared memory.

### 📧 Email Agent

* Extracts structured fields: sender, urgency, issue/request.
* Identifies tone: `Polite`, `Escalation`, `Threatening`.
* Triggers actions based on tone and urgency:

  * Escalation → `POST /crm/escalate`.
  * Routine → logs and closes.

### 📦 JSON Agent

* Parses webhook-style JSON data.
* Validates required schema fields.
* Flags anomalies (e.g., field mismatches, type errors) and logs alerts to memory.

### 📄 PDF Agent

* Extracts fields using PDF parsers (`PyPDF2`, `Apache Tika`).
* Parses line-item invoice data or policy documents.
* Flags if:

  * Invoice total > 10,000.
  * Policy mentions "GDPR", "FDA", etc.

### 🧠 Shared Memory Store

* All agents read/write to shared memory.
* Stores:

  * Input metadata (source, timestamp, classification).
  * Extracted fields per agent.
  * Chained actions triggered.
  * Agent decision traces.
* Implemented using SQLite or Redis.

### 🔁 Action Router

* Based on agent outputs, triggers follow-up actions:

  * `POST /crm/escalate`.
  * `POST /risk_alert`.
  * `POST /log`.

## 📂 Project Structure

```
multi-format-autonomous-ai-system/
├── api/
├── classifier_agent/
├── email_agent/
├── json_agent/
├── memory/
├── pdf_agent/
├── router/
├── samples/
├── tests/
├── utils/
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── README.md
├── requirements.txt
└── supervisord.conf
```

## 🧪 Sample Inputs

* `samples/sample_email.eml`: Escalated complaint email.
* `samples/sample_invoice.pdf`: Invoice with line items.
* `samples/sample_webhook.json`: Webhook with RFQ data.

## 🛠 Tech Stack

* **Python** + **FastAPI** for microservice architecture.
* **LangChain** + LLMs for routing and field extraction.
* **PyPDF2**, **Apache Tika** for PDF parsing.
* **Faker** for generating sample JSON payloads.
* **SQLite / Redis** for shared memory.
* **Docker** for containerization.

## 🧰 How to Run

```bash
# 1. Clone the repository
git clone https://github.com/SagarMaddela/Multi-Format-Autonomous-AI-System.git
cd Multi-Format-Autonomous-AI-System

# 2. Install and run the LLaMA3 model using Ollama
# (Make sure Ollama is installed: https://ollama.com)
ollama run llama3

# 3. Create a virtual environment and activate it (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

---

## 📤 Outputs

* Memory log of all inputs and actions.
* Triggered actions shown via REST endpoints.
* Decision trace of each agent.

## 📸 Screenshots

| Email Classification            | PDF Invoice Parsing         | JSON Anomaly                  |
| ------------------------------- | --------------------------- | ----------------------------- |
| ![email](screenshots/email.png) | ![pdf](screenshots/pdf.png) | ![json](screenshots/json.png) |

## 📄 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgements

Special thanks to Flowbit Private Limited for providing the challenge specification.

For questions or contributions, feel free to raise an issue or pull request!
