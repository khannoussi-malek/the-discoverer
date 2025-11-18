"""Embedding generator using sentence transformers."""
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
import asyncio

from config.settings import get_settings


class EmbeddingGenerator:
    """Embedding generator - KISS: Simple interface."""
    
    def __init__(self):
        self.settings = get_settings()
        self.model: Optional[SentenceTransformer] = None
        self._model_loaded = False
    
    def _load_model(self) -> None:
        """Lazy load model."""
        if not self._model_loaded:
            self.model = SentenceTransformer(self.settings.embedding_model)
            self._model_loaded = True
    
    async def generate(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        if not self.model:
            self._load_model()
        
        # Run in thread pool (model.encode is CPU-bound)
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(text, normalize_embeddings=True)
        )
        
        return embedding.tolist()
    
    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts - DRY: Reusable."""
        if not self.model:
            self._load_model()
        
        # Run in thread pool with batch processing
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(
                texts,
                batch_size=self.settings.batch_embedding_size,
                show_progress_bar=False,
                normalize_embeddings=True
            )
        )
        
        return embeddings.tolist()

