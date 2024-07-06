#!/usr/bin/env bash

set -euo pipefail

[[ "$#" -eq 0 || ("$1" != "upsert" && "$1" != "delete") ]] && \
    echo -e "Restart a node whilst running the perf upsert or delete workload\n\nUsage: $0 upsert/delete" >&2 && exit 42

cleanup() {
    local exit_status="$?"
    kill "$k6_pid"
    wait "$k6_pid" 2> /dev/null || true
    echo "k6 stopped" >&2
    exit "${exit_status}"
}

echo Start "$1" workload
if [[ "$1" == "upsert" ]]; then
    k6 run --duration 60s infra/perf/k6.js &
fi
if [[ "$1" == "delete" ]]; then
    DELETE_POINTS=true k6 run --duration 60s infra/perf/k6.js &
fi
k6_pid=$!

# delete a pod and run the healthcheck
# when healthcheck fails the perf test will be terminated
trap 'cleanup' ERR
for _ in {1..4};
do
    sleep 5
    kubectl delete pod qdrant-1
    sleep 5
    if [[ "$1" == "upsert" ]]; then
        .venv/bin/python -m src.demo.healthcheck --assert-counts
    fi
    if [[ "$1" == "delete" ]]; then
        .venv/bin/python -m src.demo.healthcheck --assert-payload
    fi
done
cleanup
