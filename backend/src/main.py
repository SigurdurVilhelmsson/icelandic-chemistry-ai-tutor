"""
Chemistry AI Tutor - FastAPI Backend
Main application entry point with CORS configuration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Chemistry AI Tutor API",
    description="AI-powered chemistry tutor for Icelandic students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
    question: str
    language: Optional[str] = "is"  # Icelandic by default
    context: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    sources: Optional[list] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "chemistry-ai-tutor",
        "version": "1.0.0"
    }

# Main question endpoint
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Process a chemistry question and return an AI-generated answer

    Args:
        request: QuestionRequest containing the question and optional context

    Returns:
        QuestionResponse with the answer and metadata
    """
    try:
        logger.info(f"Received question: {request.question[:100]}...")

        # TODO: Implement actual AI processing
        # This is a placeholder response
        answer = f"This is a placeholder response for: {request.question}"

        return QuestionResponse(
            answer=answer,
            confidence=0.85,
            sources=["Chemistry Textbook Chapter 3"]
        )

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
