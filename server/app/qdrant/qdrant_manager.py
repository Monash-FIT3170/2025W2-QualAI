import os
import tempfile

from fastapi import HTTPException
from qdrant_client import QdrantClient, models
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document
import uuid
from langchain_text_splitters import SpacyTextSplitter
from app.qdrant.qdrant_templates import QDrantTemplates


class QdrantManager:
    def __init__(self, qdrant_url: str = None, embedding_model_name: str = "BAAI/bge-base-en-v1.5"):
        print("Initializing QdrantManager...")
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://qdrant:6333")
        self.embedding_model_name = embedding_model_name
        self.embedding_model = self._get_embeddings_model()
        self.client = self._get_qdrant_client()
        self.text_splitter = SpacyTextSplitter(pipeline="en_core_web_sm", chunk_size=512, chunk_overlap=50)
        self.vector_size = self.embedding_model.client.get_sentence_embedding_dimension()
        print("QdrantManager initialized successfully.")

    def augment_prompt(self, prompt: str, project_id: int, analysis_mode: str = "default") -> str:
        """
        Compose the final instruction template based on analysis_mode.
        For context-driven modes (default/summary/code_theme/outlier/quote) we fetch RAG context.
        For direct modes (summary_direct/explain/rewrite) we operate on the provided text.
        """
        use_context = analysis_mode not in ("summary_direct", "explain", "rewrite")
        prompt_context = "No context found."
        if use_context:
            docs = self._get_context(prompt, project_id)
            if docs:
                prompt_context = "\n".join(doc.page_content for doc in docs)

        match analysis_mode:
            case "default":
                return QDrantTemplates.default_template(prompt, prompt_context)
            case "summary":
                return QDrantTemplates.summary_template(prompt_context)
            case "summary_direct":
                return QDrantTemplates.summary_direct_template(prompt)
            case "code_theme":
                return QDrantTemplates.code_theme_template(prompt_context)
            case "outlier":
                return QDrantTemplates.outlier_template(prompt_context)
            case "quote":
                return QDrantTemplates.quote_template(prompt, prompt_context)
            case "explain":
                return QDrantTemplates.explain_template(prompt)
            case "rewrite":
                return QDrantTemplates.rewrite_template(prompt)
            case _:
                print(f"Warning: Unknown analysis mode '{analysis_mode}'. Using default template.")
                return QDrantTemplates.default_template(prompt, prompt_context)

    def ingest_from_directory(self, project_id: int, transcription_path: str):
        print("splitting chunks")
        collection_name = project_id
        chunks = self._process_and_split_documents(transcription_path)
        if not chunks:
            print(f"No new document chunks to process for project '{project_id}'.")
            return
        print("creating ids")
        chunk_ids = []
        namespace = uuid.NAMESPACE_DNS
        for chunk in chunks:
            unique_string = f"{chunk.metadata.get('source', '')}_{chunk.page_content}"
            chunk_uuid = str(uuid.uuid5(namespace, unique_string))
            chunk_ids.append(chunk_uuid)
        self._get_collection(collection_name)
        print("inserting documents")
        Qdrant.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            url=self.qdrant_url,
            collection_name=collection_name,
            ids=chunk_ids,
            prefer_grpc=False,
            force_recreate=False,
        )

    def ingest_from_text(self, project_id: int, text_output: str):
        db = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        data_path = db.name
        db.close()
        try:
            with open(data_path, "w", encoding="utf-8") as f:
                f.write(text_output)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write transcription file: {e}")
        if os.path.exists(data_path):
            self.ingest_from_directory(project_id, data_path)
            print(f"Ingested data for project: {project_id}")
            os.remove(data_path)
        else:
            print(f"Warning: Data path not found, skipping ingestion: {data_path}")

    def clear_collection(self, project_id: int):
        print("clear vector start")
        self.client.delete_collection(collection_name=project_id)
        print("clear vector end")

    def _process_and_split_documents(self, transcription_path: str) -> list[Document]:
        print(f"Loading file: '{transcription_path}'...")
        if not os.path.exists(transcription_path):
            print(f"Warning: File '{transcription_path}' not found.")
            return []
        try:
            with open(transcription_path, "r") as file:
                transcription_content = file.read()
            documents = Document(page_content=transcription_content, metadata={"source": transcription_path})
            return self.text_splitter.split_documents([documents])
        except FileNotFoundError:
            print(f"Error: The file at {transcription_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _get_embeddings_model(self) -> HuggingFaceBgeEmbeddings:
        print(f"Loading embedding model: '{self.embedding_model_name}'...")
        return HuggingFaceBgeEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False},
        )

    def _get_qdrant_client(self) -> QdrantClient:
        print(f"Connecting to Qdrant at '{self.qdrant_url}'...")
        return QdrantClient(url=self.qdrant_url, prefer_grpc=False)

    def _get_collection(self, collection_name: int):
        try:
            _ = self.client.get_collection(collection_name=collection_name)
        except Exception:
            try:
                print(f"Collection '{collection_name}' not found. Creating...")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
                )
                print(f"Collection '{collection_name}' created.")
            except Exception as e:
                print(f"Error checking/creating collection '{collection_name}': {e}")
                raise

    def _get_context(self, prompt: str, project_id: int, k: int = 4) -> list[Document]:
        collection_name = project_id
        self._get_collection(collection_name)
        vector_store = Qdrant(client=self.client, embeddings=self.embedding_model, collection_name=collection_name)
        return vector_store.similarity_search(query=prompt, k=k)
