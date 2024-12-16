"""
Manual test script for Research Assistant core functionality.
This script demonstrates the basic workflow of the application.
"""

import os
from pathlib import Path
import logging
from app.utils.logging_config import setup_logging
from app.backend.processing.document_processor import DocumentProcessor
from app.backend.processing.embedding_generator import EmbeddingGenerator
from app.backend.vector_store.chroma_store import ChromaDocStore

# Setup logging
setup_logging(log_level="INFO")
logger = logging.getLogger('research_assistant.test')

def main():
    # Initialize components
    logger.info("Initializing components...")
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    test_docs_dir = data_dir / "test_documents"
    vector_store_dir = data_dir / "vector_store"
    
    # Create directories if they don't exist
    data_dir.mkdir(exist_ok=True)
    test_docs_dir.mkdir(exist_ok=True)
    vector_store_dir.mkdir(exist_ok=True)
    
    # Initialize components
    doc_processor = DocumentProcessor(
        chunk_size=500,
        chunk_overlap=50
    )
    
    embedding_generator = EmbeddingGenerator(
        batch_size=16
    )
    
    vector_store = ChromaDocStore(
        persist_directory=str(vector_store_dir),
        collection_name="test_collection"
    )
    
    logger.info("Components initialized successfully")
    
    # Test document processing
    logger.info("Testing document processing...")
    
    # Get all supported files
    supported_extensions = tuple(doc_processor.SUPPORTED_FORMATS.keys())
    test_files = []
    for ext in supported_extensions:
        test_files.extend(test_docs_dir.glob(f"*{ext}"))
    
    if not test_files:
        logger.warning(f"No supported files found in test_documents directory")
        logger.info(f"Please add files with these extensions to: {test_docs_dir}")
        logger.info(f"Supported formats: {', '.join(supported_extensions)}")
        return
    
    # Process each file
    for file_path in test_files:
        logger.info(f"\nProcessing {file_path.name}...")
        
        try:
            # Process document
            chunks, metadata = doc_processor.process_document(str(file_path))
            logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
            logger.info(f"Metadata: {metadata}")
            
            # Generate embeddings
            chunks_with_embeddings = embedding_generator.generate_embeddings(
                chunks,
                show_progress=True
            )
            logger.info("Generated embeddings for all chunks")
            
            # Store in vector store
            documents = [chunk.page_content for chunk in chunks_with_embeddings]
            metadatas = [chunk.metadata for chunk in chunks_with_embeddings]
            
            vector_store.add_documents(
                documents=documents,
                metadatas=metadatas
            )
            logger.info("Added documents to vector store")
            
            # Test search
            test_query = "What is the main topic of this document?"
            results = vector_store.similarity_search(
                query=test_query,
                n_results=3
            )
            
            logger.info("\nSearch Results:")
            for i, result in enumerate(results, 1):
                logger.info(f"\nResult {i}:")
                logger.info(f"Content: {result['document'][:200]}...")
                logger.info(f"Metadata: {result['metadata']}")
                logger.info(f"Distance: {result['distance']}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            continue

if __name__ == "__main__":
    main()
