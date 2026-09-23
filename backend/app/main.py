from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services import retrieval
from app.api.routes.query import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    retrieval.load()      # يتحمّل مرة واحدة بس عند تشغيل السيرفر
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                    allow_methods=["*"], allow_headers=["*"])
app.include_router(router)