import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import glob
import tiktoken
import httpx
import asyncio

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# --- CONFIG ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
COMPLETION_MODEL = os.getenv("COMPLETION_MODEL", "gpt-3.5-turbo")
DOCS_PATH = os.getenv("DOCS_PATH", "docs/*.md")
CHUNK_SIZE = 500  # characters
TOP_K = 4

# --- DOC INGESTION & EMBEDDING ---
doc_chunks = []  # List[dict]: {"text": str, "embedding": List[float], "source": str}

async def get_embedding(text: str) -> List[float]:
    headers = {}
    url = ""
    data = {}
    if LLM_PROVIDER == "openrouter":
        url = "https://openrouter.ai/api/v1/embeddings"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        data = {"model": EMBEDDING_MODEL, "input": text}
    elif LLM_PROVIDER == "xai":
        url = "https://api.x.ai/v1/embeddings"
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        data = {"model": EMBEDDING_MODEL, "input": text}
    else:  # openai
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {"model": EMBEDDING_MODEL, "input": text}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    # Simple character-based chunking, can be improved
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

async def ingest_docs():
    global doc_chunks
    doc_chunks = []
    files = glob.glob(DOCS_PATH)
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        chunks = chunk_text(content)
        for chunk in chunks:
            embedding = await get_embedding(chunk)
            doc_chunks.append({"text": chunk, "embedding": embedding, "source": os.path.basename(file)})

# --- EMBEDDING SIMILARITY ---
def cosine_similarity(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_top_k_chunks(query_embedding, k=TOP_K):
    scored = [
        (cosine_similarity(query_embedding, chunk["embedding"]), chunk)
        for chunk in doc_chunks
    ]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [chunk for score, chunk in scored[:k]]

# --- LLM COMPLETION ---
async def llm_complete(prompt: str, context: List[str]) -> str:
    headers = {}
    url = ""
    data = {}
    system_prompt = (
        "You are a helpful support assistant for the Waves Quant Engine platform. "
        "Answer the user's question using the provided documentation context. "
        "If the answer is not in the context, say you don't know but offer to connect to human support."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{chr(10).join(context)}\n\nQuestion: {prompt}"}
    ]
    if LLM_PROVIDER == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        data = {"model": COMPLETION_MODEL, "messages": messages}
    elif LLM_PROVIDER == "xai":
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        data = {"model": COMPLETION_MODEL, "messages": messages}
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {"model": COMPLETION_MODEL, "messages": messages}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

# --- FASTAPI STARTUP ---
@router.on_event("startup")
async def startup_event():
    await ingest_docs()

@router.post("/api/support/chat")
async def support_chat(req: ChatRequest):
    if not doc_chunks:
        await ingest_docs()
    query_embedding = await get_embedding(req.message)
    top_chunks = get_top_k_chunks(query_embedding)
    context = [chunk["text"] for chunk in top_chunks]
    answer = await llm_complete(req.message, context)
    return {"response": answer} 