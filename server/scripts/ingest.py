import os
import time
import spacy
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import SpacyTextSplitter
from langchain_community.vectorstores import Qdrant
import hashlib

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
    """Creates embeddings for document chunks and stores them in Qdrant."""
    if not chunks:
        print("No chunks to process")
        return

    print("Connecting to vector store and indexing documents...")
    start_time = time.time()
    
    client = get_qdrant_client()
    embeddings = get_embeddings_model()
    
    # Get the vector store object for an existing collection
    qdrant_store = Qdrant(
        client=client, 
        collection_name=QDRANT_COLLECTION_NAME, 
        embeddings=embeddings
    )

    #Unique id for each chunk so we can run ingest multiple times



    qdrant_store.add_documents(documents=chunks)

    end_time = time.time()
    print(f"Vector store updated and documents indexed in {end_time - start_time:.2f} seconds.")





def main():
    """Main function to run the entire ingestion pipeline."""    
    document_chunks = load_and_split_documents(DOCUMENTS_DIRECTORY)
    create_and_store_vectors(document_chunks)

if __name__ == "__main__":
    main()