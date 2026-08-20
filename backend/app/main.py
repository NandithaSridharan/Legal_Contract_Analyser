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

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
    Depends
)
from app.services.pdf_report import (
    generate_report
)
from app.services.persistence_service import (
    save_complete_analysis
)
from app.services.contract_comparison import (
    compare_contracts
)
from app.nlp.contract_analyzer import analyze_contract
from app.models import (
    Contract,
    Clause,
    Risk,
    Entity,
    Obligation
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.services.pdf_report import generate_report
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.database import (
    engine,
    Base,
    get_db
)
from app.services.contract_comparison import (
    compare_contracts
)
from typing import List
from app import models
from sqlalchemy.orm import Session
from app.models import Contract

from app.embeddings.vector_store import ContractVectorStore
from app.ingestion.chunker import chunk_text
from app.ingestion.parser import extract_text_from_pdf
from app.rag.pipeline import RAGPipeline
from app.rag.summarizer import summarize_contract

from app.nlp.clause_extractor import extract_clauses
from app.nlp.risk_scorer import score_contract
from app.nlp.entity_extractor import extract_entities
from app.nlp.obligation_extractor import extract_obligations

from app.services.checklist_service import create_checklist
app = FastAPI(title="AI-Powered Legal Contract Analyzer")
Base.metadata.create_all(
    bind=engine
)

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
_CONTRACT_TEXT: dict[str, str] = {}


class ChatRequest(BaseModel):
    contract_id: int
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    contract_uuid = str(uuid.uuid4())

    save_path = os.path.join(
        UPLOAD_DIR,
        f"{contract_uuid}.pdf"
    )

    try:
        # Save PDF
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract text
        text = extract_text_from_pdf(
            save_path
        )

        if not text or not text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract any text from this PDF."
            )

        # Create FAISS/RAG pipeline
        chunks = chunk_text(text)

        store = ContractVectorStore()
        store.build(chunks)

        # Save contract to MySQL
        contract = Contract(
            filename=file.filename,
            title=os.path.splitext(
                file.filename
            )[0],
            extracted_text=text
        )

        db.add(contract)
        db.commit()
        db.refresh(contract)

        # The public identifier is the persisted MySQL ID. The UUID remains
        # internal and is used only for the uploaded file path.
        public_contract_id = str(contract.id)
        _CONTRACTS[public_contract_id] = RAGPipeline(store)
        _CONTRACT_TEXT[public_contract_id] = text

        return {
            "success": True,
            "contract_id": contract.id,
            "filename": file.filename,
            "num_chunks": len(chunks)
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/batch-upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):

    results = []

    for file in files:

        if not file.filename.lower().endswith(".pdf"):

            results.append({
                "filename": file.filename,
                "success": False,
                "message": "Only PDF files are supported."
            })

            continue

        contract_uuid = str(
            uuid.uuid4()
        )

        save_path = os.path.join(
            UPLOAD_DIR,
            f"{contract_uuid}.pdf"
        )

        try:

            with open(
                save_path,
                "wb"
            ) as f:

                shutil.copyfileobj(
                    file.file,
                    f
                )

            text = extract_text_from_pdf(
                save_path
            )

            if not text or not text.strip():

                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message":
                        "Could not extract text."
                })

                continue

            chunks = chunk_text(
                text
            )

            store = ContractVectorStore()

            store.build(
                chunks
            )

            # Save MySQL record
            contract = Contract(
                filename=file.filename,
                title=os.path.splitext(
                    file.filename
                )[0],
                extracted_text=text
            )

            db.add(
                contract
            )

            db.commit()

            db.refresh(
                contract
            )

            public_contract_id = str(contract.id)
            _CONTRACTS[public_contract_id] = RAGPipeline(store)
            _CONTRACT_TEXT[public_contract_id] = text

            results.append({
                "filename": file.filename,
                "success": True,
                "contract_id": contract.id,
                "num_chunks":
                    len(chunks)
            })

        except Exception as e:

            db.rollback()

            results.append({
                "filename": file.filename,
                "success": False,
                "message": str(e)
            })

    return {
        "success": True,
        "total_files": len(files),
        "results": results
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_contract(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    public_contract_id = str(req.contract_id)
    pipeline = _CONTRACTS.get(public_contract_id)
    if pipeline is None:
        contract = db.query(Contract).filter(Contract.id == req.contract_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found. Please upload or analyze the contract first.")
        text = contract.extracted_text
        if not text or not text.strip():
            raise HTTPException(status_code=422, detail="No extracted text found for this contract.")
        chunks = chunk_text(text)
        store = ContractVectorStore()
        store.build(chunks)
        pipeline = RAGPipeline(store)
        _CONTRACTS[public_contract_id] = pipeline
        _CONTRACT_TEXT[public_contract_id] = text

    result = pipeline.answer(req.question)
    return ChatResponse(answer=result["answer"], sources=result["sources"])
@app.get("/summary/{contract_id}")
async def get_summary(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")
    text = contract.extracted_text
    if not text:
        raise HTTPException(status_code=422, detail="No extracted text found for this contract.")

    summary = summarize_contract(text)
    return {"success": True, "contract_id": contract.id, "summary": summary}


@app.get("/extract-clauses/{contract_id}")
async def get_clauses(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")
    text = contract.extracted_text
    if not text:
        raise HTTPException(status_code=422, detail="No extracted text found for this contract.")

    clauses = extract_clauses(text)
    return {"success": True, "contract_id": contract.id, "clauses": clauses}
@app.post("/risk-analysis")
async def risk_analysis(payload: dict):
    """
    Analyze the risk of extracted contract clauses.

    Expected input:

    {
        "clauses": {
            "Termination For Convenience": "...",
            "Uncapped Liability": "...",
            "Governing Law": "..."
        }
    }
    """

    try:

        clauses = payload.get(
            "clauses"
        )

        if not clauses:

            return {
                "success": False,
                "message": "No clauses provided."
            }

        result = score_contract(
            clauses
        )

        return {
            "success": True,
            **result
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
@app.post("/extract-entities")
async def extract_contract_entities(
    payload: dict
):
    """
    Extract structured entities from contract text.

    Expected input:

    {
        "text": "contract text..."
    }
    """

    try:

        contract_text = payload.get(
            "text"
        )

        if not contract_text:

            return {
                "success": False,
                "message": "No contract text provided."
            }

        result = extract_entities(
            contract_text
        )

        return result

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
@app.post("/extract-obligations")
async def extract_contract_obligations(
    payload: dict
):
    """
    Extract contractual obligations and deadlines.

    Expected input:

    {
        "text": "contract text..."
    }
    """

    try:

        contract_text = payload.get(
            "text"
        )

        if not contract_text:

            return {
                "success": False,
                "message": "No contract text provided."
            }

        result = extract_obligations(
            contract_text
        )

        return result

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
@app.post("/obligations/checklist")
async def obligations_checklist(
    payload: dict
):
    try:

        obligations = payload.get(
            "obligations"
        )

        if not obligations:
            return {
                "success": False,
                "message": "No obligations provided."
            }

        return create_checklist(
            obligations
        )

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
@app.patch("/obligations/{obligation_id}")
async def update_obligation(
    obligation_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):

    obligation = (
        db.query(Obligation)
        .filter(
            Obligation.id == obligation_id
        )
        .first()
    )

    if not obligation:

        raise HTTPException(
            status_code=404,
            detail="Obligation not found."
        )

    if "completed" in payload:

        obligation.completed = bool(
            payload["completed"]
        )

    db.commit()

    db.refresh(
        obligation
    )

    return {
        "success": True,
        "obligation": {
            "id": obligation.id,
            "completed":
                obligation.completed
        }
    }
@app.delete("/contracts/{contract_id}")
async def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db)
):

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:

        raise HTTPException(
            status_code=404,
            detail="Contract not found."
        )

    db.delete(
        contract
    )

    db.commit()

    return {
        "success": True,
        "message": "Contract deleted successfully."
    }
@app.post("/contracts")
async def create_contract(
    payload: dict,
    db: Session = Depends(get_db)
):

    contract = Contract(
        filename=payload.get(
            "filename",
            "unknown.pdf"
        ),
        title=payload.get(
            "title"
        ),
        extracted_text=payload.get(
            "text"
        ),
        summary=payload.get(
            "summary"
        )
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return {
        "success": True,
        "contract_id": contract.id
    }
@app.get("/contracts")
async def get_contracts(
    db: Session = Depends(get_db)
):

    contracts = (
        db.query(Contract)
        .order_by(
            Contract.created_at.desc()
        )
        .all()
    )

    return {
        "success": True,
        "contracts": [
            {
                "id": contract.id,
                "filename": contract.filename,
                "title": contract.title,
                "created_at": contract.created_at,
                "analysis_status": "Analyzed" if contract.summary else "Pending analysis",
                "risk_score": round(max((risk.risk_score or 0 for risk in contract.risks), default=0)),
                "risk_level": max((risk.risk_level or "LOW" for risk in contract.risks), key=lambda level: {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(level.upper(), 0), default="LOW"),
                "pending_obligations": sum(1 for obligation in contract.obligations if not obligation.completed)
            }
            for contract in contracts
        ]
    }
@app.get("/contracts/{contract_id}")
async def get_contract(
    contract_id: int,
    db: Session = Depends(get_db)
):

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found.")

    return {
        "success": True,
        "contract": {
            "id": contract.id,
            "filename": contract.filename,
            "title": contract.title,
            "text": contract.extracted_text,
            "summary": contract.summary
        }
    }
@app.post("/export-report")
async def export_report(
    payload: dict
):

    try:

        buffer = generate_report(
            contract_title=payload.get(
                "contract_title",
                "Contract"
            ),

            summary=payload.get(
                "summary",
                ""
            ),

            risks=payload.get(
                "risks",
                []
            ),

            obligations=payload.get(
                "obligations",
                []
            ),

            entities=payload.get(
                "entities",
                {}
            )
        )

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    'attachment; filename="contract_analysis.pdf"'
            }
        )

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
@app.post("/compare-contracts")
async def compare_contract_versions(
    payload: dict
):

    contract_a = payload.get(
        "contract_a"
    )

    contract_b = payload.get(
        "contract_b"
    )

    return compare_contracts(
        contract_a,
        contract_b
    )
@app.get("/contracts/{contract_id}/full")
async def get_full_contract(
    contract_id: int,
    db: Session = Depends(get_db)
):

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:

        raise HTTPException(
            status_code=404,
            detail="Contract not found."
        )

    return {
        "success": True,

        "contract": {
            "id": contract.id,
            "filename": contract.filename,
            "title": contract.title,
            "summary": contract.summary,
            "created_at": contract.created_at,
            "updated_at": contract.updated_at
        },

        "clauses": [
            {
                "id": item.id,
                "category": item.category,
                "text": item.text
            }
            for item in contract.clauses
        ],

        "risks": [
            {
                "id": item.id,
                "category": item.category,
                "clause": item.clause,
                "risk_score": item.risk_score,
                "risk_level": item.risk_level,
                "reason": item.reason
            }
            for item in contract.risks
        ],

        "entities": [
            {
                "id": item.id,
                "type": item.entity_type,
                "value": item.entity_value
            }
            for item in contract.entities
        ],

        "obligations": [
            {
                "id": item.id,
                "obligation": item.obligation,
                "responsible_party":
                    item.responsible_party,
                "deadline": item.deadline,
                "frequency": item.frequency,
                "trigger": item.trigger,
                "category": item.category,
                "consequence":
                    item.consequence,
                "evidence": item.evidence,
                "completed": item.completed
            }
            for item in contract.obligations
        ]
    }
@app.post("/analyze-contract/{contract_id}")
async def analyze_contract_endpoint(
    contract_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------
    # FIND CONTRACT
    # --------------------------------------------------

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:

        raise HTTPException(
            status_code=404,
            detail="Contract not found."
        )

    # --------------------------------------------------
    # GET TEXT
    # --------------------------------------------------

    text = contract.extracted_text

    if not text or not text.strip():

        raise HTTPException(
            status_code=422,
            detail="No extracted text found."
        )

    try:

        # --------------------------------------------------
        # ONE GEMINI CALL
        # --------------------------------------------------

        result = analyze_contract(
            text
        )

        if not result.get("success"):

            error_message = result.get(
                "message",
                "Contract analysis failed."
            )

            # Gemini quota
            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED"
                in error_message
            ):

                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Gemini API quota exceeded. "
                        "Please wait and try again."
                    )
                )

            raise HTTPException(
                status_code=500,
                detail=error_message
            )

        analysis = result["analysis"]

        # --------------------------------------------------
        # GET INDIVIDUAL RESULTS
        # --------------------------------------------------

        summary = analysis.get(
            "summary",
            ""
        )

        clauses = analysis.get(
            "clauses",
            {}
        )

        entities = {
            "success": True,
            "entities": analysis.get(
                "entities",
                {}
            )
        }

        obligations = {
            "success": True,
            "obligations": analysis.get(
                "obligations",
                []
            )
        }

        # --------------------------------------------------
        # LOCAL RISK ANALYSIS
        # --------------------------------------------------

        risks = score_contract(
            clauses
        )

        # --------------------------------------------------
        # SAVE TO MYSQL
        # --------------------------------------------------

        save_complete_analysis(
            db=db,
            contract_id=contract_id,
            summary=summary,
            clauses=clauses,
            risks=risks,
            entities=entities,
            obligations=obligations
        )

        # --------------------------------------------------
        # CHECKLIST
        # --------------------------------------------------

        checklist = create_checklist(
            obligations
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return {

            "success": True,

            "contract_id": contract_id,

            "summary": summary,

            "clauses": clauses,

            "risk_analysis": risks,

            "entities": entities,

            "obligations": obligations,

            "checklist": checklist
        }

    except HTTPException:

        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.post("/export-report")
async def export_report(
    payload: dict
):

    try:

        buffer = generate_report(
            contract_title=payload.get(
                "contract_title",
                "Contract"
            ),

            summary=payload.get(
                "summary",
                ""
            ),

            risks=payload.get(
                "risks",
                []
            ),

            obligations=payload.get(
                "obligations",
                []
            ),

            entities=payload.get(
                "entities",
                {}
            )
        )

        return StreamingResponse(
            buffer,
            media_type="application/pdf",

            headers={
                "Content-Disposition":
                (
                    'attachment; '
                    'filename="contract_analysis.pdf"'
                )
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/health")
async def health():
    return {"status": "ok"}
