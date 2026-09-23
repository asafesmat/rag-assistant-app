from fastapi import APIRouter
from app.schemas.query import QueryRequest, QueryResponse
from app.services import retrieval, generation

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    chunks = retrieval.retrieve(req.question)
    answer = generation.generate(req.question, chunks)
    sources = [c["source"] for c in chunks]
    return QueryResponse(answer=answer, sources=sources)