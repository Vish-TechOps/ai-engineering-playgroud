from qdrant_client import QdrantClient
import ollama

client = QdrantClient(url="http://localhost:6333")

query = "What is Qdrant?"

query_vector = ollama.embeddings(
    model="nomic-embed-text",
    prompt=query
)["embedding"]

hits = client.query_points(
    collection_name="tech_local_docs",
    query=query_vector,
    limit=3
)

for hit in hits.points:
    print(hit.payload["text"])