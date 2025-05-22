from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from qdrant_client import QdrantClient

# load the embedding model
model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceBgeEmbeddings(
    model_name = model_name,
    model_kwargs = {'device': 'cpu'},
    encode_kwargs = {'normalize_embeddings': False}
)

url = "http://localhost:6333"
collection_name = "test_db"

client  = QdrantClient(
    url=url,
    prefer_grpc= False
)

print(client)
print("#####################")

db = Qdrant(
    client=client,
    embeddings = embeddings,
    collection_name= collection_name
)

print(db)
print("##################")

query = "What is the late penalty if you team is not an extension"

docs = db.similarity_search_with_score(query=query, k=5)

for i in docs:
    doc, score = i
    print({"score": score, "content": doc.page_content, "metadata": doc.metadata})