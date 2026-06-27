import os
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

class ChatMessage(BaseModel):
    message: str

class DocumentText(BaseModel):
    text: str

app = FastAPI()

#THIS IS ONLY FOR A HACKATHON. IN REAL LIFE DEVELOPMENT PROCCESS I'D NEVER LEAVE A KEY IN CODE
API_KEY = ""
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('') # ADD MODEL 

@app.get("/")
def home():
    return {"status": "Server is running!"}

@app.post("/chat")
def ask_bot(data: ChatMessage):
    response = model.generate_content(data.message)
    
    return {"reply": response.text}


@app.post("/analyze")
def analyze_document(data: DocumentText):
    system_instruction = (
        "You are an expert at finding hidden terms (fineprint) in contracts. Analyze the text below and find hidden fees, automatic renewals, waivers of rights to litigation or transfer of data to third parties. Answer STRICTLY in JSON format (an array of objects). Each object must have the following fields: 'category' (Critical/Attention/Info), 'title' (a brief summary), 'explanation' (in plain language, what the catch is)."
    )
    
    full_prompt = f"{system_instruction}\n\nAgreement Text:\n{data.text}"
    
    response = model.generate_content(full_prompt)
    
    return {"analysis": response.text}