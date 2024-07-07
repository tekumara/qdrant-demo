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

# on ctrl+c or when healthcheck below fails the perf test will be terminated
trap cleanup INT ERR

# loop while k6 is still running in background
while ps -p $! > /dev/null; do
    # delete a pod and run the healthcheck
    sleep 5
    kubectl delete pod qdrant-1
    sleep 8
    if [[ "$1" == "upsert" ]]; then
        # try multiple attempts in case we have counted whilst an upsert was in flight
        .venv/bin/python -m src.demo.healthcheck --assert-counts --assert-counts-attempts 4
    fi
    if [[ "$1" == "delete" ]]; then
        .venv/bin/python -m src.demo.healthcheck --assert-payload
    fi
done

wait "$k6_pid"
