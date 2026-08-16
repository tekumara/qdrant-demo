import argparse
import json
import sys
from typing import Dict, Any

import stamina
import qdrant_client.http.exceptions
from qdrant_client import QdrantClient


def get_cluster_info(
    host: str = "localhost", port: int = 6333, api_key: str | None = None
) -> Dict[str, Any]:
    """Get cluster info from a Qdrant node."""
    client = QdrantClient(
        host=host,
        port=port,
        api_key=api_key,
        https=False if host in ["localhost", "127.0.0.1"] else True,
    )
    
    # Direct HTTP API call for /cluster endpoint
    response = client.http.rest_client.get_cluster()
    return response.dict()


def check_cluster_status(attempts: int = 1) -> None:
    """Check cluster status for all three nodes."""
    qc0 = QdrantClient(host="qdrant-0.localhost", port=6333)
    qc1 = QdrantClient(host="qdrant-1.localhost", port=6333)
    qc2 = QdrantClient(host="qdrant-2.localhost", port=6333)
    
    nodes = [
        {"name": "qdrant-0", "client": qc0},
        {"name": "qdrant-1", "client": qc1},
        {"name": "qdrant-2", "client": qc2},
    ]
    
    # Dictionary to store cluster info for all nodes
    all_cluster_info: Dict[str, Any] = {}

    @stamina.retry(on=qdrant_client.http.exceptions.UnexpectedResponse, wait_initial=1.0, attempts=attempts)
    def get_info(name: str, qc: QdrantClient) -> Dict[str, Any]:
        try:
            return {"host": name, "cluster_info": get_cluster_info(host=f"{name}.localhost", port=6333)}
        except Exception as e:
            return {"host": name, "error": str(e)}

    # Get cluster info from each node
    for node in nodes:
        name = node["name"]
        client = node["client"]
        all_cluster_info[name] = get_info(name, client)

    # Print formatted JSON
    print(json.dumps(all_cluster_info, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Qdrant cluster status check",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-a", "--attempts",
        type=int,
        metavar="attempts",
        help="Number of retry attempts for API calls.",
        default=5
    )

    args = parser.parse_args()
    try:
        check_cluster_status(args.attempts)
    except Exception as e:
        sys.exit(f"Error: {str(e)}")


if __name__ == "__main__":
    main()