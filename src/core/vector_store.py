import os
from typing import Any, Dict, List, Optional

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


class VectorStore:
    def __init__(self):
        load_dotenv()
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL not found.")

    def _get_connection(self):
        """connection with pgvector registered"""
        conn = psycopg.connect(self.database_url)
        register_vector(conn)
        return conn

    def initialize_database(self):
        """create table and enable pgvector extension"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # enable pgvector extension
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

                # create table
                cur.execute(""" 
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id TEXT PRIMARY KEY,
                        text_content TEXT NOT NULL,
                        embedding VECTOR(3072) NOT NULL,
                        source TEXT,
                        file_type TEXT,
                        page INTEGER,
                        section TEXT,
                        chunk_index INTEGER,
                        parent_document_id TEXT
                    );
                """)

                # # Create HNSW index for faster similarity search
                # cur.execute("""
                #     CREATE INDEX IF NOT EXISTS idx_embedding_hnsw
                #     ON document_chunks USING hnsw (embedding vector_cosine_ops);
                # """)

                conn.commit()

    def add_documents(self, embedded_docs: List[Dict]):
        """Insert documents with embeddings into the database"""
        self.initialize_database()

        query = """
        INSERT INTO document_chunks (
            id,
            text_content,
            embedding,
            source,
            file_type,
            page,
            section,
            chunk_index,
            parent_document_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                inserted_count = 0
                for doc in embedded_docs:
                    metadata = doc["metadata"]

                    cur.execute(
                        query,
                        (
                            doc["id"],
                            doc["text"],
                            doc["embedding"],
                            metadata.get("source"),
                            metadata.get("file_type"),
                            metadata.get("page"),
                            metadata.get("section"),
                            metadata.get("chunk_index"),
                            metadata.get("parent_document_id"),
                        ),
                    )
                    inserted_count += 1

            conn.commit()

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[tuple]:

        query = """
        SELECT
            id,
            text_content,
            embedding <=> %s::VECTOR AS distance,
            source,
            file_type,
            page,
            section,
            chunk_index,
            parent_document_id
        FROM document_chunks
        """

        where_clauses = []
        query_params = [query_embedding]  # for the distance calculation

        # dynamically append filters to WHERE clause
        if filters:
            allowed_fields = [
                "source",
                "file_type",
                "page",
                "section",
                "chunk_index",
                "parent_document_id",
            ]

            for key, value in filters.items():
                if key in allowed_fields:
                    where_clauses.append(f"{key} = %s")
                    query_params.append(value)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY embedding <=> %s::VECTOR LIMIT %s;"
        query_params.append(query_embedding)  # For ORDER BY
        query_params.append(k)  # For LIMIT

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(query_params))
                rows = cur.fetchall()

        return rows

    def get_total_count(self) -> int:
        """Helper method to verify data was inserted"""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks")
                return cur.fetchone()[0]
