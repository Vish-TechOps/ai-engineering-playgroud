"""Query Qdrant using OpenAI-compatible embeddings (no LLM generation).

Prerequisites:
  - pip install qdrant-client openai
  - Set LITELLM_MASTER_URL and LITELLM_MASTER_KEY in your environment
"""

import os

from openai import OpenAI
from qdrant_client import QdrantClient

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "rag_docs"
EMBEDDING_MODEL = "text-embedding-004"
LITELLM_MASTER_URL = os.getenv("LITELLM_MASTER_URL", "http://localhost:4000")


def main() -> None:
    litellm_master_key = os.getenv("LITELLM_MASTER_KEY")
    if not litellm_master_key:
        raise RuntimeError("LITELLM_MASTER_KEY is not set. Please export it before running.")

    query_text = "What is Qdrant?"

    openai_client = OpenAI(api_key=litellm_master_key, base_url=LITELLM_MASTER_URL)
    qdrant_client = QdrantClient(url=QDRANT_URL)

    query_vector = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query_text,
    ).data[0].embedding

    hits = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3,
    )

    print(f"Query: {query_text}\n")
    for hit in hits.points:
        score = f"{hit.score:.4f}" if hit.score is not None else "n/a"
        print(f"- score={score} text={hit.payload.get('text', '')}")


if __name__ == "__main__":
    main()