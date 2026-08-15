"""Query Neo4j knowledge graph using embeddings and return top matching chunks.

The script prints ranked results and can optionally synthesize a short grounded
answer if the OPENAI_CHAT_MODEL environment variable is set.

Environment variables:
  - LITELLM_MASTER_KEY: API key for the OpenAI-compatible endpoint
  - LITELLM_MASTER_URL: Base URL for the OpenAI-compatible endpoint
  - NEO4J_URI: Neo4j Bolt URI (default: bolt://localhost:7687)
  - NEO4J_USER: Neo4j username (default: neo4j)
  - NEO4J_PASSWORD: Neo4j password
  - NEO4J_DATABASE: Neo4j database name (default: neo4j)
  - EMBEDDING_MODEL: Embedding model name (default: text-embedding-004)
  - VECTOR_INDEX_NAME: Neo4j vector index name (default: chunk_embedding_index)
  - QUERY_TEXT: Query prompt (default: What technical docs are most relevant for Graph DB knowledge?)
  - TOP_K: Number of results to return (default: 5)
  - OPENAI_CHAT_MODEL: Optional chat model to generate a grounded answer

Usage:
  python rag_query_neo4j_openai.py
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from neo4j import GraphDatabase
from openai import OpenAI


DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
DEFAULT_VECTOR_INDEX_NAME = "chunk_embedding_index"


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"{name} is not set.")
    return value


def search_with_vector(session, index_name: str, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
    result = session.run(
        """
        CALL db.index.vector.queryNodes($index_name, $top_k, $query_vector)
        YIELD node, score
        RETURN node.id AS id,
               node.title AS title,
               node.source AS source,
               node.text AS text,
               node.chunk_index AS chunk_index,
               score
        ORDER BY score DESC
        """,
        index_name=index_name,
        top_k=top_k,
        query_vector=query_vector,
    )
    return [record.data() for record in result]


def search_with_fulltext(session, query_text: str, top_k: int) -> List[Dict[str, Any]]:
    result = session.run(
        """
        CALL db.index.fulltext.queryNodes('chunk_fulltext_index', $query_text)
        YIELD node, score
        RETURN node.id AS id,
               node.title AS title,
               node.source AS source,
               node.text AS text,
               node.chunk_index AS chunk_index,
               score
        ORDER BY score DESC
        LIMIT $top_k
        """,
        query_text=query_text,
        top_k=top_k,
    )
    return [record.data() for record in result]


def synthesize_answer(client: OpenAI, model: str, query_text: str, hits: List[Dict[str, Any]]) -> str:
    context_blocks = []
    for hit in hits:
        context_blocks.append(
            f"[Source: {hit.get('source')} | Chunk: {hit.get('chunk_index')} | Score: {hit.get('score'):.4f}]\n{hit.get('text', '')}"
        )

    prompt = (
        "You are a technical assistant grounded only in the provided context. "
        "If the answer is not present, say you do not know.\n\n"
        f"Question: {query_text}\n\n"
        "Context:\n" + "\n\n".join(context_blocks)
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Answer concisely using only the context."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def main() -> None:
    litellm_master_key = get_env("LITELLM_MASTER_KEY")
    litellm_master_url = os.getenv("LITELLM_MASTER_URL", "http://localhost:4000")
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = get_env("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
    embedding_model = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    vector_index_name = os.getenv("VECTOR_INDEX_NAME", DEFAULT_VECTOR_INDEX_NAME)
    query_text = os.getenv("QUERY_TEXT", "What technical docs are most relevant for Neo4j graph knowledge?")
    top_k = int(os.getenv("TOP_K", "5"))
    chat_model = os.getenv("OPENAI_CHAT_MODEL")

    openai_client = OpenAI(api_key=litellm_master_key, base_url=litellm_master_url)
    neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    query_vector = openai_client.embeddings.create(
        model=embedding_model,
        input=query_text,
    ).data[0].embedding

    with neo4j_driver.session(database=neo4j_database) as session:
        try:
            hits = search_with_vector(session, vector_index_name, query_vector, top_k)
        except Exception:
            hits = search_with_fulltext(session, query_text, top_k)

    neo4j_driver.close()

    print(f"Query: {query_text}\n")
    for hit in hits:
        score = hit.get("score")
        score_str = f"{score:.4f}" if isinstance(score, (int, float)) else "n/a"
        text = (hit.get("text") or "").strip().replace("\n", " ")
        preview = text[:220] + ("..." if len(text) > 220 else "")
        print(f"- score={score_str} source={hit.get('source', '')} title={hit.get('title', '')}")
        print(f"  {preview}")

    if chat_model and hits:
        answer = synthesize_answer(openai_client, chat_model, query_text, hits)
        print("\nGrounded answer:\n")
        print(answer)


if __name__ == "__main__":
    main()
