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

    def augment_prompt(self, prompt: str, project_name: str, analysis_mode: str = "default") -> str:
        """
        Augments a prompt with context from a specific project's collection.
        """
        context_documents = self._get_context(prompt, project_name)
        if not context_documents:
            prompt_context = "No context found."
        else:
            prompt_context = "\n".join(
                doc.page_content for doc in context_documents)
            

        templates = {
            "default": self._get_default_template(prompt, prompt_context),
            "summary": self._get_summary_template(prompt, prompt_context),
            "code_theme": self._get_code_theme_template(prompt, prompt_context),
            "outlier": self._get_outlier_template(prompt, prompt_context),
            "quote": self._get_quote_template(prompt, prompt_context),
            }

        # Use default template if mode not found
        if analysis_mode not in templates:
            print(f"Warning: Unknown analysis mode '{analysis_mode}'. Using default template.")
            analysis_mode = "default"

        return templates[analysis_mode]

    def _get_default_template(self, prompt: str, prompt_context: str) -> str:
        """Returns the default metaprompt template."""
        return f"""
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

    def _get_summary_template(self, prompt: str, prompt_context: str) -> str:
        """Returns the summary mode metaprompt template."""
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert research assistant specializing in creating concise summaries of qualitative data.
            </ROLE>
            <TASK>
                Create a brief, high-level summary of the key points in the provided context.
                Focus on the main themes, findings, and conclusions.
                Keep your summary concise (3-5 sentences maximum).
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Do not include detailed analysis or extensive quotes.</RULE>
                <RULE id="3">If the context is insufficient, state: "I could not find enough information to create a summary."</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <SUMMARY>
        """

    def _get_code_theme_template(self, prompt: str, prompt_context: str) -> str:
        """Returns the code/theme mode metaprompt template."""
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert qualitative researcher specializing in thematic analysis and coding.
            </ROLE>
            <TASK>
                Analyze the provided context to identify and extract key codes and themes.
                For each code/theme:
                1. Provide a clear label
                2. Include specific evidence from the text with direct quotes
                3. Note the frequency or prevalence of the theme
                4. Explain the significance of the theme

                Structure your response with clear headings for each theme.
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Support each theme with at least one direct quote.</RULE>
                <RULE id="3">If no clear themes emerge, state: "I could not identify distinct themes in this content."</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <THEMATIC_ANALYSIS>
        """

    def _get_outlier_template(self, prompt: str, prompt_context: str) -> str:
        """Returns the outlier mode metaprompt template."""
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert research assistant specializing in identifying unusual or unexpected patterns in qualitative data.
            </ROLE>
            <TASK>
                Analyze the provided context to identify any outliers, anomalies, or unexpected findings.
                For each outlier:
                1. Clearly describe what makes it unusual
                2. Provide the specific evidence from the text
                3. Explain why it stands out from the rest of the content
                4. Suggest possible interpretations or implications

                Structure your response with clear headings for each outlier.
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Support each outlier identification with specific evidence.</RULE>
                <RULE id="3">If no outliers are found, state: "I could not identify any significant outliers in this content."</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <OUTLIER_ANALYSIS>
        """

    def _get_quote_template(self, prompt: str, prompt_context: str) -> str:
        """Returns the quote mode metaprompt template."""
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert research assistant specializing in finding and organizing relevant quotes from qualitative data.
            </ROLE>
            <TASK>
                Based on the user's query about a specific theme or topic, find all relevant quotes from the provided context.
                For each quote:
                1. Include the exact text from the context
                2. Note the speaker if available
                3. Provide a brief explanation of how it relates to the theme

                Organize the quotes by sub-themes or patterns that emerge.
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Include exact quotes, do not paraphrase.</RULE>
                <RULE id="3">If no relevant quotes are found, state: "I could not find quotes related to this theme in the provided content."</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <USER_QUERY>
                {prompt.strip()}
            </USER_QUERY>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <RELEVANT_QUOTES>
        """

    def ingest_from_directory(self, project_name: str, transcription_name: str, transcription_path: str):
        """
        Main ingestion pipeline for a project.

        Args:
            project_name (str): The name of the project, used as the collection name.
            transcription_path (str): The directory containing documents to ingest.
        """
        print("splitting chunks")
        collection_name = project_name
        chunks = self._process_and_split_documents(transcription_path, project_name)

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

    def ingest_from_text(self, project_name: str, transcription_name: str, text_output: str):
        """
        Process text and ingests it into the Vector Database

        Args:
            text_output (str): The text string that has been transcribed by the software
            project_name (str): The name of the project, used as the collection name.
        """

        """
        For future reference, this can almost certainly be better written, right now im just abusing the fact that the 
        above ingestion from directory function exists.
        """
        
        #create temporary text file in projects folder (this can be replaced with database methodology when complete)

        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__),  "projects", "temporaryTranscriptIngestionFile.txt"))

        if not os.path.exists(data_path):
            f = open(data_path, "x")
            
        try:
            with open(data_path, "w", encoding="utf-8") as f:
                f.write(text_output)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to write transcription file: {e}")
        
        #clears qdrant_manager of past project details (we may want to change this at a later date)
        

        #ingests new transcript data
        if os.path.exists(data_path):
            self.ingest_from_directory(
                project_name, data_path)
            print(f"Ingested data for project: {project_name}")

            #deletes temporary text file *this can be replaced with supplementary database management tools*
            os.remove(data_path)
        else:
            print(f"Warning: Data path not found, skipping ingestion: {data_path}")

    def clear_collection(self, project_name: str):
        """
        clears the vector database of the project data 

        Args:
            project_name (str): The name of the project, used as the collection name.
        """
        print("clear vector start")
        self.client.delete_collection(
            collection_name = project_name
        )
        print("clear vector end")



    def clear_filtered_metadata(project_name: str, metadata_type: str, metadata_label):
        self.client.delete(
        collection_name=project_name,
        filter=models.Filter(
        must=[models.FieldCondition(key=metadata_type, match=models.MatchValue(value=metadata_label))]
        )
)

    
    

    # --- Private methods to assist with funcitonalities ---

    def _process_and_split_documents(self, transcription_path: str, project_name: str, transcript_name: str) -> List[Document]:
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
                metadata={
                    "source": transcription_path,
                    "transcription_id": transcript_name,
                    "project_id": project_name}
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
    
    
