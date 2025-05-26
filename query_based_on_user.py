from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("FinLang/finance-embeddings-investopedia")  # same as used during insert
query = "What is the auto industry today?"
query_vector = model.encode(query).tolist()


client = QdrantClient("http://localhost:6333")  # or your remote URL

search_result = client.search(
    collection_name="stock_news",
    query_vector=query_vector,
    limit=5,  # top 5 results
    with_payload=True  # to get your stored data back
)

for result in search_result:
    print(f"Score: {result.score}")
    print(f"Payload: {result.payload}")
