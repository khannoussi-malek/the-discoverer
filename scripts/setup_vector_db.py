"""Script to set up vector database collections."""
import asyncio
from src.infrastructure.vector_db.client import QdrantVectorDBClient


async def main():
    """Initialize vector DB collections."""
    client = QdrantVectorDBClient()
    await client.initialize_collections()
    print("Vector DB collections initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())

