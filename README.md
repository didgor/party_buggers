<div align="center">

<img src="docs/banner.png" alt="HouseWise – Student Housing Transparency Assistant" width="100%">

</div>

## 🏠 Why HouseWise?

Finding student accommodation should be exciting, not a gamble.

As students, finding accommodation can feel like one of the most stressful parts of university. You're expected to sign a legally binding contract, understand complicated tenancy agreements, trust that a landlord is legitimate, and commit to paying thousands of pounds, often within just a few days. Most students simply don't have the experience to know whether they're making the right decision.

Every year, thousands of students sign tenancy agreements without fully understanding what they're agreeing to. They often don't know whether the rent is actually competitive, whether hidden costs will make the property more expensive, whether the landlord has a poor reputation, or even whether they're renting from someone who is properly certified. Important information exists, but it's scattered across different platforms, making it difficult for students to make informed decisions.

**HouseWise brings all of this information into one place.**

---

## 🚀 Features

* **AI Fine Print Analyzer (`/analyze`)**: Scans contract text using Gemini 2.5 Flash and returns a structured JSON array of hidden fees, automatic renewals, and legal risks.
* **AI Legal Chatbot (`/chat`)**: A conversational AI assistant to ask quick questions about lease terms or landlord disputes.
* **PDF Text Extraction**: Automatic PDF parsing using PyMuPDF (`fitz`).
* **Rule-Based Red Flag Scanner**: Fast, keyword-based local screening for common rental traps.

---

## 🛠️ Prerequisites & Dependencies

Before building and running the project, ensure you have **Python 3.10+** installed on your machine.

### Required Python Packages
The project relies on the following core libraries:
* **Flask**: The lightweight web framework powering the API.
* **google-genai**: The official, modern SDK for Google Gemini models.
* **PyMuPDF (`fitz`)**: Used for robust PDF document text extraction.

To install all dependencies at once, run:
```bash
pip3 install flask pymupdf google-genai
```

To run the backend, run:
```bash
python3 HouseWise/app.py