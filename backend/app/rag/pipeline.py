"""
Step 4: Tie retrieval + generation together.

This is the heart of the system: given a user question, retrieve the most
relevant chunks from the contract's vector store, then ask Gemini to answer
using ONLY those chunks. This is what keeps answers grounded instead of
hallucinated.
"""
import os

import google.generativeai as genai
from dotenv import load_dotenv

from app.embeddings.vector_store import ContractVectorStore

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_SYSTEM_PROMPT = """You are a legal contract assistant. Answer the user's \
question using ONLY the contract excerpts provided below. Do not use \
outside knowledge. If the excerpts don't contain enough information to \
answer, say so explicitly rather than guessing.

Contract excerpts:
{context}

Question: {question}

Answer clearly and cite which excerpt(s) you used."""


class RAGPipeline:
    def __init__(self, vector_store: ContractVectorStore):
        self.vector_store = vector_store
        self.model = genai.GenerativeModel("gemini-flash-latest")

    def answer(self, question: str, top_k: int = 4) -> dict:
        relevant_chunks = self.vector_store.search(question, top_k=top_k)
        context = "\n\n---\n\n".join(relevant_chunks)

        prompt = _SYSTEM_PROMPT.format(context=context, question=question)
        response = self.model.generate_content(prompt)

        return {
            "answer": response.text,
            "sources": relevant_chunks,
        }


if __name__ == "__main__":
    # Manual end-to-end test (needs GEMINI_API_KEY set in .env):
    #   python -m app.rag.pipeline
    store = ContractVectorStore()
    store.build([
        "Either party may terminate this Agreement with 30 days written notice.",
        "Each party agrees to keep proprietary information confidential for 5 years.",
        "Payment shall be made within 30 days of invoice receipt.",
    ])
    pipeline = RAGPipeline(store)
    result = pipeline.answer("How much notice do I need to give to cancel?")
    print("ANSWER:", result["answer"])
    print("SOURCES:", result["sources"])
