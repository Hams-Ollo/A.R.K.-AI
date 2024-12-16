"""
Embedding generation utilities for Research Assistant.

This module handles the generation of embeddings for document chunks
using various embedding models.
"""

import logging
from typing import List, Dict, Optional, Union
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import numpy as np
import torch
from tqdm import tqdm
from app.utils import performance_monitor, error_tracker

# Setup logging
logger = logging.getLogger('research_assistant.processing')

class EmbeddingGenerator:
    """Handles generation of embeddings for document chunks."""
    
    @error_tracker.handle_exception()
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        batch_size: int = 32
    ):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the embedding model to use
            device: Device to run the model on ('cuda' or 'cpu')
            batch_size: Batch size for embedding generation
        """
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        
        # Initialize embedding model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': device}
        )
        
        logger.info(f"Initialized EmbeddingGenerator with model {model_name} on {device}")
    
    @performance_monitor.log_execution_time
    @error_tracker.handle_exception()
    def generate_embeddings(
        self,
        documents: List[Document],
        show_progress: bool = True
    ) -> List[Document]:
        """
        Generate embeddings for a list of documents.

        Args:
            documents: List of Document objects
            show_progress: Whether to show progress bar

        Returns:
            Documents with embeddings added to metadata
        """
        try:
            texts = [doc.page_content for doc in documents]
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
            
            # Process in batches
            all_embeddings = []
            
            with tqdm(total=len(texts), disable=not show_progress) as pbar:
                for i in range(0, len(texts), self.batch_size):
                    batch_texts = texts[i:i + self.batch_size]
                    
                    # Generate embeddings for batch
                    batch_embeddings = self.embedding_model.embed_documents(batch_texts)
                    all_embeddings.extend(batch_embeddings)
                    
                    pbar.update(len(batch_texts))
            
            # Add embeddings to documents
            for doc, embedding in zip(documents, all_embeddings):
                doc.metadata["embedding"] = embedding
            
            logger.info(f"Generated embeddings for {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    @performance_monitor.log_execution_time
    @error_tracker.handle_exception()
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Search query text

        Returns:
            Query embedding
        """
        try:
            embedding = self.embedding_model.embed_query(query)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    @performance_monitor.log_execution_time
    @error_tracker.handle_exception()
    def batch_encode_texts(
        self,
        texts: List[str],
        batch_size: Optional[int] = None
    ) -> np.ndarray:
        """
        Encode multiple texts in batches.

        Args:
            texts: List of texts to encode
            batch_size: Optional batch size override

        Returns:
            Array of embeddings
        """
        batch_size = batch_size or self.batch_size
        embeddings = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.embedding_model.embed_documents(batch)
                embeddings.extend(batch_embeddings)
            
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Error in batch encoding: {str(e)}")
            raise
    
    @error_tracker.handle_exception()
    @staticmethod
    def compute_similarity(
        query_embedding: Union[List[float], np.ndarray],
        document_embeddings: Union[List[List[float]], np.ndarray]
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and document embeddings.

        Args:
            query_embedding: Query embedding
            document_embeddings: Document embeddings

        Returns:
            Array of similarity scores
        """
        query_embedding = np.array(query_embedding)
        document_embeddings = np.array(document_embeddings)
        
        # Normalize embeddings
        query_norm = np.linalg.norm(query_embedding)
        doc_norm = np.linalg.norm(document_embeddings, axis=1)
        
        # Compute cosine similarity
        similarities = np.dot(document_embeddings, query_embedding) / (doc_norm * query_norm)
        
        return similarities
