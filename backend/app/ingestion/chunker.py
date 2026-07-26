"""
Step 2b: Split extracted contract text into overlapping semantic chunks.

Overlap matters here: contract clauses often reference definitions or
conditions stated a paragraph earlier, so cutting cleanly at N characters
can sever meaning. RecursiveCharacterTextSplitter tries paragraph/sentence
boundaries first before falling back to hard cuts.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


if __name__ == "__main__":
    sample = """1. TERMINATION. Either party may terminate this Agreement with 30
    days written notice.\n\n2. CONFIDENTIALITY. Each party agrees to keep
    all proprietary information confidential for a period of 5 years."""
    chunks = chunk_text(sample, chunk_size=100, chunk_overlap=20)
    for i, c in enumerate(chunks):
        print(f"--- chunk {i} ---\n{c}\n")
