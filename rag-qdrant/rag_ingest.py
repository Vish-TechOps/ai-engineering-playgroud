"""Ingest sample documents into Qdrant using OpenAI-compatible embeddings.

Prerequisites:
  - pip install qdrant-client openai
  - Set LITELLM_MASTER_URL and LITELLM_MASTER_KEY in your environment
"""

import os
import uuid

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "rag_docs"
EMBEDDING_MODEL = "text-embedding-004"
LITELLM_MASTER_URL = os.getenv("LITELLM_MASTER_URL", "http://localhost:4000")

# Sample content (replace with your own list if needed)
DOCUMENTS = [
    "Context engineering is everything in LLM",
    "Agent Skills are a set of instructions packaged as a simple folder that teaches Claude how to handle specific tasks or workflows",
    "Qdrant is a high performance vector database",
    "Neo4j is a graph database used for relationships",
    "RAG means Retrieval Augmented Generation.",
]


def get_embedding_dimension(client: OpenAI, model: str) -> int:
    """Return embedding dimension by generating a small sample embedding."""
    sample = client.embeddings.create(model=model, input="dimension probe")
    return len(sample.data[0].embedding)


def ensure_collection(qdrant: QdrantClient, vector_size: int) -> None:
    """Create collection if it doesn't exist."""
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def main() -> None:
    litellm_master_key = os.getenv("LITELLM_MASTER_KEY")
    if not litellm_master_key:
        raise RuntimeError("LITELLM_MASTER_KEY is not set. Please export it before running.")

    openai_client = OpenAI(api_key=litellm_master_key, base_url=LITELLM_MASTER_URL)
    qdrant_client = QdrantClient(url=QDRANT_URL)

    vector_size = get_embedding_dimension(openai_client, EMBEDDING_MODEL)
    ensure_collection(qdrant_client, vector_size)

    for doc in DOCUMENTS:
        embedding = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=doc,
        ).data[0].embedding

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                {
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {"text": doc},
                }
            ],
        )

    print("Documents inserted into Qdrant ✅")


if __name__ == "__main__":
    main()