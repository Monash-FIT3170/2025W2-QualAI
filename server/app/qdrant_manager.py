import os
from typing import List

from qdrant_client import QdrantClient, models, AsyncQdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document
import uuid
from langchain_text_splitters import SpacyTextSplitter


class QdrantManager:
    """
    Manages interactions with Qdrant for multiple project collections.
    """

    def __init__(self, qdrant_url: str = os.getenv("QDRANT_URL", "http://qdrant:6333"), embedding_model_name: str = "BAAI/bge-base-en-v1.5"):
        print("Initializing QdrantManager...")
        self.qdrant_url = qdrant_url
        self.embedding_model_name = embedding_model_name

        # Initialize heavyweight objects once and store as attributes
        self.embedding_model = self._get_embeddings_model()
        self.client = self._get_qdrant_client()
        self.text_splitter = SpacyTextSplitter(
            pipeline="en_core_web_sm",
            chunk_size=512,
            chunk_overlap=50
        )

        self.vector_size = self.embedding_model.client.get_sentence_embedding_dimension()

        print("QdrantManager initialized successfully.")

    # --- Main methods to interact with vector database ---

    def augment_prompt(self, prompt: str, project_name: str) -> str:
        """
        Augments a prompt with context from a specific project's collection.
        """
        context_documents = self._get_context(prompt, project_name, k = 3)
        if not context_documents:
            prompt_context = "No context found."
        else:
            prompt_context = "\n".join(
                doc.page_content for doc in context_documents)

        metaprompt = f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert AI research assistant designed for qualitative analysis of interview transcripts. Your responses must be objective, precise, and strictly grounded in the provided context.
            </ROLE>
            <PROCESS>
                <STEP_1>Analyze the user's question to determine its nature.</STEP_1>
                <STEP_2>
                    If the question is conversational (e.g., greetings, pleasantries), provide a brief, polite response. Do not consult the context.
                </STEP_2>
                <STEP_3>
                    If the question is a research query, perform a detailed analysis of the <CONTEXT> to formulate your answer. Your answer must be synthesized directly from this information. Support your claims with direct quotes where appropriate.
                </STEP_3>
            </PROCESS>
            <RULES>
                <RULE id="1">NEVER use information outside of the provided <CONTEXT> block.</RULE>
                <RULE id="2" importance="CRITICAL">If the answer to a research query cannot be found in the <CONTEXT>, you must respond *only* with the phrase: "I could not find information on this topic in the provided transcript."</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <QUESTION>
                {prompt.strip()}
            </QUESTION>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <ANSWER>
        """
        return metaprompt

    def ingest_from_directory(self, project_name: str, transcription_path: str):
        """
        Main ingestion pipeline for a project.

        Args:
            project_name (str): The name of the project, used as the collection name.
            transcription_path (str): The directory containing documents to ingest.
        """
        print("splitting chunks")
        collection_name = project_name
        chunks = self._process_and_split_documents(transcription_path)

        if not chunks:
            print(
                f"No new document chunks to process for project '{project_name}'.")
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
            force_recreate=False  # Set to False to add to an existing collection
        )

    # --- Private methods to assist with funcitonalities ---

    def _process_and_split_documents(self, transcription_path: str) -> List[Document]:
        """
        Loads text document from a directory and splits them into chunks.

        Args:
            directory_path (str): The path to the txt file

        Returns:
            List[Document]: A list of document chunks.
        """
        print(f"Loading file: '{transcription_path}'...")
        if not os.path.exists(transcription_path):
            print(
                f"Warning: File '{transcription_path}' not found.")
            return []

        try:
            with open(transcription_path, "r") as file:
                transcription_content = file.read()

            documents = Document(
                page_content=transcription_content,
                metadata={"source": transcription_path}
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

    def _get_collection(self, collection_name: str):
        """
        Checks if a collection exists, and creates it if it doesn't.
        """
        try:
            collections_list = self.client.get_collections().collections
            collection_names = [c.name for c in collections_list]

            if collection_name not in collection_names:
                print(f"Collection '{collection_name}' not found. Creating...")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"Collection '{collection_name}' created.")
        except Exception as e:
            print(
                f"Error checking/creating collection '{collection_name}': {e}")
            raise

    def _get_context(self, prompt: str, project_name: str, k: int = 4) -> List[Document]:
        """
        Performs a similarity search for a given project (collection).
        """
        collection_name = project_name
        self._get_collection(collection_name)

        vector_store = Qdrant(
            client=self.client,
            embeddings=self.embedding_model,
            collection_name=collection_name,
        )

        return vector_store.similarity_search(query=prompt, k=k)
