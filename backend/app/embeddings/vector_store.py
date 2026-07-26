"""
Step 3: Embed text chunks and store/query them in a FAISS index.

One ContractVectorStore instance = one contract's searchable index.
For the MVP we keep it in-memory + save to disk; swap for a persistent
per-document index (e.g. keyed by contract_id) once multi-document
support / MySQL persistence is added.
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good enough for MVP


class ContractVectorStore:
    def __init__(self):
        self.model = SentenceTransformer(_MODEL_NAME)
        self.index: faiss.IndexFlatL2 | None = None
        self.chunks: list[str] = []

    def build(self, chunks: list[str]):
        self.chunks = chunks
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def search(self, query: str, top_k: int = 4) -> list[str]:
        if self.index is None:
            raise ValueError("Index not built yet. Call build() first.")

        query_vec = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_vec, top_k)

        return [self.chunks[i] for i in indices[0] if i != -1]


if __name__ == "__main__":
    store = ContractVectorStore()
    store.build([
        "Either party may terminate this Agreement with 30 days written notice.",
        "Each party agrees to keep proprietary information confidential for 5 years.",
        "Payment shall be made within 30 days of invoice receipt.",
    ])
    results = store.search("How much notice is needed to end the contract?", top_k=2)
    for r in results:
        print("-", r)
