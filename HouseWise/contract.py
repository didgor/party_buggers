from flask import Blueprint, request, jsonify
import fitz  # PyMuPDF
import os
from google import genai

contracts_bp = Blueprint('contracts', __name__)

# Initialising the Gemini client
ai_client = genai.Client(api_key="AQ.AdshjbfsdhjbEiCFW6GSzPB4nRmpWMREAg9_qhOVu_TAveB19fOw") #THIS IS ONLY FOR A HACKATHON. IN REAL LIFE DEVELOPMENT PROCCESS WE'D NEVER LEAVE A KEY IN CODE

# -------------------------------------------------------
# RED FLAG DEFINITIONS
# Each entry has:
#   - keywords  : words to look for in the contract
#   - risk      : how serious it is
#   - meaning   : plain English explanation
#   - question  : what to ask the landlord before signing
# -------------------------------------------------------
RED_FLAGS = [
    {
        "keywords": ["professional cleaning", "professional clean"],
        "risk": "Medium",
        "meaning": "You may be charged for a professional cleaner when you leave, even if the property is clean.",
        "question": "Can you remove the professional cleaning clause? I intend to leave the property in the same condition I found it."
    },
    {
        "keywords": ["joint and several liability", "jointly and severally"],
        "risk": "High",
        "meaning": "If a housemate stops paying rent, YOU could be held responsible for their share.",
        "question": "Can you explain what happens if one tenant cannot pay their share of the rent?"
    },
    {
        "keywords": ["no break clause", "no early termination"],
        "risk": "High",
        "meaning": "You cannot leave early. You are locked in for the full tenancy period.",
        "question": "Is there any way to end the tenancy early if my circumstances change?"
    },
    {
        "keywords": ["landlord may enter", "landlord can enter", "right to enter", "access at any time"],
        "risk": "Medium",
        "meaning": "The landlord may be claiming the right to enter without proper notice. By law they usually need 24 hours notice.",
        "question": "Can you confirm you will always give 24 hours written notice before entering the property?"
    },
    {
        "keywords": ["non-refundable", "non refundable", "holding deposit is non"],
        "risk": "High",
        "meaning": "Some fees or deposits may not be returned to you.",
        "question": "Under what circumstances would I not get this money back?"
    },
    {
        "keywords": ["sign today", "must sign today", "sign immediately", "sign now"],
        "risk": "High",
        "meaning": "You are being pressured to sign immediately. You always have the right to take time to read a contract.",
        "question": "Can you give me at least 48 hours to review this contract properly before signing?"
    },
    {
        "keywords": ["fair wear and tear excluded", "wear and tear not accepted", "no wear and tear"],
        "risk": "High",
        "meaning": "The landlord may try to charge you for normal everyday use of the property, which is not legal.",
        "question": "Can you clarify what you consider fair wear and tear?"
    },
    {
        "keywords": ["redecoration", "repainting", "repaint"],
        "risk": "Medium",
        "meaning": "You could be charged for repainting walls even if you did not damage them.",
        "question": "Can you confirm what standard the property should be returned in regarding decoration?"
    },
    {
        "keywords": ["pets not permitted", "no pets allowed", "no pets"],
        "risk": "Low",
        "meaning": "You cannot keep any pets at the property.",
        "question": "Is there any flexibility on the no pets policy?"
    },
    {
        "keywords": ["subletting", "no subletting", "not sublet"],
        "risk": "Low",
        "meaning": "You cannot rent out any part of the property to someone else.",
        "question": "What happens if I need a friend to temporarily stay and contribute to rent?"
    },
    {
        "keywords": ["deposit deduction", "deduct from deposit"],
        "risk": "Medium",
        "meaning": "The landlord lists reasons they can take money from your deposit. Check these carefully.",
        "question": "Can you give me a full list of what you would deduct from my deposit?"
    },
    {
        "keywords": ["notice period", "one month notice", "two months notice"],
        "risk": "Low",
        "meaning": "Check how much notice you need to give before leaving, and how much notice the landlord must give you.",
        "question": "What notice period applies to both me and you as the landlord?"
    },
]


def extract_text_from_pdf(filepath):
    """Pull all text out of a PDF file."""
    text = ""
    doc = fitz.open(filepath)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def scan_for_red_flags(text):
    """Check the contract text against our red flag list."""
    found_flags = []
    text_lower = text.lower()

    for flag in RED_FLAGS:
        for keyword in flag["keywords"]:
            if keyword.lower() in text_lower:
                # Find a snippet of the actual contract text around the keyword
                idx = text_lower.find(keyword.lower())
                snippet = text[max(0, idx - 80): idx + 120].strip()
                snippet = snippet.replace("\n", " ")

                found_flags.append({
                    "risk": flag["risk"],
                    "triggered_by": keyword,
                    "contract_snippet": f"...{snippet}...",
                    "plain_english": flag["meaning"],
                    "question_to_ask": flag["question"],
                })
                break  # Only flag once per red flag category

    return found_flags


def calculate_risk_score(flags):
    """Give the contract an overall risk level."""
    if not flags:
        return "Low", "No major red flags found. Still read it carefully!"

    high = sum(1 for f in flags if f["risk"] == "High")
    medium = sum(1 for f in flags if f["risk"] == "Medium")

    if high >= 2:
        return "High", "This contract has serious concerns. Do not sign until you get answers."
    elif high == 1 or medium >= 2:
        return "Medium", "This contract has some concerns worth questioning before you sign."
    else:
        return "Low", "This contract looks fairly standard but always ask about anything unclear."


# -------------------------------------------------------
# ROUTE: Upload a contract PDF and scan it
# POST /contracts/scan
# -------------------------------------------------------
@contracts_bp.route('/contracts/scan', methods=['POST'])
def scan_contract():
    # 1. Check a file was sent
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded. Please upload a PDF."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Please upload a PDF file."}), 400

    # 2. Save the file
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)

    # 3. Extract text from PDF
    try:
        contract_text = extract_text_from_pdf(filepath)
    except Exception as e:
        return jsonify({"error": f"Could not read PDF: {str(e)}"}), 500

    if not contract_text.strip():
        return jsonify({"error": "The PDF appears to be empty or is a scanned image we cannot read."}), 400

    # 4. Scan for red flags
    flags = scan_for_red_flags(contract_text)

    # 5. Calculate overall risk
    overall_risk, summary = calculate_risk_score(flags)

    # 6. Send back the results
    return jsonify({
        "overall_risk": overall_risk,
        "summary": summary,
        "total_flags_found": len(flags),
        "red_flags": flags,
        "advice": "Always take at least 48 hours to read a contract. Never sign under pressure."
    })


# -------------------------------------------------------
# ROUTE: Health check — just to test the server is running
# GET /
# -------------------------------------------------------
@contracts_bp.route('/', methods=['GET'])
def home():
    return jsonify({"message": "HouseWise backend is running!"})

@contracts_bp.route('/chat', methods=['POST'])
def ask_bot():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request body"}), 400
        
    user_message = data['message']

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": f"AI Service Error: {str(e)}"}), 500

@contracts_bp.route('/analyze', methods=['POST'])
def analyze_document():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
        
    contract_text = data['text']

    system_instruction = (
        "You are an expert at finding hidden terms (fineprint) in contracts. "
        "Analyze the text below and find hidden fees, automatic renewals, "
        "waivers of rights to litigation or transfer of data to third parties. "
        "Answer STRICTLY in JSON format (an array of objects). "
        "Each object must have the following fields: "
        "'category' (Critical/Attention/Info), 'title' (a brief summary), "
        "'explanation' (in plain language, what the catch is)."
    )
    
    full_prompt = f"{system_instruction}\n\nAgreement Text:\n{contract_text}"

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt
        )
        return jsonify({"analysis": response.text})
    except Exception as e:
        return jsonify({"error": f"AI Service Error: {str(e)}"})