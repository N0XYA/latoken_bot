import os
import logging
from typing import List, Dict, Tuple
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from config import OPENAI_API_KEY, VECTOR_DB_DIR, RELEVANT_TOPICS
from scraper import fetch_all_sources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self):
        """Initialize the knowledge base"""
        self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        self.documents = []
        self.index = None
        self.index_path = os.path.join(VECTOR_DB_DIR, "faiss_index")
        self.document_path = os.path.join(VECTOR_DB_DIR, "documents.npy")

    def load_or_create_index(self):
        """Load an existing index or create a new one"""
        if os.path.exists(self.index_path) and os.path.exists(self.document_path):
            logger.info("Loading existing index and documents")
            self.index = faiss.read_index(self.index_path)
            self.documents = np.load(self.document_path, allow_pickle=True).tolist()
            return True
        else:
            logger.info("No existing index found. Creating new index.")
            return False

    def is_question_relevant(self, question: str) -> bool:
        """Check if a question is relevant to LATOKEN topics"""
        question_lower = question.lower()
        return any(topic in question_lower for topic in RELEVANT_TOPICS)

    def create_index(self):
        """Create a new index from source documents"""
        logger.info("Creating new index from sources")

        # Fetch content from all sources
        source_contents = fetch_all_sources()

        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Process each source
        all_documents = []
        for source, content in source_contents.items():
            chunks = text_splitter.split_text(content)
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={"source": source, "chunk_id": i}
                )
                all_documents.append(doc)

        logger.info(f"Created {len(all_documents)} documents from sources")

        # Create embeddings and index
        embeddings_list = []
        self.documents = all_documents

        batch_size = 20  # Process in batches to avoid rate limits
        for i in range(0, len(all_documents), batch_size):
            batch = all_documents[i:i+batch_size]
            texts = [doc.page_content for doc in batch]
            batch_embeddings = self.embeddings.embed_documents(texts)
            embeddings_list.extend(batch_embeddings)
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(all_documents)-1)//batch_size + 1}")

        # Create FAISS index
        vector_dimension = len(embeddings_list[0])
        self.index = faiss.IndexFlatL2(vector_dimension)
        embeddings_array = np.array(embeddings_list).astype('float32')
        self.index.add(embeddings_array)

        # Save index and documents
        faiss.write_index(self.index, self.index_path)
        np.save(self.document_path, self.documents)

        logger.info(f"Index created with {self.index.ntotal} vectors")

    def query(self, question: str, top_k: int = 5) -> Tuple[List[str], List[Dict]]:
        """
        Query the knowledge base for relevant documents

        Args:
            question (str): The question to search for
            top_k (int): Number of results to return

        Returns:
            Tuple[List[str], List[Dict]]: Retrieved texts and their metadata
        """
        # Check if question is relevant
        if not self.is_question_relevant(question):
            return (["I can only answer questions about LATOKEN, its culture, or the hackathon."], 
                    [{"source": "filter", "chunk_id": 0}])

        # Embed the question
        question_embedding = self.embeddings.embed_query(question)
        question_embedding_array = np.array([question_embedding]).astype('float32')

        # Search the index
        scores, indices = self.index.search(question_embedding_array, top_k)

        # Retrieve documents
        retrieved_docs = []
        retrieved_metadata = []

        for idx in indices[0]:
            if idx != -1:  # FAISS may return -1 if there are not enough results
                doc = self.documents[idx]
                retrieved_docs.append(doc.page_content)
                retrieved_metadata.append(doc.metadata)

        return retrieved_docs, retrieved_metadata


def initialize_knowledge_base():
    """Initialize and return the knowledge base"""
    kb = KnowledgeBase()
    if not kb.load_or_create_index():
        kb.create_index()
    return kb


if __name__ == "__main__":
    # Test the knowledge base
    kb = initialize_knowledge_base()

    test_questions = [
        "Why does LATOKEN help people study and buy assets?",
        "What is the Sugar Cookie test for?",
        "Why is a Wartime CEO needed?",
        "When is stress useful and when is it harmful?",
        "What is the weather in New York today?"  # Irrelevant question
    ]

    for question in test_questions:
        print(f"Question: {question}")
        docs, metadata = kb.query(question)
        print(f"Found {len(docs)} relevant documents")
        for i, (doc, meta) in enumerate(zip(docs, metadata)):
            print(f"Document {i+1} from {meta['source']}:")
            print(doc[:200] + "..." if len(doc) > 200 else doc)
            print("-" * 40)
        print("=" * 80)
