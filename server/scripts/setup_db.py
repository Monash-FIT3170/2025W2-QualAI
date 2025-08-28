import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.vector import setup_qdrant_collection, QDRANT_COLLECTION_NAME
from qdrant_client import QdrantClient
from app.vector import QDRANT_URL


def main():
    """
    Sets up the Qdrant collection and checks if it's empty.
    Exits with code 0 if ingestion should run (collection is new/empty).
    Exits with code 1 if ingestion can be skipped (collection has data).
    """
    is_newly_created = setup_qdrant_collection()
    if is_newly_created:
        print("Collection is new and empty. Proceeding with ingestion.")
        sys.exit(0)
    
    client = QdrantClient(url=QDRANT_URL)
    count = client.count(collection_name=QDRANT_COLLECTION_NAME, exact=True).count
    
    if count == 0:
        print("Collection exists but is empty. Proceeding with ingestion.")
        sys.exit(0)
    else:
        print(f"Collection already contains {count} vectors. Skipping ingestion.")
        sys.exit(1)

if __name__ == "__main__":
    main()