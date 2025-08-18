# debug_qdrant.py
from qdrant_client import QdrantClient
import json

# Connect to your local Qdrant instance
client = QdrantClient(host="localhost", port=6333)

# 1. List all collections
collections = client.get_collections()
print("\n📂 Collections in Qdrant:")
for coll in collections.collections:
    print(f" - {coll.name}")

# Pick the first collection for inspection
if collections.collections:
    collection_name = collections.collections[0].name
    print(f"\n🔍 Inspecting collection: {collection_name}")

    # 2. Get collection info
    info = client.get_collection(collection_name=collection_name)
    print(f"Vector size: {info.vectors_count}, Dim: {info.config.params.vectors.size}")

    # 3. Retrieve a sample point
    points = client.scroll(
        collection_name=collection_name,
        limit=3,
        with_payload=True,
        with_vectors=False
    )

    print("\n📄 Sample points:")
    for point in points[0]:
        print(f"ID: {point.id}")
        print(f"Payload:\n{json.dumps(point.payload, indent=2)}\n")

else:
    print("\n⚠️ No collections found in Qdrant.")
