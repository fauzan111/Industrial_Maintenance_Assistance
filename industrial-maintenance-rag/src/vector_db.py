import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

class VectorDB:
    def __init__(self, collection_name: str = "manuals_rag"):
        self.collection_name = collection_name
        # Connect to Qdrant - assumes running locally or via Docker on default port
        # For production, use env vars for host/port
        self.client = QdrantClient(host="localhost", port=6333)
        # Load embedding model
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def ensure_collection(self):
        """Creates the collection if it doesn't exist."""
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            print(f"Creating collection {self.collection_name}...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
        else:
            print(f"Collection {self.collection_name} already exists.")

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Adds documents to the vector DB.
        documents: List of dicts with keys 'content', 'type', 'path', 'source_file'
        """
        points = []
        for doc in documents:
            # Generate embedding for the content (text or image description)
            vector = self.encoder.encode(doc['content']).tolist()
            
            # Create a payload
            payload = {
                "content": doc['content'],
                "type": doc['type'], # 'text' or 'image_desc'
                "path": doc.get('path'), # Path to image file if applicable
                "source_file": doc.get('source_file')
            }
            
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            ))
            
        # Upsert in batches if needed, but for now simple upsert
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Indexed {len(points)} documents.")

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches for relevant documents."""
        vector = self.encoder.encode(query).tolist()
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit
        ).points
        
        return [hit.payload for hit in results]

if __name__ == "__main__":
    # Test
    db = VectorDB()
    db.ensure_collection()
