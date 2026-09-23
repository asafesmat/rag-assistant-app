from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    vector_store_path: str = "data/vector_store"
    collection_name: str = "laws"
    embedding_model: str = "BAAI/bge-m3"
    ollama_model: str = "qwen2.5:7b"
    top_k: int = 4

    class Config:
        env_file = ".env"

settings = Settings()