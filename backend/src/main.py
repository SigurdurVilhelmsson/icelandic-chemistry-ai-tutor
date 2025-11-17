"""
FastAPI Application for Icelandic Chemistry AI Tutor
Provides REST API endpoints for the RAG-based tutoring system.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .rag_pipeline import RAGPipeline

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Icelandic Chemistry AI Tutor",
    description="RAG-based chemistry tutoring system for Icelandic high school students",
    version="1.0.0"
)

# Configure CORS (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline (singleton)
rag_pipeline: Optional[RAGPipeline] = None


# Pydantic models for request/response
class AskRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., min_length=1, description="Question in Icelandic")
    session_id: str = Field(..., min_length=1, description="User session ID")
    chapter_filter: Optional[str] = Field(None, description="Filter by chapter (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Hvað er atóm?",
                "session_id": "user_123",
                "chapter_filter": None
            }
        }


class Citation(BaseModel):
    """Citation information."""
    chapter: str
    section: str
    title: str
    text_preview: str


class AskResponse(BaseModel):
    """Response model for questions."""
    answer: str
    citations: list[Citation]
    timestamp: str
    metadata: dict

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Atóm er minnsta eining efnis...",
                "citations": [
                    {
                        "chapter": "1",
                        "section": "1",
                        "title": "Atómbygging",
                        "text_preview": "Atóm er minnsta eining efnis sem..."
                    }
                ],
                "timestamp": "2025-11-17T10:30:00",
                "metadata": {
                    "chunks_found": 5,
                    "response_time_ms": 1250.5
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    db_chunks: int
    timestamp: str
    version: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup."""
    global rag_pipeline

    logger.info("Starting Icelandic Chemistry AI Tutor API")

    try:
        # Get database path from environment
        chroma_db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

        # Initialize pipeline
        rag_pipeline = RAGPipeline(
            chroma_db_path=chroma_db_path,
            top_k=5,
            max_context_chunks=4
        )

        logger.info("RAG pipeline initialized successfully")

        # Perform health check
        health = rag_pipeline.health_check()
        logger.info(f"Health check: {health['status']}")

        if health['status'] != 'healthy':
            logger.warning(f"Pipeline is not fully healthy: {health}")

    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Icelandic Chemistry AI Tutor API")


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.now()

    # Log request
    logger.info(f"{request.method} {request.url.path} - Start")

    # Process request
    try:
        response = await call_next(request)

        # Log response
        duration = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.2f}ms"
        )

        return response

    except Exception as e:
        logger.error(f"{request.method} {request.url.path} - Error: {e}")
        raise


# API Endpoints

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Icelandic Chemistry AI Tutor",
        "version": "1.0.0",
        "description": "RAG-based chemistry tutoring system",
        "endpoints": {
            "ask": "POST /ask - Ask a chemistry question",
            "health": "GET /health - Health check",
            "stats": "GET /stats - Pipeline statistics"
        }
    }


@app.post("/ask", response_model=AskResponse, tags=["Tutoring"])
async def ask_question(request: AskRequest):
    """
    Ask a chemistry question and get an AI-generated answer with citations.

    Args:
        request: AskRequest with question and session_id

    Returns:
        AskResponse with answer, citations, and metadata
    """
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )

    try:
        # Log request
        logger.info(
            f"Question from session {request.session_id}: "
            f"'{request.question}'"
        )

        # Prepare metadata filter if chapter specified
        metadata_filter = None
        if request.chapter_filter:
            metadata_filter = {"chapter": request.chapter_filter}

        # Process question
        result = rag_pipeline.ask(
            question=request.question,
            metadata_filter=metadata_filter
        )

        # Format response
        response = AskResponse(
            answer=result["answer"],
            citations=[Citation(**c) for c in result["citations"]],
            timestamp=result["metadata"]["timestamp"],
            metadata=result["metadata"]
        )

        logger.info(
            f"Answer generated for session {request.session_id} in "
            f"{result['metadata']['response_time_ms']:.2f}ms"
        )

        return response

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse with system status and database info
    """
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )

    try:
        # Get pipeline stats
        stats = rag_pipeline.get_pipeline_stats()
        db_chunks = stats["database"]["total_chunks"]

        # Perform health check
        health = rag_pipeline.health_check()

        return HealthResponse(
            status=health["status"],
            db_chunks=db_chunks,
            timestamp=datetime.now().isoformat(),
            version="1.0.0"
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/stats", tags=["System"])
async def get_stats():
    """
    Get detailed pipeline statistics.

    Returns:
        Dictionary with configuration and database statistics
    """
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )

    try:
        stats = rag_pipeline.get_pipeline_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


@app.get("/validate", tags=["System"])
async def validate_setup():
    """
    Validate pipeline setup and component functionality.

    Returns:
        Dictionary with validation results
    """
    if not rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not initialized"
        )

    try:
        validation = rag_pipeline.validate_setup()
        return validation

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# Run with: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
