import shutil
import os
import yaml
import argparse

from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pathlib import Path

# CLI Arguments
BASE_DIR = Path(__file__).resolve().parent.parent
# Defaults when imported as a module
VECTORIZE_FAQ = False
VECTORIZE_KB = False

input_faq_file = BASE_DIR / "store" / "faq.yml"
output_faq_dir = BASE_DIR / "store" / "faq_collection"

input_kb_dir = BASE_DIR / "store" / "docs"
output_kb_dir = BASE_DIR / "store" / "kb_collection"

def get_embeddings():

    model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model)

    return embeddings

def _get_collection(name):
    return Chroma(
        collection_name=name,
        persist_directory=f"{BASE_DIR}/store/{name}",
        embedding_function=get_embeddings()
    )

def get_faq_collection():
    return _get_collection("faq_collection")

def get_kb_collection():
    return _get_collection("kb_collection")

def vectorize_faq_data(faq_collection, faq_data):
    print("---- Vectorizing FAQ data...")

    docs = []
    ids = []

    # Convert each question into a Document with metadata
    for faq in faq_data["faqs"]:
        faq_id = faq["id"]
        category = faq["category"]
        answer = faq["answer"]

        for i, question in enumerate(faq["questions"]):
            metadata = {
                "faq_id":faq_id,
                "category": category,
                "answer": answer
            }

            docs.append(Document(
                page_content=question, 
                metadata=metadata,
            ))
            # IDs are in the format "faq_XXX_qX"
            ids.append(f"{faq_id}_q{i}")

    # Add all documents at once
    print("---- Adding documents to FAQ collection...")
    faq_collection.add_documents(docs)

    print(f"---- Added {len(docs)} FAQ entries to vector database.\n")

def vectorize_kb(kb_collection, text_splitter, input_kb_dir):

    print("---- Vectorizing KB Data...")
    all_chunks = []

    # Iterate through every pdf file in docs directory
    for file in input_kb_dir.glob("*.pdf"):
        print(f"---- Loading file: \"{file}\"...")
        loader = PyPDFLoader(file,mode="page",)
        docs = loader.load()

        # Apply splitting
        print("---- Chunking documents...")
        chunk = text_splitter.split_documents(docs)
        all_chunks.extend(chunk)

    # TODO: Add metadata (titles, etc.)

    # Add all documents to collection
    print(f"---- Adding chunks to KB collection...")
    kb_collection.add_documents(all_chunks)

    print(f"---- Added {len(all_chunks)} KB chunks to vector database.\n")

    return all_chunks

if __name__ == "__main__":

    # Parse CLI args only when run as a script (avoid running on import)
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectorize-faq", action="store_true", help="Vectorize FAQ data")
    parser.add_argument("--vectorize-kb", action="store_true", help="Vectorize knowledge base data")
    args = parser.parse_args()

    VECTORIZE_FAQ = args.vectorize_faq
    VECTORIZE_KB = args.vectorize_kb

    # Delete existing FAQ collection if it exists
    if os.path.exists(output_faq_dir):
        shutil.rmtree(output_faq_dir)

    # Delete existing KB collection if it exists
    if os.path.exists(output_kb_dir):
        shutil.rmtree(output_kb_dir)

    # Initialize vector database (Chroma) for FAQ
    embeddings = get_embeddings()
    faq_collection, kb_collection = get_faq_collection(), get_kb_collection()

    if VECTORIZE_FAQ:
        # Parse FAQ YAML
        with open(input_faq_file, "r", encoding="utf-8") as f:
            faq_data = yaml.safe_load(f)

        vectorize_faq_data(faq_collection, faq_data)
    else:
        print("---- FAQ vectorization skipped.\n")

    if VECTORIZE_KB:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500, 
            chunk_overlap = 50 
        )

        # Vectorize KB Data (Chunked)
        texts = vectorize_kb(kb_collection, text_splitter, input_kb_dir)

    else:
        print("---- KB Vectorization skipped.\n")
    
