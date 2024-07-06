import argparse
import sys
import pydantic_core
from qdrant_client import QdrantClient, models
from qdrant_client.conversions import common_types as types


def main():
    parser = argparse.ArgumentParser(
        description="Qdrant healthcheck",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c", "--assert-counts",
        action='store_true',
        help="Assert collection count is the same for all nodes.",
    )

    parser.add_argument(
        "-p", "--assert-payloads",
        action='store_true',
        help="Assert payloads are not empty across all nodes.",
    )

    args = parser.parse_args()

    col_name = "k6-perf-test"
    qc0 = QdrantClient(host="qdrant-0.localhost", port=6333)
    qc1 = QdrantClient(host="qdrant-1.localhost", port=6333)
    qc2 = QdrantClient(host="qdrant-2.localhost", port=6333)

    def empty_payloads(qc: QdrantClient) -> list[types.Record]:
        points, _offset = qc.scroll(
            collection_name=col_name,
            limit=10,
            scroll_filter=models.Filter(
                must=[
                    models.IsEmptyCondition(is_empty=models.PayloadField(key="color"))
                ]
            ),
        )
        return points

    count0 = qc0.count(collection_name=col_name).count
    count1 = qc1.count(collection_name=col_name).count
    count2 = qc2.count(collection_name=col_name).count
    print(f"{count0=}")
    print(f"{count1=}")
    print(f"{count2=}")
    if args.assert_counts and (count0 != count1 or count1 != count2):
        sys.exit("Counts not equal")

    ep0 = empty_payloads(qc0)
    ep1 = empty_payloads(qc1)
    ep2 = empty_payloads(qc2)
    print(f"ep0={pydantic_core.to_jsonable_python(ep0)}")
    print(f"ep1={pydantic_core.to_jsonable_python(ep1)}")
    print(f"ep2={pydantic_core.to_jsonable_python(ep2)}")
    if args.assert_payloads and (len(ep0) + len(ep1) + len(ep2) > 0):
        sys.exit("Empty payloads")

if __name__ == "__main__":
    main()
