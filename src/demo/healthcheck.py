import argparse
import sys
import pydantic_core
from qdrant_client import QdrantClient, models
import qdrant_client.http.exceptions
from qdrant_client.conversions import common_types as types
import stamina

def healthcheck(assert_counts: bool, assert_payloads: bool, assert_attempts: int = 1) -> None:
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

    @stamina.retry(on=AssertionError, wait_initial=1.0, attempts=assert_attempts)
    def check_counts():
        count0 = count(qc0)
        count1 = count(qc1)
        count2 = count(qc2)
        print(f"{count0=}")
        print(f"{count1=}")
        print(f"{count2=}")
        if assert_counts and (count0 != count1 or count1 != count2):
            raise AssertionError("Counts not equal")

    def check_payloads():
        empty0 = empty_payloads(qc0)
        empty1 = empty_payloads(qc1)
        empty2 = empty_payloads(qc2)
        print(f"empty0={pydantic_core.to_json(empty0)}")
        print(f"empty1={pydantic_core.to_json(empty1)}")
        print(f"empty2={pydantic_core.to_json(empty2)}")
        if assert_payloads and (len(empty0) + len(empty1) + len(empty2) > 0):
            raise AssertionError("Empty payloads")

    check_counts()
    check_payloads()


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
        "-a", "--assert-counts-attempts",
        type=int,
        metavar="attempts",
        help="Number of attempts to assert counts.",
        default=1
    )


    parser.add_argument(
        "-p", "--assert-payloads",
        action='store_true',
        help="Assert payloads are not empty across all nodes.",
    )

    args = parser.parse_args()
    try:
        healthcheck(args.assert_counts, args.assert_payloads, args.assert_counts_attempts)
    except AssertionError as e:
        # pretty error without traceback
        sys.exit(f"AssertionError: {str(e)}")


if __name__ == "__main__":
    main()
