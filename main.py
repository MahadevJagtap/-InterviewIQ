"""
Interview Question Generator — FastAPI Application
Main entry point for the web server.
"""

import logging
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from models.schemas import GenerationConfig, DifficultyLevel, QuestionCategory, InterviewQuestionSet
from services.graph_pipeline import interview_graph

# ─── Setup ────────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
)
logger = logging.getLogger("interview-gen")

app = FastAPI(
    title="Interview Question Generator",
    description="AI-powered interview question generator from Job Descriptions",
    version="1.1.0",
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def extract_text_from_file(file_path: str) -> str:
    """Use LangChain loaders to extract text from PDF or DOCX."""
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.lower().endswith((".docx", ".doc")):
        loader = UnstructuredWordDocumentLoader(file_path)
    else:
        raise ValueError("Unsupported file type")
    
    docs = loader.load()
    return "\n\n".join([doc.page_content for doc in docs])


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate")
async def generate_questions(
    file: UploadFile = File(...),
    difficulty: str = Form("Medium"),
    num_questions: int = Form(10),
    categories: str = Form("Technical,Behavioral,Situational"),
):
    """
    Accept a JD file upload, extract text via LangChain, and process via LangGraph.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    
    # Save to temp file because LangChain loaders expect a path
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Step 1: Extract text using LangChain Loaders
        logger.info(f"📄 Extracting text from {file.filename}")
        jd_text = extract_text_from_file(tmp_path)
        
        if not jd_text.strip():
            raise ValueError("Could not extract any text from the document.")

        # Step 2: Parse categories and build config
        try:
            cat_list = [QuestionCategory(c.strip()) for c in categories.split(",") if c.strip()]
        except ValueError:
            cat_list = [QuestionCategory.TECHNICAL, QuestionCategory.BEHAVIORAL, QuestionCategory.SITUATIONAL]
        
        config = GenerationConfig(
            difficulty=DifficultyLevel(difficulty),
            num_questions=num_questions,
            categories=cat_list,
        )

        # Step 3: Run LangGraph Pipeline
        logger.info("🚀 Invoking LangGraph AI pipeline")
        inputs = {
            "raw_jd_text": jd_text,
            "config": config,
            "analysis": None,
            "questions": None,
            "error": None
        }
        
        result_state = await interview_graph.ainvoke(inputs)

        if result_state.get("error"):
            raise RuntimeError(result_state["error"])

        # Step 4: Format Response
        # We wrap the results back into our InterviewQuestionSet model
        final_set = InterviewQuestionSet(
            jd_analysis=result_state["analysis"],
            questions=result_state["questions"],
            total_questions=len(result_state["questions"]),
            model_used="llama-3.3-70b-versatile"
        )
        
        return JSONResponse(content=final_set.model_dump(mode="json"))

    except Exception as e:
        logger.exception("Generation pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
