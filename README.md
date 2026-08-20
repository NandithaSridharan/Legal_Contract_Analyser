


# 📄 LexiCore AI — Legal Contract Intelligence Platform

> **AI-powered legal contract analysis, risk detection, obligation tracking, document comparison, and grounded question answering using RAG.**

LexiCore AI is an intelligent legal contract analysis platform designed to help users **upload, understand, analyze, compare, and manage legal contracts** using Artificial Intelligence and Retrieval-Augmented Generation (RAG).

The system extracts important information from contracts, identifies clauses and potential risks, tracks contractual obligations and deadlines, generates summaries, and allows users to ask questions about a specific contract with answers grounded in the uploaded document.

---

## 🚀 Key Features

### 📑 Contract Management

* Upload legal contracts in PDF format
* Store contracts securely
* View all uploaded contracts
* Search and filter contracts
* Track contract analysis status
* View individual contract workspaces

### 🤖 AI Contract Analysis

The system analyzes contracts and extracts important information such as:

* Contract parties
* Effective date
* Contract type
* Governing law
* Contract duration
* Clauses
* Entities
* Obligations
* Deadlines
* Payment terms
* Termination conditions
* Confidentiality provisions
* Liability provisions
* Dispute resolution
* Non-compete clauses
* Insurance requirements

---

### 🧠 AI-Powered Contract Summary

The system generates a concise overview of the contract containing:

* Purpose of the agreement
* Parties involved
* Major responsibilities
* Contract duration
* Important contractual terms
* Key risks
* Important obligations

Instead of manually reading an entire contract, users can quickly understand the agreement through an AI-generated summary.

---

### 💬 Grounded Contract Q&A

LexiCore AI provides a **contract-specific AI assistant**.

Users can ask questions such as:

```text
What is this contract about?

What are the termination conditions?

What are my obligations?

When does this contract expire?

What are the payment terms?

Which clauses are risky?

Who are the parties involved?

What is the governing law?

What happens if the agreement is terminated?
```

The assistant retrieves relevant sections from the contract and generates an answer based on those sections.

This follows a **Retrieval-Augmented Generation (RAG)** approach rather than relying only on the language model's general knowledge.

---

### ⚠️ Risk Analysis

The platform identifies potentially important contractual risks and categorizes them.

Examples include:

* Non-compete
* Termination
* Insurance
* Governing Law
* Dispute Resolution
* Confidentiality
* Limitation of Liability
* Payment-related risks
* Other contractual risks

Each contract receives a risk overview that helps users prioritize clauses requiring attention.

---

### 📌 Obligation & Deadline Tracking

The system extracts contractual obligations and presents them in a structured format.

Each obligation can contain:

| Field             | Description                                      |
| ----------------- | ------------------------------------------------ |
| Responsible Party | Party responsible for the obligation             |
| Deadline          | When the obligation must be completed            |
| Frequency         | One-time, monthly, ongoing, etc.                 |
| Category          | Reporting, Payment, Marketing, Development, etc. |
| Status            | Pending / completed                              |

This allows users to identify commitments that might otherwise be missed in lengthy contracts.

---

### 🔄 Contract Comparison

The comparison module allows users to compare two stored contracts.

It identifies:

* Removed clauses
* Added clauses
* Modified language
* Changed terms
* Differences between contract versions

This is particularly useful for reviewing different versions of an agreement before negotiation or approval.

---

### 📊 Contract Reports

The system provides a consolidated report containing:

* AI-generated contract summary
* Number of clauses
* Number of risks
* Entities
* Obligations
* Deadlines
* Risk findings
* Important contractual information

Reports can be generated for further review and documentation.

---

## 🏗️ System Architecture

The overall system follows a modular architecture:

```text
                    ┌─────────────────────┐
                    │      User           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │   Web Application    │
                    └──────────┬──────────┘
                               │
                         REST API
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌────────────┐    ┌─────────────┐   ┌─────────────┐
      │ Document   │    │ NLP / AI    │   │ Database    │
      │ Processing │    │ Processing  │   │             │
      └─────┬──────┘    └──────┬──────┘   └─────────────┘
            │                  │
            ▼                  ▼
      ┌────────────┐    ┌─────────────┐
      │ Chunking   │    │ Embeddings  │
      └─────┬──────┘    └──────┬──────┘
            │                  │
            └──────────┬───────┘
                       ▼
                ┌─────────────┐
                │ Vector Store│
                │    FAISS    │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ RAG Retrieval│
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │ LLM / AI    │
                │ Generation  │
                └─────────────┘
```

---

# 🔄 RAG Pipeline

The Contract Q&A system follows a Retrieval-Augmented Generation pipeline.

```text
PDF Contract
     │
     ▼
Text Extraction
     │
     ▼
Document Cleaning
     │
     ▼
Text Chunking
     │
     ▼
Embeddings Generation
     │
     ▼
Vector Database / FAISS
     │
     ▼
User Question
     │
     ▼
Question Embedding
     │
     ▼
Similarity Search
     │
     ▼
Relevant Contract Chunks
     │
     ▼
Context + Question
     │
     ▼
LLM
     │
     ▼
Grounded Answer
     │
     ▼
Source References
```

### Why RAG?

Legal contracts can contain hundreds of pages. Passing the entire document to an AI model for every question is inefficient and may exceed context limits.

RAG solves this by:

1. Breaking the contract into smaller chunks.
2. Converting the chunks into vector representations.
3. Storing the vectors.
4. Converting the user's question into a vector.
5. Finding the most relevant contract sections.
6. Sending only the relevant context to the language model.
7. Generating an answer based on the retrieved contract content.

This improves **relevance, efficiency, and document grounding**.

---

# 🧩 Main Modules

## 1. Authentication Module

Provides secure access to the platform.

### Functions

* User registration
* Secure login
* Credential verification
* Session management
* Logout

### Outcome

Only authenticated users can access their contracts and analysis features.

---

## 2. Contract Management Module

Handles the complete contract lifecycle.

### Functions

* Upload contract
* Store contract
* View contracts
* Search contracts
* Filter contracts
* Delete contracts
* Open contract workspace

---

## 3. Document Processing Module

Processes uploaded contracts before AI analysis.

### Functions

* PDF processing
* Text extraction
* Text cleaning
* Document segmentation
* Chunk generation

---

## 4. NLP & Information Extraction Module

Extracts meaningful information from contractual text.

### Extracted Information

* Parties
* Dates
* Clauses
* Entities
* Obligations
* Deadlines
* Payment information
* Termination conditions
* Legal provisions

---

## 5. RAG Module

Provides document-grounded question answering.

### Process

```text
Question
   ↓
Embedding
   ↓
Similarity Search
   ↓
Relevant Contract Sections
   ↓
Context Construction
   ↓
LLM
   ↓
Answer + Sources
```

---

## 6. Contract Risk Analysis Module

Identifies potentially risky contractual provisions.

### Risk Categories

* Termination
* Non-compete
* Insurance
* Liability
* Confidentiality
* Governing law
* Dispute resolution
* Payment
* Other contractual risks

---

## 7. Obligation Management Module

Converts contractual commitments into structured obligations.

```text
Contract Clause
      ↓
Obligation Extraction
      ↓
Responsible Party
      ↓
Deadline
      ↓
Frequency
      ↓
Category
      ↓
Status
```

---

## 8. Contract Comparison Module

Compares two contracts or versions.

```text
Original Contract
        │
        ├──────────────┐
        │              │
        ▼              ▼
   Contract A      Contract B
        │              │
        └──────┬───────┘
               ▼
        Text Comparison
               │
               ▼
       Difference Detection
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
      Added  Removed Modified
```

---

## 9. Reporting Module

Generates a consolidated view of the contract analysis.

### Report Includes

* Contract summary
* Clauses
* Risks
* Entities
* Obligations
* Deadlines
* Important findings

---

# 🛠️ Technology Stack

### Frontend

* React
* JavaScript / TypeScript
* HTML
* CSS
* REST API integration

### Backend

* Python
* FastAPI
* REST APIs

### Database

* MySQL
* SQLAlchemy / database ORM

### AI / NLP

* Natural Language Processing
* Embeddings
* Large Language Models
* Retrieval-Augmented Generation (RAG)

### Vector Search

* FAISS

### Machine Learning / Data Processing

* Python
* NumPy
* Pandas
* Scikit-learn

### Development Tools

* Git
* GitHub
* VS Code

---

# 📁 Project Structure

```text
legal-contract-analyzer/
│
├── backend/
│   │
│   ├── app/
│   │   ├── evaluation/
│   │   │
│   │   ├── nlp/
│   │   │
│   │   ├── rag/
│   │   │   └── summarizer.py
│   │   │
│   │   ├── services/
│   │   │
│   │   ├── database.py
│   │   ├── models.py
│   │   └── main.py
│   │
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

---

# ⚙️ Installation & Setup

## Prerequisites

Make sure you have installed:

* Python 3.x
* Node.js
* npm
* MySQL
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/legal-contract-analyzer.git
cd legal-contract-analyzer
```

Replace `YOUR-USERNAME` with your GitHub username.

---

# 🐍 Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file inside `backend/`.

You can use `.env.example` as the template.

Example:

```env
DATABASE_URL=your_database_url
OPENAI_API_KEY=your_api_key
```

**Never commit `.env` to GitHub.**

---

## Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend will normally run on:

```text
http://127.0.0.1:8000
```

---

# ⚛️ Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at the URL shown by the development server.

---

# 📌 Dataset

The project uses the **CUAD (Contract Understanding Atticus Dataset)** as a source for legal contract understanding and evaluation.

CUAD contains legal contracts annotated for different contractual clauses and is useful for developing and evaluating contract analysis systems.

The dataset is not included directly in this repository when it is unnecessary for application execution.

---

# 🔐 Security & Privacy

The project follows basic security practices including:

* Environment variables for API credentials
* `.env` excluded from Git
* Uploaded documents excluded from version control
* Local vector indexes excluded from Git
* Separation of frontend and backend
* User authentication
* Contract-specific document retrieval

Sensitive documents and credentials should not be committed to the repository.

---

# 🎯 Project Objectives

The main objectives of LexiCore AI are:

1. Automate legal contract analysis.
2. Reduce the time required to manually review contracts.
3. Extract important contractual information.
4. Identify potentially risky clauses.
5. Track contractual obligations and deadlines.
6. Provide document-grounded question answering.
7. Compare different contract versions.
8. Generate structured contract reports.
9. Improve accessibility of complex legal documents.

---

# 🔬 AI Approach

The project combines several AI/NLP techniques:

```text
Natural Language Processing
          +
Information Extraction
          +
Text Embeddings
          +
Vector Similarity Search
          +
Retrieval-Augmented Generation
          +
Large Language Models
```

The combination allows the system to move from simple document storage toward **intelligent contract understanding**.

---

# 💡 Example Workflow

A typical user workflow is:

```text
Login
  ↓
Upload Contract
  ↓
Document Processing
  ↓
AI Analysis
  ↓
Contract Workspace
  │
  ├── Overview
  ├── Clauses
  ├── Risks
  ├── Entities
  ├── Obligations
  ├── Chat
  ├── Compare
  └── Reports
```

---

# 📊 Example Analysis

For a contract containing a termination clause such as a notice-based termination provision, the system can identify:

```text
Risk Category:
Termination

Responsible Party:
Contracting Party

Notice Period:
30 days

Risk Level:
High / Medium / Low

Source:
Relevant contract clause
```

The user can then ask:

> "What are the termination conditions?"

The RAG system retrieves the relevant section and generates a grounded answer.

---

# 🚧 Current Limitations

The current system is a final-year academic project/prototype and may have limitations such as:

* Extraction accuracy can vary depending on document formatting.
* Scanned PDFs may require OCR.
* Legal interpretation should be reviewed by qualified legal professionals.
* AI-generated answers should not be treated as legal advice.
* Complex contractual relationships may require additional domain-specific processing.

---

# 🔮 Future Enhancements

Possible future improvements include:

* OCR for scanned contracts
* Multi-language contract analysis
* Advanced clause classification
* Improved entity extraction
* Clause-level risk scoring
* Contract renewal notifications
* Email/calendar integration
* Advanced negotiation recommendations
* Automated redlining
* Clause recommendation
* Legal precedent retrieval
* Multi-contract conversational analysis
* Role-based access control
* Cloud deployment
* Advanced audit logging

---


# ⚖️ Disclaimer

LexiCore AI is an academic/technical project designed to assist with contract analysis and document understanding.

It does **not provide legal advice** and should not replace professional legal review.

---

## 📜 License

This project is intended for academic and educational purposes.

---






