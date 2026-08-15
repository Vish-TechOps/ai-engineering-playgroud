"""Ingest technical documents into Neo4j as a lightweight knowledge graph.

This script:
  - reads local tech docs from a directory (recursive)
  - chunks each file into manageable passages
  - stores Documents + Chunks in Neo4j
  - generates embeddings for each chunk via an OpenAI-compatible endpoint
  - creates/uses a Neo4j vector index for retrieval

Environment variables:
  - LITELLM_MASTER_KEY: API key for the OpenAI-compatible embedding endpoint
  - LITELLM_MASTER_URL: Base URL for the OpenAI-compatible endpoint
  - NEO4J_URI: Neo4j Bolt URI (default: bolt://localhost:7687)
  - NEO4J_USER: Neo4j username (default: neo4j)
  - NEO4J_PASSWORD: Neo4j password
  - NEO4J_DATABASE: Neo4j database name (default: neo4j)
  - DOCS_DIR: Directory containing docs to ingest (default: ../tech_docs)
  - EMBEDDING_MODEL: Embedding model name (default: text-embedding-004)
  - VECTOR_INDEX_NAME: Neo4j vector index name (default: chunk_embedding_index)

Usage:
  python rag_ingest_neo4j_openai.py
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

from neo4j import GraphDatabase
from openai import OpenAI


DEFAULT_DOCS_DIR = Path(__file__).resolve().parents[1] / "tech_docs"
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
DEFAULT_VECTOR_INDEX_NAME = "chunk_embedding_index"
DEFAULT_FULLTEXT_INDEX_NAME = "chunk_fulltext_index"
SUPPORTED_EXTENSIONS = {".md", ".txt", ".rst", ".adoc", ".py", ".ts", ".js", ".java", ".go", ".json", ".yml", ".yaml"}


@dataclass
class Chunk:
    text: str
    chunk_index: int


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"{name} is not set.")
    return value


def get_embedding_dimension(client: OpenAI, model: str) -> int:
    sample = client.embeddings.create(model=model, input="dimension probe")
    return len(sample.data[0].embedding)


def ensure_indexes(tx, vector_index_name: str, vector_size: int, fulltext_index_name: str) -> None:
    tx.run(
        """
        CREATE CONSTRAINT document_id IF NOT EXISTS
        FOR (d:Document)
        REQUIRE d.id IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT chunk_id IF NOT EXISTS
        FOR (c:Chunk)
        REQUIRE c.id IS UNIQUE
        """
    )
    tx.run(
        f"""
        CREATE FULLTEXT INDEX {fulltext_index_name} IF NOT EXISTS
        FOR (c:Chunk)
        ON EACH [c.text, c.title, c.source]
        """
    )

    # Neo4j vector index syntax requires the vector dimensions to be known up front.
    tx.run(
        f"""
        CREATE VECTOR INDEX {vector_index_name} IF NOT EXISTS
        FOR (c:Chunk)
        ON (c.embedding)
        OPTIONS {{
          indexConfig: {{
            `vector.dimensions`: {vector_size},
            `vector.similarity_function`: 'cosine'
          }}
        }}
        """
    )


def load_documents(docs_dir: Path) -> List[Path]:
    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs directory does not exist: {docs_dir}")
    files = [p for p in docs_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not files:
        raise RuntimeError(f"No supported documents found under {docs_dir}")
    return sorted(files)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> Iterable[str]:
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [cleaned]

    chunks: List[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        start = 0
        while start < len(paragraph):
            end = min(len(paragraph), start + max_chars)
            chunks.append(paragraph[start:end])
            if end >= len(paragraph):
                current = ""
                break
            start = max(0, end - overlap)
        else:
            current = ""

    if current:
        chunks.append(current)

    return chunks


def create_document_payload(path: Path, root: Path) -> dict:
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, str(path.resolve()))),
        "title": path.stem,
        "source": str(path.relative_to(root).as_posix()) if path.is_relative_to(root) else str(path),
        "path": str(path.resolve()),
        "extension": path.suffix.lower(),
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }


def ingest_document(tx, client: OpenAI, model: str, doc: dict, text: str) -> int:
    tx.run(
        """
        MERGE (d:Document {id: $id})
        SET d.title = $title,
            d.source = $source,
            d.path = $path,
            d.extension = $extension,
            d.updated_at = $updated_at,
            d.created_at = coalesce(d.created_at, $created_at)
        """,
        **doc,
    )

    tx.run(
        """
        MATCH (d:Document {id: $id})
        OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
        DETACH DELETE c
        """,
        id=doc["id"],
    )

    chunks = list(chunk_text(text))
    for idx, chunk in enumerate(chunks):
        embedding = client.embeddings.create(model=model, input=chunk).data[0].embedding
        chunk_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc['id']}::{idx}"))
        tx.run(
            """
            MATCH (d:Document {id: $document_id})
            MERGE (c:Chunk {id: $chunk_id})
            SET c.text = $text,
                c.chunk_index = $chunk_index,
                c.source = $source,
                c.title = $title,
                c.embedding = $embedding,
                c.updated_at = $updated_at,
                c.created_at = coalesce(c.created_at, $created_at)
            MERGE (d)-[:HAS_CHUNK]->(c)
            """,
            document_id=doc["id"],
            chunk_id=chunk_id,
            text=chunk,
            chunk_index=idx,
            source=doc["source"],
            title=doc["title"],
            embedding=embedding,
            updated_at=utc_now_iso(),
            created_at=utc_now_iso(),
        )

    return len(chunks)


def main() -> None:
    litellm_master_key = get_env("LITELLM_MASTER_KEY")
    litellm_master_url = os.getenv("LITELLM_MASTER_URL", "http://localhost:4000")
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = get_env("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
    docs_dir = Path(os.getenv("DOCS_DIR", str(DEFAULT_DOCS_DIR))).expanduser()
    embedding_model = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    vector_index_name = os.getenv("VECTOR_INDEX_NAME", DEFAULT_VECTOR_INDEX_NAME)
    fulltext_index_name = os.getenv("FULLTEXT_INDEX_NAME", DEFAULT_FULLTEXT_INDEX_NAME)

    openai_client = OpenAI(api_key=litellm_master_key, base_url=litellm_master_url)
    neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    files = load_documents(docs_dir)
    vector_size = get_embedding_dimension(openai_client, embedding_model)

    with neo4j_driver.session(database=neo4j_database) as session:
        session.execute_write(ensure_indexes, vector_index_name, vector_size, fulltext_index_name)

        total_docs = 0
        total_chunks = 0
        for path in files:
            text = read_text(path)
            if not text:
                continue
            doc = create_document_payload(path, docs_dir)
            chunk_count = session.execute_write(ingest_document, openai_client, embedding_model, doc, text)
            total_docs += 1
            total_chunks += chunk_count
            print(f"Ingested {path} -> {chunk_count} chunks")

    neo4j_driver.close()
    print(f"Done. Documents: {total_docs}, chunks: {total_chunks}, database: {neo4j_database}")


if __name__ == "__main__":
    main()
