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
from app.utils import performance_monitor, error_tracker, cli_logger

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
        
        cli_logger.info("Initializing ChromaDB...", context='database',
                       details={"persist_dir": persist_directory})
        
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
        
        cli_logger.success("ChromaDB initialized successfully!", context='database',
                         details={"collection": collection_name})
        
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
            cli_logger.info("Adding documents to vector store...", context='upload',
                           details={"doc_count": len(documents)})
            
            if ids is None:
                ids = [f"doc_{i}_{datetime.utcnow().timestamp()}" for i in range(len(documents))]
            
            if metadatas is None:
                metadatas = [{"timestamp": datetime.utcnow().isoformat()} for _ in documents]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            cli_logger.success("Documents added successfully!", context='upload')
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            return ids
            
        except Exception as e:
            cli_logger.error(f"Error adding documents: {str(e)}")
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
            cli_logger.info("Performing similarity search...", context='search',
                           details={"query": query, "n_results": n_results})
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=metadata_filter
            )
            
            cli_logger.success("Search completed", context='search',
                              details={"results_found": len(results['ids'][0])})
            
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
            cli_logger.error(f"Error performing similarity search: {str(e)}")
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
            cli_logger.info("Deleting documents from vector store...", context='delete',
                           details={"doc_count": len(ids)})
            
            self.collection.delete(ids=ids)
            
            cli_logger.success("Documents deleted successfully!", context='delete')
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
        except Exception as e:
            cli_logger.error(f"Error deleting documents: {str(e)}")
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
            cli_logger.info("Retrieving document from vector store...", context='retrieve',
                           details={"doc_id": doc_id})
            
            result = self.collection.get(ids=[doc_id])
            if result['ids']:
                cli_logger.success("Document retrieved successfully!", context='retrieve')
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            cli_logger.error("Document not found", context='retrieve')
            return None
        except Exception as e:
            cli_logger.error(f"Error retrieving document: {str(e)}")
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
            cli_logger.info("Updating document in vector store...", context='update',
                           details={"doc_id": doc_id})
            
            if metadata is None:
                metadata = {"updated_at": datetime.utcnow().isoformat()}
            
            self.collection.update(
                ids=[doc_id],
                documents=[document],
                metadatas=[metadata]
            )
            
            cli_logger.success("Document updated successfully!", context='update')
            logger.info(f"Updated document {doc_id}")
        except Exception as e:
            cli_logger.error(f"Error updating document: {str(e)}")
            logger.error(f"Error updating document {doc_id}: {str(e)}")
            raise
