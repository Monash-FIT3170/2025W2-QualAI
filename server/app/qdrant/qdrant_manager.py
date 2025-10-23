import os
import tempfile
from collections import defaultdict
from typing import Iterable, Tuple

from fastapi import HTTPException
from qdrant_client import QdrantClient, models
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document
import uuid
from langchain_text_splitters import SpacyTextSplitter
from app.qdrant.qdrant_templates import QDrantTemplates
from app.config import config
from app.database import Highlight


class QdrantManager:
    """
    Manages interactions with Qdrant for multiple project collections.
    """

    def __init__(
        self,
        qdrant_url: str = None,
        embedding_model_name: str = "BAAI/bge-base-en-v1.5",
        highlight_store: Highlight | None = None,
    ):

        print("Initializing QdrantManager...")
        self.qdrant_url = qdrant_url
        if qdrant_url is None:
            self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")

        self.embedding_model_name = embedding_model_name
        try:
            self.highlight_store = highlight_store or Highlight(config.DB_PATH)
        except Exception as exc:
            print(f"Warning: Failed to initialise highlight store: {exc}")
            self.highlight_store = None

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

        highlight_context, ignore_snippets = self._prepare_highlight_context(
            project_id
        )

        if ignore_snippets:
            prompt_context = self._remove_ignored_snippets(prompt_context, ignore_snippets)

        if highlight_context:
            prompt_context = f"{highlight_context}\n\nADDITIONAL CONTEXT:\n{prompt_context}"

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
                return (QDrantTemplates.quote_template(prompt, prompt_context),)
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

    def _prepare_highlight_context(
        self, project_id: int, max_total: int = 12
    ) -> Tuple[str, list[str]]:
        """
        Builds a formatted highlight priority block and collects ignored snippets.
        """
        if self.highlight_store is None:
            return "", []

        try:
            highlights = self.highlight_store.get_project_highlights_with_metadata(
                project_id
            )
        except Exception as exc:
            print(f"Warning: Failed to load highlights for project {project_id}: {exc}")
            return "", []

        if not highlights:
            return "", []

        ignore_snippets = [
            h["snippet"]
            for h in highlights
            if h.get("weight", 0) <= 1 and h.get("snippet")
        ]

        priority_items = [
            h for h in highlights if h.get("weight", 0) > 1 and h.get("snippet")
        ]

        if not priority_items and not ignore_snippets:
            return "", []

        weight_labels = {
            5: "Critical",
            4: "High",
            3: "Medium",
            2: "Low",
            1: "Ignore",
        }

        # Sort by weight (desc), then by transcription name and start offset for stability
        priority_items.sort(
            key=lambda h: (-h.get("weight", 0), h.get("transcription_name", ""), h.get("start_offset", 0))
        )

        # Cap the amount of data per weight to keep prompts concise
        per_weight_cap = {5: 5, 4: 3, 3: 2, 2: 1}
        counts = defaultdict(int)
        selected: list[dict] = []
        for item in priority_items:
            weight = item.get("weight", 0)
            cap = per_weight_cap.get(weight, 1)
            if counts[weight] >= cap:
                continue
            counts[weight] += 1
            selected.append(item)
            if len(selected) >= max_total:
                break

        if not selected and not ignore_snippets:
            return "", ignore_snippets

        lines: list[str] = [
            "HIGHLIGHT PRIORITY CONTEXT",
            "The user marked certain transcript segments with importance levels. "
            "Prioritise higher weight excerpts and down-weight lower ones accordingly.",
        ]

        current_weight = None
        for highlight in selected:
            weight = highlight.get("weight", 0)
            if weight != current_weight:
                label = weight_labels.get(weight, f"Weight {weight}")
                lines.append(f"[{label.upper()} PRIORITY]")
                current_weight = weight

            snippet = self._condense_snippet(highlight.get("snippet", ""), max_length=220)
            label = highlight.get("highlighter_label") or weight_labels.get(weight, "Highlight")
            source = highlight.get("transcription_name", "Unknown transcript")
            comment = highlight.get("comment")

            entry = f"- {label} → \"{snippet}\" (source: {source})"
            if comment:
                entry += f" [Note: {comment}]"
            lines.append(entry)

        if ignore_snippets:
            lines.append(
                "[IGNORE PRIORITY] The following segments were flagged to be ignored. "
                "If they appear elsewhere in the context, treat them as out-of-scope."
            )

        return "\n".join(lines), ignore_snippets

    @staticmethod
    def _condense_snippet(snippet: str, max_length: int = 220) -> str:
        """
        Normalises whitespace and trims long snippets for prompt readability.
        """
        condensed = " ".join(snippet.split())
        if len(condensed) <= max_length:
            return condensed
        return condensed[: max_length - 1].rstrip() + "…"

    @staticmethod
    def _remove_ignored_snippets(context: str, ignore_snippets: Iterable[str]) -> str:
        """
        Removes or masks snippets that the user deliberately marked as 'Ignore'.
        """
        if not context or not ignore_snippets:
            return context

        masked_context = context
        for snippet in ignore_snippets:
            if not snippet:
                continue
            condensed = " ".join(snippet.split())
            for candidate in {snippet.strip(), condensed}:
                if not candidate:
                    continue
                masked_context = masked_context.replace(candidate, "[IGNORED SEGMENT]")

        return masked_context

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
