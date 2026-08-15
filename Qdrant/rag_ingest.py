from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import ollama
import uuid

# Connect Qdrant
client = QdrantClient(url="http://localhost:6333")

COLLECTION = "local_docs"

# Create collection if not exists
if COLLECTION not in [c.name for c in client.get_collections().collections]:
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

# Example documents
documents = [
    "Qdrant is a high performance vector database.",
    "Neo4j is a graph database used for relationships.",
    "RAG means Retrieval Augmented Generation."
]

# Generate embeddings + insert
for doc in documents:
    embedding = ollama.embeddings(
        model="nomic-embed-text",
        prompt=doc
    )["embedding"]

    client.upsert(
        collection_name=COLLECTION,
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {"text": doc}
            }
        ]
    )

print("Documents inserted into Qdrant 🚀")