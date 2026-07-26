"""
Step 5: FastAPI app exposing the pipeline as HTTP endpoints.

Run with:
    uvicorn app.main:app --reload

This is what your frontend teammate builds against. Endpoints and response
shapes below are the "API contract" — agree on these together before either
of you goes too far, so the frontend can mock these responses without
waiting on the backend.
"""
import os
import shutil
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.embeddings.vector_store import ContractVectorStore
from app.ingestion.chunker import chunk_text
from app.ingestion.parser import extract_text_from_pdf
from app.rag.pipeline import RAGPipeline

app = FastAPI(title="AI-Powered Legal Contract Analyzer")

# Allow the React dev server to call this API. Tighten this before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# MVP in-memory store: contract_id -> RAGPipeline
# Swap for a real per-contract persisted index (+ MySQL row) once multi-user
# support is needed. Fine for a single-user dev/demo build.
_CONTRACTS: dict[str, RAGPipeline] = {}


class ChatRequest(BaseModel):
    contract_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contract_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{contract_id}.pdf")

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text_from_pdf(save_path)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from this PDF.")

    chunks = chunk_text(text)

    store = ContractVectorStore()
    store.build(chunks)
    _CONTRACTS[contract_id] = RAGPipeline(store)

    return {
        "contract_id": contract_id,
        "filename": file.filename,
        "num_chunks": len(chunks),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_with_contract(req: ChatRequest):
    pipeline = _CONTRACTS.get(req.contract_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Contract not found. Upload it first.")

    result = pipeline.answer(req.question)
    return ChatResponse(answer=result["answer"], sources=result["sources"])


@app.get("/health")
async def health():
    return {"status": "ok"}
