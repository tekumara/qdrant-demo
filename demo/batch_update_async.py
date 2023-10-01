import asyncio
from typing import Iterable, List

from qdrant_client import QdrantClient, grpc
from qdrant_client.conversions.conversion import payload_to_grpc

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


async def main():
    qdrant_client = QdrantClient(
        host="127.0.0.1", port=6333, prefer_grpc=True, timeout=20
    )

    grpc_collections = qdrant_client.async_grpc_collections
    grpc_points = qdrant_client.async_grpc_points

    payload = BIRDS

    mock_vectors(VECTOR_SIZE, len(payload))

    print("List")
    res = await grpc_collections.List(grpc.ListCollectionsRequest(), timeout=1.0)
    print(res)

    print("Delete")
    await grpc_collections.Delete(
        grpc.DeleteCollection(collection_name=COLLECTION_NAME)
    )

    print("Create")
    await grpc_collections.Create(
        grpc.CreateCollection(
            collection_name=COLLECTION_NAME,
            vectors_config=grpc.VectorsConfig(
                params=grpc.VectorParams(
                    size=VECTOR_SIZE, distance=grpc.Distance.Euclid
                )
            ),
            replication_factor=3,
            write_consistency_factor=3
        )
    )

    point1 = grpc.PointStruct(
        id=grpc.PointId(num=1),
        vectors=grpc.Vectors(vector=grpc.Vector(data=[1.0, 1.0, 1.0, 1.0])),
        payload=payload_to_grpc(
            dict(name="Wren", species="Troglodytes troglodytes", lifespan=7)
        ),
    )

    point2 = grpc.PointStruct(
        id=grpc.PointId(num=1),
        vectors=grpc.Vectors(vector=grpc.Vector(data=[1.0, 1.0, 1.0, 1.0])),
        payload=payload_to_grpc(dict(name="Wren", species="A nice bird", lifespan=10)),
    )

    up_op1 = grpc.PointsUpdateOperation(
        upsert=grpc.PointsUpdateOperation.PointStructList(points=[point1])
    )
    up_op2 = grpc.PointsUpdateOperation(
        upsert=grpc.PointsUpdateOperation.PointStructList(points=[point2])
    )

    del_op = grpc.PointsUpdateOperation(
        delete=grpc.PointsSelector(
            filter=grpc.Filter(
                must=[
                    grpc.Condition(
                        field=grpc.FieldCondition(
                            key="name", match=grpc.Match(keyword="Wren")
                        )
                    )
                ]
            )
        )
    )

    ops = [up_op1, del_op, up_op2] * 10000

    print("UpdateBatch")
    await grpc_points.UpdateBatch(
        grpc.UpdateBatchPoints(
            collection_name=COLLECTION_NAME, operations=ops, wait=False
        )
    )

    print("Scroll")
    res = await grpc_points.Scroll(
        grpc.ScrollPoints(
            collection_name=COLLECTION_NAME,
        )
    )
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
