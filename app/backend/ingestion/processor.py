import os
from typing import List, Dict, Any
from datetime import datetime
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import GroqEmbeddings
import chromadb
from tqdm import tqdm
from ..models import Document, DocumentChunk
from ..database import SessionLocal
import base64
import numpy as np

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.embeddings = GroqEmbeddings(
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )
        self.db = SessionLocal()

    def process_pdf(self, file_path: str, metadata: Dict[str, Any]) -> Document:
        """Process a PDF file and store its contents in the database."""
        try:
            # Create document record
            doc = Document(
                title=metadata.get("title", os.path.basename(file_path)),
                author=metadata.get("author"),
                publication_date=metadata.get("publication_date"),
                file_path=file_path,
                file_type="pdf"
            )
            self.db.add(doc)
            self.db.commit()

            # Extract text from PDF
            pdf_reader = PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)

            # Process chunks with progress bar
            for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
                # Generate embedding
                embedding = self.embeddings.embed_query(chunk)
                
                # Convert embedding to base64 string for storage
                embedding_bytes = np.array(embedding).tobytes()
                embedding_b64 = base64.b64encode(embedding_bytes).decode('utf-8')

                # Create chunk record
                doc_chunk = DocumentChunk(
                    document_id=doc.id,
                    content=chunk,
                    embedding=embedding_b64,
                    chunk_index=i,
                    page_number=i // 2  # Approximate page number
                )
                self.db.add(doc_chunk)

            self.db.commit()
            return doc

        except Exception as e:
            self.db.rollback()
            raise e

    def process_bulk_documents(self, file_paths: List[str], metadata_list: List[Dict[str, Any]]) -> List[Document]:
        """Process multiple documents in bulk."""
        documents = []
        for file_path, metadata in zip(file_paths, metadata_list):
            try:
                doc = self.process_pdf(file_path, metadata)
                documents.append(doc)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
        return documents

    def __del__(self):
        """Close database session when processor is destroyed."""
        self.db.close()
