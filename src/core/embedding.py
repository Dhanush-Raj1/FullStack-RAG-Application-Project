import os
import time
import logging
from dataclasses import asdict
from typing import Dict, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

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

    def embed_text(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        return response.embeddings[0].values

    def embed_query(self, query: str) -> List[float]:
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
    
            # Extract all text blocks to perform combined batch processing
            texts_to_embed = [chunk.page_content for chunk in chunks]
            all_embeddings = []
    
            # DROP BATCH SIZE: Free tier allows a max of 100 items per minute bucket.
            # Running 15 chunks per batch keeps us completely safe.
            SAFE_BATCH_SIZE = 15 
            
            logger.info(f"Splitting {len(chunks)} chunks into safe sub-batches of {SAFE_BATCH_SIZE}...")
    
            for i in range(0, len(texts_to_embed), SAFE_BATCH_SIZE):
                batch = texts_to_embed[i : i + SAFE_BATCH_SIZE]
                
                current_batch_num = (i // SAFE_BATCH_SIZE) + 1
                total_batches = (len(texts_to_embed) + SAFE_BATCH_SIZE - 1) // SAFE_BATCH_SIZE
                
                logger.info(f"🚀 Sending batch {current_batch_num}/{total_batches} (Size: {len(batch)})...")
                
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
                )
                
                # Extract individual vector records from this specific batch's response
                for emb in response.embeddings:
                    all_embeddings.append(emb.values)
    
                # --- FREE TIER THROTTLING GUARDRAIL ---
                # If there are more batches left, sleep for 10 seconds.
                # This allows the Google Per-Minute API bucket to refresh smoothly.
                if i + SAFE_BATCH_SIZE < len(texts_to_embed):
                    logger.info("⏱️ Sleeping for 10 seconds to protect Free Tier RPM limits...")
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


# import os
# import time
# import logging
# from dataclasses import asdict
# from typing import Dict, List

# from dotenv import load_dotenv
# from google import genai
# from google.genai import types

# logger = logging.getLogger(__name__)


# class GeminiEmbeddingGenerator:
#     def __init__(self, model_name: str):
#         load_dotenv()

#         api_key = os.getenv("GEMINI_API_KEY")

#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not found in environment.")

#         self.client = genai.Client(api_key=api_key)
#         self.model_name = model_name
#         # Gemini API hard limit for a single batch operation
#         self._MAX_BATCH_SIZE = 100 

#     def embed_text(self, text: str) -> List[float]:
#         response = self.client.models.embed_content(
#             model=self.model_name,
#             contents=text,
#             config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
#         )
#         return response.embedding.values

#     def embed_query(self, query: str) -> List[float]:
#         response = self.client.models.embed_content(
#             model=self.model_name,
#             contents=query,
#             config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
#         )

#         if hasattr(response, "embedding") and response.embedding:
#             return response.embedding.values

#         return response.embeddings[0].values

#     def embed_documents(self, chunks) -> List[Dict]:
#         if not chunks:
#             return []

#         # Extract all text blocks to perform combined batch processing
#         texts_to_embed = [chunk.page_content for chunk in chunks]
#         all_embeddings = []

#         logger.info(f"Splitting {len(chunks)} chunks into batches of {self._MAX_BATCH_SIZE}...")

#         # Process in windows of 100 max elements to satisfy BatchEmbedContentsRequest parameters
#         for i in range(0, len(texts_to_embed), self._MAX_BATCH_SIZE):
#             batch = texts_to_embed[i : i + self._MAX_BATCH_SIZE]
            
#             logger.info(f"Embedding batch {(i // self._MAX_BATCH_SIZE) + 1} (Size: {len(batch)})...")
            
#             response = self.client.models.embed_content(
#                 model=self.model_name,
#                 contents=batch,
#                 config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
#             )
            
#             # Extract individual vector records from this specific batch's response
#             for emb in response.embeddings:
#                 all_embeddings.append(emb.values)

#             # Throttle execution for 2 seconds between API hits to keep the 
#             # free tier TPM (Tokens Per Minute) metric completely safe.
#             if i + self._MAX_BATCH_SIZE < len(texts_to_embed):
#                 logger.info("Throttling request pipeline for 2 seconds to respect free tier boundaries...")
#                 time.sleep(2)

#         embedded_docs = []

#         # Map vectors back safely into your target dictionary format matching the original index
#         for idx, chunk in enumerate(chunks):
#             vector = all_embeddings[idx]

#             embedded_docs.append(
#                 {
#                     "id": chunk.metadata.chunk_id,
#                     "text": chunk.page_content,
#                     "embedding": vector,
#                     "metadata": asdict(chunk.metadata),
#                 }
#             )

#         return embedded_docs



# import os
# from dataclasses import asdict
# from typing import Dict, List

# from dotenv import load_dotenv
# from google import genai
# from google.genai import types


# class GeminiEmbeddingGenerator:
#     def __init__(self, model_name: str):
#         load_dotenv()

#         api_key = os.getenv("GEMINI_API_KEY")

#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not found in environment.")

#         self.client = genai.Client(api_key=api_key)

#         self.model_name = model_name

#     def embed_text(self, text: str) -> List[float]:
#         response = self.client.models.embed_content(
#             model=self.model_name,
#             contents=text,
#             config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
#         )

#         return response.embedding.values

#     def embed_query(self, query: str) -> List[float]:
#         response = self.client.models.embed_content(
#             model=self.model_name,
#             contents=query,
#             config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
#         )

#         if hasattr(response, "embedding") and response.embedding:
#             return response.embedding.values

#         return response.embeddings[0].values

#     def embed_documents(self, chunks) -> List[Dict]:

#         # Extract all text blocks to perform a combined batch request
#         texts_to_embed = [chunk.page_content for chunk in chunks]

#         response = self.client.models.embed_content(
#             model=self.model_name,
#             contents=texts_to_embed,
#             config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
#         )

#         embedded_docs = []

#         # When sending a list of texts, response.embeddings contains an iterable array list of records
#         for idx, chunk in enumerate(chunks):
#             vector = response.embeddings[idx].values

#             embedded_docs.append(
#                 {
#                     "id": chunk.metadata.chunk_id,
#                     "text": chunk.page_content,
#                     "embedding": vector,
#                     "metadata": asdict(chunk.metadata),
#                 }
#             )

#         return embedded_docs
