"""
ChromaDB Vector Store Implementation for Research Assistant.

This module provides a wrapper around ChromaDB for vector storage and retrieval,
specifically designed for academic document management and citation tracking.
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging
from typing import List, Dict, Optional, Any
import os
from datetime import datetime
from app.utils import performance_monitor, error_tracker

# Setup logging
logger = logging.getLogger('research_assistant.vector_store')

class ChromaDocStore:
    """Vector store implementation using ChromaDB."""
    
    @error_tracker.handle_exception()
    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "research_documents",
        embedding_function: Optional[Any] = None
    ):
        """
        Initialize the ChromaDB document store.

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
            embedding_function: Custom embedding function (optional)
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Setup embedding function
        self.embedding_function = embedding_function or embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"created_at": datetime.utcnow().isoformat()}
        )
        
        logger.info(f"Initialized ChromaDB store at {persist_directory}")
    
    @performance_monitor.log_execution_time
    @error_tracker.handle_exception()
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        try:
            if ids is None:
                ids = [f"doc_{i}_{datetime.utcnow().timestamp()}" for i in range(len(documents))]
            
            if metadatas is None:
                metadatas = [{"timestamp": datetime.utcnow().isoformat()} for _ in documents]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    @performance_monitor.log_execution_time
    @error_tracker.handle_exception()
    def similarity_search(
        self,
        query: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform similarity search for a query.

        Args:
            query: Search query
            n_results: Number of results to return
            metadata_filter: Optional metadata filter

        Returns:
            List of matching documents with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=metadata_filter
            )
            
            logger.info(f"Performed similarity search for query: {query}")
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            raise
    
    @error_tracker.handle_exception()
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store.

        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    @error_tracker.handle_exception()
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Retrieve a specific document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document data if found, None otherwise
        """
        try:
            result = self.collection.get(ids=[doc_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {str(e)}")
            raise
    
    @error_tracker.handle_exception()
    def update_document(
        self,
        doc_id: str,
        document: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Update an existing document.

        Args:
            doc_id: Document ID
            document: New document text
            metadata: Optional new metadata
        """
        try:
            if metadata is None:
                metadata = {"updated_at": datetime.utcnow().isoformat()}
            
            self.collection.update(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            logger.info(f"Updated document {doc_id}")
        except Exception as e:
            logger.error(f"Error updating document {doc_id}: {str(e)}")
            raise
