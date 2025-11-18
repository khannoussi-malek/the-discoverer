"""Embedding generator using sentence transformers."""
from typing import List, Optional, TYPE_CHECKING
import numpy as np
import asyncio

from config.settings import get_settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
else:
    SentenceTransformer = None


class EmbeddingGenerator:
    """Embedding generator - KISS: Simple interface."""
    
    def __init__(self):
        self.settings = get_settings()
        self.model: Optional['SentenceTransformer'] = None
        self._model_loaded = False
        self._sentence_transformers_available = False
    
    def _check_dependencies(self) -> bool:
        """Check if sentence-transformers is available."""
        if not self._sentence_transformers_available:
            try:
                from sentence_transformers import SentenceTransformer
                self._SentenceTransformer = SentenceTransformer
                self._sentence_transformers_available = True
            except ImportError:
                return False
        return self._sentence_transformers_available
    
    def _load_model(self) -> None:
        """Lazy load model."""
        if not self._check_dependencies():
            raise ImportError("sentence-transformers is not installed. Install it with: pip install sentence-transformers")
        if not self._model_loaded:
            self.model = self._SentenceTransformer(self.settings.embedding_model)
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

