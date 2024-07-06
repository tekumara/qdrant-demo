#!/usr/bin/env bash

set -euo pipefail

cleanup() {
    local exit_status="$?"
    kill "$k6_pid"
    wait "$k6_pid" 2> /dev/null || true
    echo "k6 stopped" >&2
    exit "${exit_status}"
}

echo Start perf workload
k6 run --duration 60s infra/perf/k6.js &
k6_pid=$!

# delete a pod and run the healthcheck
# when healthcheck fails the perf test will be terminated
trap 'cleanup' ERR
for _ in {1..4};
do
    sleep 5
    kubectl delete pod qdrant-1
    sleep 10
    .venv/bin/python -m src.demo.healthcheck --assert-counts
done
cleanup
