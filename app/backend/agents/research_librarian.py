"""
AI Research Librarian agent for ARK AI.
Handles natural language interactions and knowledge base queries.
"""

from typing import List, Dict, Any, Tuple, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langgraph.graph import Graph, MessageGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain.tools import Tool
from langchain.agents import AgentExecutor
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import os
from app.utils.cli_logger import CliLogger

logger = logging.getLogger('ark_ai.agents')

class ResearchLibrarianState(BaseModel):
    """State for the Research Librarian agent."""
    messages: List[BaseMessage] = Field(default_factory=list)
    current_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    research_focus: Optional[str] = Field(default=None)
    next_steps: List[str] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    last_search_results: Optional[List[Dict[str, Any]]] = Field(default=None)

class ResearchLibrarian:
    """AI Research Librarian agent that handles natural conversations and knowledge base queries."""

    def __init__(self, vector_store, document_store):
        """Initialize the Research Librarian agent."""
        self.vector_store = vector_store
        self.document_store = document_store
        
        # Get configuration from environment variables
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            CliLogger.error("GROQ API key not found!", details={"env_var": "GROQ_API_KEY"})
            raise ValueError("GROQ_API_KEY environment variable is required")
            
        model_name = os.getenv('MODEL_NAME', 'llama3-groq-70b-8192-tool-use-preview')
        model_temperature = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
        model_max_tokens = int(os.getenv('MODEL_MAX_TOKENS', '8192'))
            
        CliLogger.info("Initializing AI model...", context='model_loaded', 
                      details={
                          "model": model_name,
                          "temperature": model_temperature,
                          "max_tokens": model_max_tokens
                      })
            
        self.llm = ChatGroq(
            temperature=model_temperature,
            model_name=model_name,
            groq_api_key=groq_api_key,
            max_tokens=model_max_tokens,
            streaming=True
        )
        
        CliLogger.success("AI model initialized successfully!", context='model_loaded')
        
        self.tools = self._create_tools()
        self.state = ResearchLibrarianState()
        
        # Initialize conversation with system message
        self.state.messages.append(
            SystemMessage(content=self._get_system_prompt())
        )
        
        CliLogger.info("Research Librarian agent ready!", context='ready')

    async def process_message(self, message: str) -> str:
        """Process a user message and return the AI response."""
        CliLogger.info("Processing user message...", context='user_input',
                      details={"message_length": len(message)})
        
        try:
            # Add user message to state
            self.state.messages.append(HumanMessage(content=message))
            
            CliLogger.ai_event('thinking', "Generating response...")
            
            # Generate response using the LLM
            response = await self.llm.ainvoke(
                self.state.messages
            )
            
            # Add AI response to state
            self.state.messages.append(response)
            
            CliLogger.ai_event('response', "Response generated successfully",
                             details={"response_length": len(response.content)})
            
            return response.content
            
        except Exception as e:
            CliLogger.error(f"Error processing message: {str(e)}")
            raise

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Research Librarian."""
        return """You are an AI Research Librarian, a knowledgeable and helpful assistant dedicated to guiding users through their academic research.
        
        Your core responsibilities:
        1. Navigate and explain the knowledge repository with expertise
        2. Provide detailed answers with specific citations to source documents
        3. Suggest relevant research directions and connections
        4. Maintain conversation context and research continuity
        5. Offer proactive suggestions for deeper investigation
        
        Guidelines:
        - Always ground your responses in the available documents
        - Provide specific citations when referencing information
        - Maintain a professional yet approachable tone
        - If information is not in the knowledge base, acknowledge this clearly
        - Proactively suggest related topics and research directions
        
        Remember: You are helping researchers explore and understand complex topics. Be thorough, accurate, and helpful."""

    def _create_tools(self) -> List[BaseTool]:
        """Create the tools available to the Research Librarian."""
        return [
            Tool(
                name="search_knowledge_base",
                func=self._search_knowledge_base,
                description="Search the knowledge base using semantic search"
            ),
            Tool(
                name="get_document_content",
                func=self._get_document_content,
                description="Retrieve the full content of a specific document"
            ),
            Tool(
                name="find_related_documents",
                func=self._find_related_documents,
                description="Find documents related to a given document"
            ),
            Tool(
                name="get_document_metadata",
                func=self._get_document_metadata,
                description="Get metadata about a specific document"
            ),
            Tool(
                name="create_research_summary",
                func=self._create_research_summary,
                description="Create a summary of the current research findings"
            )
        ]

    def _search_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base using semantic search."""
        try:
            results = self.vector_store.similarity_search(query, n_results=limit)
            self.state.last_search_results = results
            return results
        except Exception as e:
            CliLogger.error(f"Error searching knowledge base: {str(e)}")
            return []

    def _get_document_content(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the full content of a specific document."""
        try:
            return self.document_store.get_document(doc_id)
        except Exception as e:
            CliLogger.error(f"Error retrieving document {doc_id}: {str(e)}")
            return None

    def _find_related_documents(self, doc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find documents related to a given document."""
        try:
            doc = self.document_store.get_document(doc_id)
            if doc and doc.get('content'):
                return self.vector_store.similarity_search(doc['content'], n_results=limit)
            return []
        except Exception as e:
            CliLogger.error(f"Error finding related documents for {doc_id}: {str(e)}")
            return []

    def _get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a specific document."""
        try:
            doc = self.document_store.get_document(doc_id)
            return doc.get('metadata') if doc else None
        except Exception as e:
            CliLogger.error(f"Error retrieving metadata for {doc_id}: {str(e)}")
            return None

    def _create_research_summary(self, topic: str) -> Dict[str, Any]:
        """Create a summary of the current research findings."""
        try:
            # Get relevant documents
            docs = self._search_knowledge_base(topic)
            
            # Extract key points and create summary
            summary = {
                'topic': topic,
                'key_findings': [],
                'sources': [],
                'suggested_directions': []
            }
            
            # Add documents as sources
            for doc in docs:
                if doc.get('metadata'):
                    summary['sources'].append({
                        'id': doc['id'],
                        'title': doc['metadata'].get('title', 'Untitled'),
                        'relevance': doc['metadata'].get('score', 0)
                    })
            
            return summary
        except Exception as e:
            CliLogger.error(f"Error creating research summary: {str(e)}")
            return {
                'topic': topic,
                'error': str(e)
            }

    def _generate_response(self, message: str) -> Dict[str, Any]:
        """Generate a response using the LLM and tools."""
        try:
            # First, try to understand the user's intent
            context = self._search_knowledge_base(message)
            
            # Prepare prompt with context
            prompt = self._get_system_prompt() + "\n\nCurrent context:\n"
            for doc in context:
                prompt += f"- {doc.get('content', '')}\n"
            
            prompt += f"\nUser message: {message}\n\nResponse:"
            
            # Generate response using invoke instead of predict
            response = self.llm.invoke(prompt).content
            
            # Extract citations from context
            citations = []
            for doc in context:
                if doc.get('metadata'):
                    citations.append({
                        'title': doc['metadata'].get('title', 'Untitled'),
                        'page': doc['metadata'].get('page', 1),
                        'relevance_score': doc['metadata'].get('score', 0)
                    })
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(message, context)
            
            return {
                'content': response,
                'citations': citations,
                'suggestions': suggestions
            }
            
        except Exception as e:
            CliLogger.error(f"Error generating response: {str(e)}")
            return {
                'content': "I apologize, but I encountered an error generating a response. Please try again.",
                'error': str(e)
            }

    def _generate_suggestions(self, message: str, context: List[Dict[str, Any]]) -> List[str]:
        """Generate research suggestions based on the current context."""
        try:
            suggestions = []
            
            # Add suggestions based on related documents
            if context:
                for doc in context[:2]:  # Use top 2 most relevant docs
                    related = self._find_related_documents(doc['id'], limit=2)
                    for rel_doc in related:
                        if rel_doc.get('metadata', {}).get('title'):
                            suggestions.append(
                                f"Explore: {rel_doc['metadata']['title']}"
                            )
            
            # Add general research directions
            suggestions.extend([
                "Consider broader implications of this topic",
                "Look for practical applications",
                "Examine historical context"
            ])
            
            return list(set(suggestions))[:5]  # Return up to 5 unique suggestions
            
        except Exception as e:
            CliLogger.error(f"Error generating suggestions: {str(e)}")
            return []
