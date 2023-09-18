# qdrant demo

qdrant demo running in a local kubernetes cluster.

## Getting started

Prerequisites:

- [k3d](https://k3d.io/) (for creating a local kubernetes cluster)
- kubectl
- helm

Create k3d cluster and deploy qdrant:

```
make kubes
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

- [Web UI](https://qdrant.tech/documentation/interfaces/#qdrant-web-ui): [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- [Metrics (prometheus)](https://qdrant.tech/documentation/guides/monitoring/): [http://localhost:6333/metrics](http://localhost:6333/metrics)
- [Telemetry](https://qdrant.tech/documentation/guides/telemetry/): [http://localhost:6333/telemetry](http://localhost:6333/telemetry)
- [Explore endpoints via Swagger UI](https://ui.qdrant.tech/)

## References

- [Quick Start using curl](https://github.com/qdrant/qdrant/blob/master/QUICK_START.md)
- [Quick Start using python](https://qdrant.tech/documentation/quick-start/)
- [API Docs](https://qdrant.github.io/qdrant/redoc/index.html)
