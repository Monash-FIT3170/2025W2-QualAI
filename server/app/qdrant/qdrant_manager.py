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
    """
    Manages interactions with Qdrant for multiple project collections.
    """

    def __init__(
        self,
        qdrant_url: str = None,
        embedding_model_name: str = "BAAI/bge-base-en-v1.5",
    ):

        print("Initializing QdrantManager...")
        self.qdrant_url = qdrant_url
        if qdrant_url is None:
            self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")

        self.embedding_model_name = embedding_model_name

        # Initialize heavyweight objects once and store as attributes
        self.embedding_model = self._get_embeddings_model()
        self.client = self._get_qdrant_client()
        self.text_splitter = SpacyTextSplitter(
            pipeline="en_core_web_sm", chunk_size=512, chunk_overlap=50
        )

        self.vector_size = (
            self.embedding_model.client.get_sentence_embedding_dimension()
        )

        print("QdrantManager initialized successfully.")

    # --- Main methods to interact with vector database ---

    def augment_prompt(
        self, prompt: str, project_id: int, analysis_mode: str = "default"
    ) -> str:
        """
        Augments a prompt with context from a specific project's collection.
        """
        print("gettin context")
        context_documents = self._get_context(prompt, project_id)

        print(context_documents)

        prompt_context = "No context found."
        if len(context_documents):
            prompt_context = "\n".join(doc.page_content for doc in context_documents)

        match analysis_mode:
            case "default":
                return QDrantTemplates.default_template(prompt, prompt_context)
            case "summary":
                return QDrantTemplates.summary_template(prompt_context)
            case "code_theme":
                return QDrantTemplates.code_theme_template(prompt_context)
            case "outlier":
                return QDrantTemplates.outlier_template(prompt_context)
            case "quote":
                return QDrantTemplates.quote_template(prompt, prompt_context)
            case "research":
                return QDrantTemplates.generate_code_template(prompt, prompt_context)
            case _:
                print(
                    f"Warning: Unknown analysis mode '{analysis_mode}'. Using default template."
                )

        return QDrantTemplates.default_template(prompt, prompt_context)

    def ingest_from_directory(self, project_id: int, transcription_path: str):
        """
        Main ingestion pipeline for a project.

        Args:
            project_id (int): The id of the project, used as the collection name.
            transcription_path (str): The directory containing documents to ingest.
        """
        print("splitting chunks")
        collection_name = project_id
        chunks = self._process_and_split_documents(transcription_path)

        if not chunks:
            print(f"No new document chunks to process for project '{project_id}'.")
            return

        print("creating ids")
        # Generate unique id for each chunk
        chunk_ids = []
        namespace = uuid.NAMESPACE_DNS
        for chunk in chunks:
            # Create a unique ID from the source file and the chunk content
            unique_string = f"{chunk.metadata.get('source', '')}_{chunk.page_content}"
            chunk_uuid = str(uuid.uuid5(namespace, unique_string))
            chunk_ids.append(chunk_uuid)

        # check collection exists
        self._get_collection(collection_name)

        print("inserting documents")
        # insert chunks into qdrant
        Qdrant.from_documents(
            documents=chunks,
            embedding=self.embedding_model,
            url=self.qdrant_url,
            collection_name=collection_name,
            ids=chunk_ids,
            prefer_grpc=False,
            force_recreate=False,  # Set to False to add to an existing collection
        )

    def ingest_from_text(self, project_id: int, text_output: str):
        """
        Process text and ingests it into the Vector Database

        Args:
            text_output (str): The text string that has been transcribed by the software
            project_id (int): The id of the project, used as the collection name.
        """

        """
        For future reference, this can almost certainly be better written, right now im just abusing the fact that the 
        above ingestion from directory function exists.
        """

        # create temporary text file in projects folder (this can be replaced with database methodology when complete)
        db = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        data_path = db.name
        db.close()

        try:
            with open(data_path, "w", encoding="utf-8") as f:
                f.write(text_output)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to write transcription file: {e}"
            )
        # clears qdrant_manager of past project details (we may want to change this at a later date)

        # ingests new transcript data
        if os.path.exists(data_path):
            self.ingest_from_directory(project_id, data_path)
            print(f"Ingested data for project: {project_id}")

            # deletes temporary text file *this can be replaced with supplementary database management tools*
            os.remove(data_path)
        else:
            print(f"Warning: Data path not found, skipping ingestion: {data_path}")

    def clear_collection(self, project_id: int):
        """
        clears the vector database of the project data

        Args:
            project_id (int): The id of the project, used as the collection name.
        """
        print("clear vector start")
        self.client.delete_collection(collection_name=project_id)
        print("clear vector end")

    # --- Private methods to assist with funcitonalities ---

    def _process_and_split_documents(self, transcription_path: str) -> list[Document]:
        """
        Loads text document from a directory and splits them into chunks.

        Args:
            directory_path (str): The path to the txt file

        Returns:
            list[Document]: A list of document chunks.
        """
        print(f"Loading file: '{transcription_path}'...")
        if not os.path.exists(transcription_path):
            print(f"Warning: File '{transcription_path}' not found.")
            return []

        try:
            with open(transcription_path, "r") as file:
                transcription_content = file.read()

            documents = Document(
                page_content=transcription_content,
                metadata={"source": transcription_path},
            )

            return self.text_splitter.split_documents([documents])

        except FileNotFoundError:
            print(f"Error: The file at {transcription_path} was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _get_embeddings_model(self) -> HuggingFaceBgeEmbeddings:
        """Loads the embedding model."""
        print(f"Loading embedding model: '{self.embedding_model_name}'...")
        return HuggingFaceBgeEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False},
        )

    def _get_qdrant_client(self) -> QdrantClient:
        """Initializes the Qdrant client."""
        print(f"Connecting to Qdrant at '{self.qdrant_url}'...")
        return QdrantClient(url=self.qdrant_url, prefer_grpc=False)

    def _get_collection(self, collection_name: int):
        """
        Checks if a collection exists, and creates it if it doesn't.
        """
        try:
            _ = self.client.get_collection(collection_name=collection_name)

        except Exception:
            try:
                print(f"Collection '{collection_name}' not found. Creating...")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size, distance=models.Distance.COSINE
                    ),
                )
                print(f"Collection '{collection_name}' created.")

            except Exception as e:
                print(f"Error checking/creating collection '{collection_name}': {e}")
                raise

    def _get_context(self, prompt: str, project_id: int, k: int = 4) -> list[Document]:
        """
        Performs a similarity search for a given project (collection).
        """
        collection_name = project_id
        self._get_collection(collection_name)

        print(self.client)
        print(collection_name)

        vector_store = Qdrant(
            client=self.client,
            embeddings=self.embedding_model,
            collection_name=collection_name,
        )

        return vector_store.similarity_search(query=prompt, k=k)
