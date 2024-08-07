# qdrant demo

qdrant demo running in a local kubernetes cluster.

## Getting started

Prerequisites:

- [k3d](https://k3d.io/) (for creating a local kubernetes cluster)
- kubectl
- helm
- [k6](https://k6.io/docs/get-started/installation/) (for perf test)
- python 3.10+

Install python demo, create k3d cluster and deploy qdrant:

```
make all
```

Create `birds` collection:

```
make birds
```

Search:

```
make search
```

## Usage

Endpoints:

- [Web UI](https://qdrant.tech/documentation/interfaces/web-ui/): [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- [Metrics (prometheus)](https://qdrant.tech/documentation/guides/monitoring/): [http://localhost:6333/metrics](http://localhost:6333/metrics)
- [Telemetry](https://qdrant.tech/documentation/guides/telemetry/): [http://localhost:6333/telemetry](http://localhost:6333/telemetry)
- [Explore endpoints via Swagger UI](https://ui.qdrant.tech/)

Individual node Web UIs:

- [qdrant-0](http://qdrant-0.localhost:6333/dashboard)
- [qdrant-1](http://qdrant-1.localhost:6333/dashboard)
- [qdrant-2](http://qdrant-2.localhost:6333/dashboard)

## References

- [Quick Start using curl](https://github.com/qdrant/qdrant/blob/master/QUICK_START.md)
- [Quick Start using python](https://qdrant.tech/documentation/quick-start/)
- [API Docs](https://qdrant.github.io/qdrant/redoc/index.html)

## Known issues

### Internal communication channels are never protected by an API key nor bearer tokens

> Internal gRPC uses port 6335 by default if running in distributed mode. You must ensure that this port is not publicly reachable and can only be used for node communication

### Consistency of write operations is only guaranteed if the operation was accepted

[`write_consistency_factor`](https://qdrant.tech/documentation/guides/distributed_deployment/#write-consistency-factor) sets the number of replicas that must acknowledge the write for the operation to be accepted. To consistently accept writes, this implies that `write_consistency_factor` should be less than the number of replicas/nodes available during node restarts due to maintenance, upgrades, OOMKilled etc. See [#4626](https://github.com/qdrant/qdrant/issues/4626#issuecomment-2212415559).

### Other issues

- [#3360 Failed send message to http://qdrant-1.qdrant-headless:6335/ with error: Error in closure supplied to transport channel pool: status: Unavailable](https://github.com/qdrant/qdrant/issues/3360) during indexing because of OOM errors
- [Backpressure when updating points to avoid OOM](https://github.com/qdrant/qdrant/issues/4169)
- [Snapshot storage on S3 #3324](https://github.com/qdrant/qdrant/issues/3324)
- [Cluster level snapshot API #2763](https://github.com/qdrant/qdrant/issues/2763)
- [Optimistic concurrency control](https://github.com/qdrant/qdrant/issues/2749)
- [Points with empty payloads](https://github.com/qdrant/qdrant/issues/4627)
