# Minimal MCP server

## qdrant-mcp-server

✅ A tiny qdrant-mcp-server (Python, no Docker/WSL)
✅ A tiny MCP client (Python)
✅ Your existing rag_query logic, but routed through MCP instead of directly calling Qdrant

## Flows

Current flow
rag_query.py → Qdrant

New flow
rag_query_mcp.py → MCP Client → MCP Server (qdrant_mcp_server.py) → Qdrant

## Steps

✅ Step 1 — Install Dependencies
You already have Qdrant + Ollama.
Install Python libs:
pip install mcp

✅ Step 2 — Create Project Structure
Inside folder:
qdrant_mcp_server.py
rag_query_mcp.py

✅ Step 3 — Minimal Qdrant MCP Server
Create:
qdrant_mcp_server.py
This server exposes ONE tool:
search_qdrant(query, collection)
That’s your MCP server.

✅ Step 4 — MCP Client Version of rag_query

Create:

rag_query_mcp.py

This script:

✔ Launches MCP server as subprocess
✔ Calls tool via MCP
✔ Prints results


✅ Step 5 — Run It

From folder:

$ python rag_query_mcp.py

✅ MCP Response:
- {
  "text": "RAG means Retrieval Augmented Generation."
}
- {
  "text": "Neo4j is a graph database used for relationships."
}
- {
  "text": "Qdrant is a high performance vector database."
}

Flow:

✔ Client starts server
✔ Server connects to Qdrant
✔ Server calls Ollama for embedding
✔ Server queries Qdrant
✔ Server returns payload
✔ Client prints text

## Learnings

This tiny example demonstrates real MCP mechanics:

MCP Server
Declares tools
Owns data access (Qdrant)
Owns logic (embedding + search)

MCP Client
Knows NOTHING about Qdrant
Only calls tools by name
This is why MCP is powerful:

👉 Tools become portable
👉 LLM / Agent / IDE can reuse same server
👉 Backend logic isolated

---
$ python rag_query_mcp.py

✅ MCP Response:
- {
  "text": "RAG means Retrieval Augmented Generation."
}
- {
  "text": "Neo4j is a graph database used for relationships."
}
- {
  "text": "Qdrant is a high performance vector database."
}