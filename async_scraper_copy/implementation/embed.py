import uuid

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import pytz
from datetime import datetime



def chunk_text(text: str, max_words: int):
    """
    Splits `text` into chunks of at most `max_words` words each.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def embed_article(id, headline, body,url):
    model = SentenceTransformer('FinLang/finance-embeddings-investopedia')
    # 1. Build your list of texts: headline + chunks of the body
    texts = [headline] + chunk_text(body, max_words=200)

    # 2. Embed them all at once
    embs = model.encode(texts, convert_to_numpy=True)
    #uuid_made = uuid.uuid4().hex

    points = []

    ist = pytz.timezone('Asia/Kolkata')

    # Current time in IST
    created_at = int(datetime.now(ist).timestamp())

    for idx, vec in enumerate(embs):
        # 3. Include the chunk’s raw text in the payload
        payload = {
            "article_id": id,
            "type":       "headline" if idx == 0 else "body",
            "chunk_idx":  idx,
            "text":       texts[idx] ,
            "url":url,
            "created_at":created_at
        }

        print(payload)

        points.append(
            rest.PointStruct(
                id=uuid.uuid4().hex,
                vector=vec.tolist(),
                payload=payload
            )
        )
    return points
#
# # Example inputs
# article_id = "stock-news-001"
# headline   = "Acme Corp Q1 Earnings Beat Analyst Expectations"
# body = """Quarterly earnings for Acme Corp came in at $1.2B, beating analyst expectations by 5%.
# The company cited strong demand in its consumer electronics segment, especially smart devices.
# CEO Jane Doe remarked that supply chain improvements contributed to higher margins.
# Investors will be watching guidance for the next quarter closely."""
#
# # Call the function
# embed_article(article_id, headline, body)