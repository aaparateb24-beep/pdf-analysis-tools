from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

# Import your QnA system
from qa_system import process_text, get_answer

app = FastAPI()

# Allow frontend access (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store extracted text (temporary)
stored_text = ""


# 📄 1. Upload PDF and extract text
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global stored_text

    contents = await file.read()

    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        text = ""
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()

    stored_text = text

    # 🔥 VERY IMPORTANT: process text for AI
    process_text(stored_text)

    return {
        "message": "PDF uploaded and processed successfully",
        "length": len(stored_text)
    }


# 🤖 2. Ask Question
@app.post("/ask")
def ask_question(question: str):
    if not stored_text:
        return {"error": "Please upload a PDF first"}

    answer = get_answer(question)

    return {
        "question": question,
        "answer": answer
    }


# 🟢 3. Root (optional test)
@app.get("/")
def home():
    return {"message": "AI Document Analyzer Backend Running"}