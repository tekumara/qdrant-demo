import argparse
import sys
import pydantic_core
from qdrant_client import QdrantClient, models
import qdrant_client.http.exceptions
from qdrant_client.conversions import common_types as types
import stamina

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

    # retry on 404, which occurs when a node is not yet ready
    @stamina.retry(on=qdrant_client.http.exceptions.UnexpectedResponse, wait_initial=1.0, attempts=5)
    def count(qc: QdrantClient) -> int:
        return qc.count(collection_name=col_name).count

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

    count0 = count(qc0)
    count1 = count(qc1)
    count2 = count(qc2)
    print(f"{count0=}")
    print(f"{count1=}")
    print(f"{count2=}")
    if args.assert_counts and (count0 != count1 or count1 != count2):
        sys.exit("Counts not equal")

    empty0 = empty_payloads(qc0)
    empty1 = empty_payloads(qc1)
    empty2 = empty_payloads(qc2)
    print(f"empty0={pydantic_core.to_jsonable_python(empty0)}")
    print(f"empty1={pydantic_core.to_jsonable_python(empty1)}")
    print(f"empty2={pydantic_core.to_jsonable_python(empty2)}")
    if args.assert_payloads and (len(empty0) + len(empty1) + len(empty2) > 0):
        sys.exit("Empty payloads")

if __name__ == "__main__":
    main()
