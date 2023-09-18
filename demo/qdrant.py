from typing import Iterable, List

from qdrant_client import QdrantClient, models

BATCH_SIZE = 256
COLLECTION_NAME = "birds"
VECTOR_SIZE = 4

BIRDS = [
    dict(name="Wren", species="Troglodytes troglodytes", lifespan=7),
    dict(name="Bullfinch", species="Pyrrhula pyrrhula", lifespan=9),
    dict(name="Sand martin", species="Riparia riparia", lifespan=8),
    dict(name="Great tit", species="Parus major", lifespan=14),
    dict(name="Barn owl", species="Tyto alba", lifespan=15),
    dict(name="Rook	Corvus", species="frugilegus", lifespan=23),
    dict(name="Goshawk", species="Accipiter gentilis", lifespan=19),
    dict(name="Black Grouse", species="Tetrao tetrix", lifespan=4),
    dict(name="Common tern", species="Sterna hirundo", lifespan=33),
    dict(name="Buzzard", species="Buteo buteo", lifespan=26),
    dict(name="Purple sandpiper", species="Calidris maritima", lifespan=14),
    dict(name="Manx shearwater", species="Puffinus puffinus", lifespan=50),
]


def mock_vectors(size: int, count: int) -> Iterable[List[float]]:
    for i in range(count):
        vector = [float(i)] * size
        yield vector


def main():
    qdrant_client = QdrantClient(host="127.0.0.1", port=6333)

    payload = BIRDS

    vectors = mock_vectors(VECTOR_SIZE, len(payload))

    print("recreate_collection")
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE, distance=models.Distance.EUCLID
        ),
    )

    print("upload_collection")
    qdrant_client.upload_collection(
        collection_name=COLLECTION_NAME,
        vectors=vectors,
        payload=payload,
        ids=None,
        batch_size=BATCH_SIZE,
        parallel=2,
    )

    print("create_payload_index")
    qdrant_client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="species",
        field_schema=models.TextIndexParams(
            type=models.TextIndexType.TEXT,
            tokenizer=models.TokenizerType.PREFIX,
            min_token_len=1,
            max_token_len=20,
            lowercase=True,
        ),
    )

    res = qdrant_client.search(
        collection_name=COLLECTION_NAME, query_vector=[float(1)] * VECTOR_SIZE, limit=3
    )
    print(res)


if __name__ == "__main__":
    main()
