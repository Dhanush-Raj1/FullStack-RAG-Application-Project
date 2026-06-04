import logging
import os
import time
from dataclasses import asdict
from typing import Dict, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.models.document import Document

logger = logging.getLogger(__name__)


class GeminiEmbeddingGenerator:
    def __init__(self, model_name: str):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        # Gemini API hard limit for a single batch operation
        self._MAX_BATCH_SIZE = 100

    def embed_text(self, chunks: List[Document]) -> List[float]:
        """
        Accepts a list of chunked documents, groups them into batches.
        Generate embeddings and returns a list of dictionaries pairing the generated vector with source text properties.
        """

        if not chunks:
            return [], []

        # Filter out empty or whitespace-only chunks — Gemini SDK rejects them causing CORS error
        valid_chunks = [c for c in chunks if c.page_content and c.page_content.strip()]

        if not valid_chunks:
            raise ValueError("All chunks are empty after filtering — nothing to embed.")

        texts_to_embed = [chunk.page_content.strip() for chunk in valid_chunks]   # ensure no leading/trailing whitespace in texts sent to Gemini
        # texts_to_embed = [chunk.page_content for chunk in chunks]
        all_embeddings = []

        SAFE_BATCH_SIZE = 15

        logger.info(
            f"Splitting {len(valid_chunks)} chunks into safe sub-batches of {SAFE_BATCH_SIZE}..."
        )

        for i in range(0, len(texts_to_embed), SAFE_BATCH_SIZE):
            batch = texts_to_embed[i : i + SAFE_BATCH_SIZE]

            current_batch_num = (i // SAFE_BATCH_SIZE) + 1
            total_batches = (
                len(texts_to_embed) + SAFE_BATCH_SIZE - 1
            ) // SAFE_BATCH_SIZE

            logger.info(
                f"🚀 Sending batch {current_batch_num}/{total_batches} (Size: {len(batch)})..."
            )
            print(
                f"🚀 Sending batch {current_batch_num}/{total_batches} (Size: {len(batch)})..."
            )

            response = self.client.models.embed_content(
                model=self.model_name,
                contents=batch,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )

            for emb in response.embeddings:
                all_embeddings.append(emb.values)

            if i + SAFE_BATCH_SIZE < len(texts_to_embed):
                time.sleep(10)

        embedded_docs = []

        for idx, chunk in enumerate(valid_chunks):
            vector = all_embeddings[idx]
            embedded_docs.append(
                {
                    "id": chunk.metadata.chunk_id,
                    "text": chunk.page_content,
                    "embedding": vector,
                    "metadata": asdict(chunk.metadata),
                }
            )

        return embedded_docs, valid_chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds incoming user's query.
        """
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )

        if hasattr(response, "embedding") and response.embedding:
            return response.embedding.values

        return response.embeddings[0].values

    # Main function for embedding list of chunked documents with batch request
    def embed_documents(self, chunks) -> List[Dict]:
        if not chunks:
            return []

        texts_to_embed = [chunk.page_content for chunk in chunks]
        all_embeddings = []

        # DROP BATCH SIZE: Free tier allows a max of 100 items per minute bucket.
        # Running 15 chunks per batch keeps us completely safe.
        SAFE_BATCH_SIZE = 15

        logger.info(
            f"Splitting {len(chunks)} chunks into safe sub-batches of {SAFE_BATCH_SIZE}..."
        )

        for i in range(0, len(texts_to_embed), SAFE_BATCH_SIZE):
            batch = texts_to_embed[i : i + SAFE_BATCH_SIZE]

            current_batch_num = (i // SAFE_BATCH_SIZE) + 1
            total_batches = (
                len(texts_to_embed) + SAFE_BATCH_SIZE - 1
            ) // SAFE_BATCH_SIZE

            logger.info(
                f"🚀 Sending batch {current_batch_num}/{total_batches} (Size: {len(batch)})..."
            )

            response = self.client.models.embed_content(
                model=self.model_name,
                contents=batch,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )

            # Extract individual vector records from this specific batch's response
            for emb in response.embeddings:
                all_embeddings.append(emb.values)

            # If there are more batches left, sleep for 10 seconds.
            # This allows the Google Per-Minute API bucket to refresh smoothly.
            if i + SAFE_BATCH_SIZE < len(texts_to_embed):
                logger.info(
                    "⏱️ Sleeping for 10 seconds to protect Free Tier RPM limits..."
                )
                time.sleep(10)

        embedded_docs = []

        # Map vectors back safely into your target dictionary format matching the original index
        for idx, chunk in enumerate(chunks):
            vector = all_embeddings[idx]

            embedded_docs.append(
                {
                    "id": chunk.metadata.chunk_id,
                    "text": chunk.page_content,
                    "embedding": vector,
                    "metadata": asdict(chunk.metadata),
                }
            )

        return embedded_docs
