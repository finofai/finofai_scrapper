from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def ensure_collection(client: QdrantClient,
                      name: str,
                      vector_size: int,
                      distance: Distance = Distance.COSINE):
    # fetch existing collections
    existing = [col.name for col in client.get_collections().collections]
    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=distance)
        )
        print(f"Collection '{name}' created.")
    else:
        print(f"Collection '{name}' already exists.")

# ———————————————— usage ————————————————

client = QdrantClient(url="http://localhost:6333")

# e.g. for your stock_news embeddings (768-dim, cosine similarity)
ensure_collection(client, name="stock_news", vector_size=768, distance=Distance.COSINE)
