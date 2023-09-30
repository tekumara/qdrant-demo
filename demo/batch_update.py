from typing import Iterable, List

from qdrant_client import QdrantClient, models
from qdrant_client.conversions import common_types as types

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
    qdrant_client = QdrantClient(host="127.0.0.1", port=6333, prefer_grpc=True, timeout=60*5)

    payload = BIRDS

    vectors = mock_vectors(VECTOR_SIZE, len(payload))

    print("recreate_collection")
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE, distance=models.Distance.EUCLID
        ),
        replication_factor=3
    )

    print("batch_update_points")

    point1 = models.PointStruct(
        id=1,
        vector=[1.0, 1.0, 1.0, 1.0],
        payload=dict(name="Wren", species="Troglodytes troglodytes", lifespan=7),
    )

    point2 = models.PointStruct(
        id=1,
        vector=[1.0, 1.0, 1.0, 1.0],
        payload=dict(name="Wren", species="A nice bird", lifespan=10),
    )

    up_op1 = models.UpsertOperation(upsert=models.PointsList(points=[point1]))
    up_op2 = models.UpsertOperation(upsert=models.PointsList(points=[point2]))
    del_op = models.DeleteOperation(
        delete=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="name", match=models.MatchValue(value="Wren")
                    )
                ]
            )
        )
    )

    ops = [up_op1, del_op, up_op2] * 10000

    qdrant_client.batch_update_points(
        collection_name=COLLECTION_NAME,
        update_operations=ops,
        wait=False,
        ordering=types.WriteOrdering.WEAK,
    )

    print("scroll")
    res = qdrant_client.scroll(
        collection_name=COLLECTION_NAME,
    )
    print(res)


if __name__ == "__main__":
    main()
