from typing import Iterable, List
from qdrant_client import QdrantClient, models

COLLECTION_NAME = "k6-perf-test"
import httpx


def main():
    # use httpx because qdrantclient
    qdrant0_client = QdrantClient(
        host="qdrant-0.localhost", prefer_grpc=True, port=6333
    )
    qdrant1_client = QdrantClient(
        host="qdrant-1.localhost", prefer_grpc=True, port=6333
    )
    qdrant2_client = QdrantClient(
        host="qdrant-2.localhost", prefer_grpc=True, port=6333
    )

    count0 = qdrant0_client.count(
        collection_name=COLLECTION_NAME,
    )
    count1 = qdrant1_client.count(
        collection_name=COLLECTION_NAME,
    )
    count2 = qdrant2_client.count(
        collection_name=COLLECTION_NAME,
    )
    print(f"{count0.count=}")
    print(f"{count1.count=}")
    print(f"{count2.count=}")

    count0 = httpx.post(
        f"http://qdrant-0.localhost:6333/collections/{COLLECTION_NAME}/points/count", json={}
    ).json()["result"]["count"]
    count1 = httpx.post(
        f"http://qdrant-1.localhost:6333/collections/{COLLECTION_NAME}/points/count", json={}
    ).json()["result"]["count"]
    count2 = httpx.post(
        f"http://qdrant-2.localhost:6333/collections/{COLLECTION_NAME}/points/count", json={}
    ).json()["result"]["count"]
    print(f"{count0=}")
    print(f"{count1=}")
    print(f"{count2=}")


if __name__ == "__main__":
    main()
