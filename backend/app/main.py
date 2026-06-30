# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# Import routers once implemented
from app.api import ask

app = FastAPI(
    title="Insurance RAG Agentic AI",
    description="API for the Insurance RAG Agentic AI system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health API
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Service is healthy"}

# Router Registration
app.include_router(ask.router, prefix="/api/ask", tags=["Q&A"])
