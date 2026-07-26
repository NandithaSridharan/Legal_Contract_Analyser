# AI-Powered Legal Contract Analyzer

RAG + NLP system for uploading legal contracts and getting instant summaries,
clause extraction, risk scoring, and grounded Q&A chat.

## Team split
- **Backend / RAG pipeline** — PDF ingestion, embeddings, FAISS, RAG, FastAPI
- **Frontend** — React upload UI, chat interface, dashboard

## API contract (agree on this first)
| Endpoint | Method | Purpose |
|---|---|---|
| `/upload` | POST (multipart file) | Upload a contract PDF, returns `contract_id` |
| `/chat` | POST `{contract_id, question}` | Ask a question, returns `{answer, sources}` |
| `/health` | GET | Sanity check |

Frontend dev can mock these exact shapes and build the UI without waiting on
the backend being finished.

---

## Step-by-step: getting the RAG pipeline running

### 1. Push this skeleton to GitHub
```bash
cd legal-contract-analyzer
git init
git add .
git commit -m "Initial project skeleton"
gh repo create legal-contract-analyzer --public --source=. --push
# or create the repo on github.com manually and:
# git remote add origin <your-repo-url>
# git push -u origin main
```
Then add your teammate as a collaborator (repo Settings → Collaborators),
and both work on feature branches (`backend/rag-pipeline`, `frontend/upload-ui`)
merged via PRs.

### 2. Set up your Python environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
If `pytesseract`/`pdf2image` complain, install system deps:
- Mac: `brew install tesseract poppler`
- Ubuntu/Debian: `sudo apt install tesseract-ocr poppler-utils`

### 3. Get a Gemini API key
Get one free at https://aistudio.google.com/apikey. Copy `.env.example` to
`.env` and paste it in:
```bash
cp .env.example .env
# edit .env, set GEMINI_API_KEY=...
```

### 4. Test each piece in isolation (in this order)

**a) PDF parsing** — drop any contract PDF in `backend/` and run:
```bash
cd backend
python -m app.ingestion.parser path/to/some_contract.pdf
```
You should see extracted text printed. If it's empty, your PDF is scanned
and OCR should kick in automatically — check Tesseract is installed.

**b) Chunking**
```bash
python -m app.ingestion.chunker
```
Should print sample chunks with overlap. This confirms the splitter logic
works before you feed it real contract text.

**c) Embeddings + FAISS**
```bash
python -m app.embeddings.vector_store
```
First run downloads the `all-MiniLM-L6-v2` model (~80MB). Should print the
2 most relevant chunks for a test query.

**d) Full RAG pipeline** (needs `GEMINI_API_KEY` in `.env`)
```bash
python -m app.rag.pipeline
```
Should print a grounded answer + which source chunks it used.

### 5. Run the API server
```bash
uvicorn app.main:app --reload
```
Visit `http://localhost:8000/docs` — FastAPI's auto-generated Swagger UI.
Use it to manually upload a PDF and test `/chat` before the frontend exists.

### 6. Hand off to your teammate
Once `/upload` and `/chat` work in `/docs`, your teammate can point their
React fetch calls at `http://localhost:8000` and build against real
responses instead of mocks.

---

## Next steps after the pipeline works
- [ ] NER + clause classification (Hugging Face Transformers) on extracted chunks
- [ ] Risk scoring logic on top of extracted clauses
- [ ] MySQL persistence (contracts, chat history) instead of in-memory dict
- [ ] Contract comparison (diff two documents)
- [ ] Deadline/obligation extraction → exportable checklist
- [ ] PDF export of summaries

See `docs/` for dataset notes (CUAD, LEDGAR) once you start clause
classification / risk scoring training.
