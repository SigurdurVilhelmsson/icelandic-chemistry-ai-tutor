"""
Chemistry AI Tutor - FastAPI Backend
Main application entry point with CORS configuration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import RAG Pipeline
try:
    from .rag_pipeline import RAGPipeline
except ImportError:
    # If running as script, use absolute import
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rag_pipeline import RAGPipeline

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Chemistry AI Tutor API",
    description="AI-powered chemistry tutor for Icelandic students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Request/Response Models
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    language: Optional[str] = "is"  # Icelandic by default
    context: Optional[str] = Field(None, max_length=5000)

    @validator('question')
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace only')
        return v.strip()

class Citation(BaseModel):
    chapter: str
    section: str
    title: str
    text_preview: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    timestamp: str
    session_id: Optional[str] = None

# Global RAG pipeline instance
rag_pipeline: Optional[RAGPipeline] = None

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline on startup"""
    global rag_pipeline
    try:
        logger.info("Initializing RAG pipeline...")
        chroma_db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        rag_pipeline = RAGPipeline(chroma_db_path=chroma_db_path)
        logger.info("✓ RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize RAG pipeline: {e}")
        logger.warning("Server will start but /ask endpoint may not function correctly")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    health_status = {
        "status": "healthy",
        "service": "chemistry-ai-tutor",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

    # Check if RAG pipeline is initialized
    if rag_pipeline is None:
        health_status["status"] = "degraded"
        health_status["warnings"] = ["RAG pipeline not initialized"]
    else:
        try:
            # Get pipeline stats
            stats = rag_pipeline.get_pipeline_stats()
            health_status["database"] = {
                "total_chunks": stats["database"]["total_chunks"],
                "status": "ok" if stats["database"]["total_chunks"] > 0 else "empty"
            }
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["warnings"] = [f"Database check failed: {str(e)}"]

    return health_status

# Main question endpoint
@app.post("/ask", response_model=QuestionResponse)
@limiter.limit("30/minute")
async def ask_question(request: QuestionRequest, req: Request):
    """
    Process a chemistry question and return an AI-generated answer

    Args:
        request: QuestionRequest containing the question and optional context

    Returns:
        QuestionResponse with the answer and metadata
    """
    # Check if RAG pipeline is initialized
    if rag_pipeline is None:
        logger.error("RAG pipeline not initialized")
        raise HTTPException(
            status_code=503,
            detail="Service not ready. RAG pipeline not initialized."
        )

    try:
        logger.info(f"Received question: {request.question[:100]}...")

        # Use RAG pipeline to generate answer
        result = rag_pipeline.ask(question=request.question)

        # Format citations for response
        citations = []
        for citation in result.get("citations", []):
            citations.append(Citation(
                chapter=citation.get("chapter", "N/A"),
                section=citation.get("section", "N/A"),
                title=citation.get("title", "N/A"),
                text_preview=citation.get("text_preview", None)
            ))

        # Build response
        response = QuestionResponse(
            answer=result["answer"],
            citations=citations,
            timestamp=result["metadata"]["timestamp"],
            session_id=request.session_id
        )

        logger.info(f"Answer generated successfully with {len(citations)} citations")
        return response

    except ValueError as e:
        # Client error (e.g., empty question)
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Villa kom upp við úrvinnslu spurningar. Vinsamlegast reyndu aftur."
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Chemistry AI Tutor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
