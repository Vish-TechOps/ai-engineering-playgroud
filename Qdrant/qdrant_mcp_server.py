from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
import ollama

mcp = FastMCP("qdrant-mcp-server")

client = QdrantClient(url="http://localhost:6333")


@mcp.tool()
def search_qdrant(query: str, collection: str = "local_docs", limit: int = 3):
    """
    Search Qdrant collection using embeddings
    """
    query_vector = ollama.embeddings(
        model="nomic-embed-text",
        prompt=query
    )["embedding"]

    hits = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=limit
    )

    return [hit.payload for hit in hits.points]


if __name__ == "__main__":
    mcp.run()