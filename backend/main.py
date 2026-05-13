from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from routers import health, query, attacks, metrics
from ml.bert_classifier import BERTClassifier
from ml.cosine_drift_monitor import CosineDriftMonitor
from ml.retrieval_engine import RetrievalEngine
from ml.integrity_scorer import IntegrityScorer
from ml.pipeline import RAGPipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    classifier = BERTClassifier()
    drift_monitor = CosineDriftMonitor()
    retrieval_engine = RetrievalEngine()
    integrity_scorer = IntegrityScorer()
    pipeline = RAGPipeline(classifier, drift_monitor, retrieval_engine, integrity_scorer)

    app.state.classifier = classifier
    app.state.drift_monitor = drift_monitor
    app.state.retrieval_engine = retrieval_engine
    app.state.integrity_scorer = integrity_scorer
    app.state.pipeline = pipeline

    print("✅ Adversarial AI backend started")
    yield
    print("🛑 Shutting down")

app = FastAPI(
    title="Adversarial AI RAG Security API",
    description="Detects prompt injection, adversarial attacks, and monitors RAG pipeline integrity",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173"
)
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(attacks.router, prefix="/api", tags=["Attacks"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("ENV", "production") == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)