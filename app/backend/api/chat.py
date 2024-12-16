"""
Chat API endpoints for ARK AI.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.backend.agents.research_librarian import ResearchLibrarian
from app.backend.vector_store.chroma_store import ChromaDocStore
from app.backend.document_store.document_store import DocumentStore

router = APIRouter()

class ChatMessage(BaseModel):
    """Chat message model."""
    content: str
    role: str
    timestamp: datetime

class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None

def get_research_librarian():
    """Dependency to get Research Librarian instance."""
    vector_store = ChromaDocStore()  # Initialize with proper config
    document_store = DocumentStore()  # Initialize with proper config
    return ResearchLibrarian(vector_store, document_store)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    librarian: ResearchLibrarian = Depends(get_research_librarian)
) -> ChatResponse:
    """
    Process a chat message and return a response.
    
    Args:
        message: The user's chat message
        librarian: Research Librarian instance
        
    Returns:
        ChatResponse containing the AI's response and any relevant citations
    """
    try:
        # Process message
        response = librarian.process_message(message.content)
        
        return ChatResponse(
            content=response["content"],
            citations=response.get("citations"),
            suggestions=response.get("suggestions")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

@router.get("/chat/history", response_model=List[ChatMessage])
async def get_chat_history(
    librarian: ResearchLibrarian = Depends(get_research_librarian)
) -> List[ChatMessage]:
    """
    Get the chat conversation history.
    
    Args:
        librarian: Research Librarian instance
        
    Returns:
        List of chat messages with metadata
    """
    try:
        history = librarian.get_conversation_history()
        return [
            ChatMessage(
                content=msg["content"],
                role=msg["role"],
                timestamp=msg["timestamp"]
            )
            for msg in history
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )
