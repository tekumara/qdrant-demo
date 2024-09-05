import json
import os
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.conversions import common_types as types

import argparse


def download_payloads(
    qc: QdrantClient,
    collection_name: str,
    limit: Optional[int] = None,
    batch_size: int = 100,
) -> List[Dict]:
    all_payloads = []
    offset: Optional[types.PointId] = None

    while True:
        current_batch_size = (
            min(batch_size, limit - len(all_payloads)) if limit else batch_size
        )
        search_result, next_offset = qc.scroll(
            collection_name=collection_name,
            limit=current_batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        if not search_result:
            break

        payloads = [item.payload for item in search_result]
        all_payloads.extend(payloads)

        if limit and len(all_payloads) >= limit:
            all_payloads = all_payloads[:limit]
            break

        if next_offset is None:
            break

        offset = next_offset

    return all_payloads


def main():
    parser = argparse.ArgumentParser(
        description="Download payloads from a Qdrant collection."
    )
    parser.add_argument(
        "collection_name",
        help="Name of the Qdrant collection to download payloads from",
    )
    parser.add_argument(
        "--host", default="localhost", help="Qdrant server host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=6333, help="Qdrant HTTP server port (default: 6333)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of payloads to download (default: all)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of payloads to retrieve in each batch (default: 100)",
    )
    args = parser.parse_args()

    api_key = os.environ.get('API_KEY')

    qc = QdrantClient(host=args.host, prefer_grpc=False, port=args.port, api_key=api_key, https=False)

    payloads = download_payloads(qc, args.collection_name, args.limit, args.batch_size)

    print(json.dumps(payloads))


if __name__ == "__main__":
    main()
