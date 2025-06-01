from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

async def insert_points(points):
    client = QdrantClient(url="http://172.17.0.1:6333")

    if not points:
        print("No points to insert.")
        return

    # All your points share the same URL, so grab it once
    url = points[0].payload.get("url")
    if url:
        # Use `count_filter` instead of `filter`
        existing_count = client.count(
            collection_name="stock_news",
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="url",
                        match=MatchValue(value=url)
                    )
                ]
            ),
            exact=True
        ).count

        if existing_count > 0:
            print(f"Skipping upsert: URL already exists ({url})")
            return

    # If we get here, URL wasn’t found—upsert the batch
    try:
        client.upsert(
            collection_name="stock_news",
            points=points
        )
        print(f"Upserted {len(points)} points into 'stock_news'")
    except Exception as e:
        print("Exception occurred during upsert:", e)
