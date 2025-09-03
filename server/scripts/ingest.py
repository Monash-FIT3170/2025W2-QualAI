import os
import time
import spacy
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import SpacyTextSplitter
from langchain_community.vectorstores import Qdrant
import hashlib
from qdrant_client.http import models as rest_models

# We need to import the functions from the 'app' module.
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.vector import get_embeddings_model, get_qdrant_client, QDRANT_URL, QDRANT_COLLECTION_NAME


DOCUMENTS_DIRECTORY = "/app/papers"


def load_and_split_documents(directory_path: str):
    """Loads PDF documents from a directory and splits them into chunks using SpaCy."""
    print(f"Loading documents from '{directory_path}'...")
    if not os.path.exists(directory_path) or not os.listdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found or is empty.")
        print("Please make sure you have a 'papers' directory in './server/app/' and added PDF files to it.")
        return []

    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()

    if not documents:
        print("No documents could be loaded. Aborting.")
        return []

    print(f"Loaded {len(documents)} document(s).")
    print("Splitting documents into chunks with SpaCy...")

    text_splitter = SpacyTextSplitter(
        pipeline="en_core_web_sm",
        chunk_size=512,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Successfully split documents into {len(chunks)} chunks.")
    return chunks



def create_and_store_vectors(chunks):
    """Creates embeddings for document chunks and stores them in per-file Qdrant collections.

    Assumes each chunk has metadata with 'source' (file path) and possibly 'page'. We will group by source filename
    and index each group into its own collection named 'paper_<slug>'.
    """
    if not chunks:
        print("No chunks to process")
        return

    print("Connecting to vector store and indexing documents (per-file collections)...")
    start_time = time.time()

    client = get_qdrant_client()
    embeddings = get_embeddings_model()

    # Group chunks by source filename
    from collections import defaultdict
    groups = defaultdict(list)
    for d in chunks:
        src = (d.metadata.get('source') or '').split('/')[-1]
        if not src:
            src = 'unknown'
        groups[src].append(d)

    for src_filename, docs in groups.items():
        # Build a safe collection name
        base = os.path.splitext(src_filename)[0]
        slug = base.replace(' ', '_').replace('/', '_').replace(':', '_')
        collection_name = f"paper_{slug}"
        print(f"Indexing {len(docs)} chunks into collection '{collection_name}'")

        # Ensure collection exists with correct vector size
        dim = embeddings.client.get_sentence_embedding_dimension()
        try:
            existing = client.get_collection(collection_name)
        except Exception:
            client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "size": dim,
                    "distance": "Cosine"
                }
            )

        store = Qdrant(client=client, collection_name=collection_name, embeddings=embeddings)
        store.add_documents(documents=docs)

    end_time = time.time()
    print(f"All collections indexed in {end_time - start_time:.2f} seconds.")





def main():
    """Main function to run the entire ingestion pipeline."""    
    document_chunks = load_and_split_documents(DOCUMENTS_DIRECTORY)
    create_and_store_vectors(document_chunks)

if __name__ == "__main__":
    main()