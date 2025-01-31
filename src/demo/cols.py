import argparse
import os
from qdrant_client import QdrantClient
import json
from typing import Dict, Any


def all_collections_details(
    host: str = "localhost", port: int = 6333, api_key: str | None = None
) -> None:
    """List all collections and their complete details as JSON."""

    client = QdrantClient(
        host=host,
        port=port,
        api_key=api_key,
        https=False if host == "localhost" else True,
    )

    # Get list of all collections
    collections = client.get_collections()

    if not collections.collections:
        print(json.dumps({"message": "No collections found"}, indent=2))
        return

    # Store details for all collections
    all_details: Dict[str, Any] = {}

    # Get complete details for each collection
    for collection in collections.collections:
        name = collection.name
        details = client.get_collection(collection_name=name)
        # Convert to dict for JSON serialization
        all_details[name] = details.model_dump()

    # Print formatted JSON
    print(json.dumps(all_details, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List all collections and their details"
    )
    parser.add_argument("--host", default="localhost", help="Qdrant server host")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant server port")

    args = parser.parse_args()
    api_key = os.getenv("API_KEY")
    all_collections_details(host=args.host, port=args.port, api_key=api_key)
