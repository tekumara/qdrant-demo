# qdrant demo

qdrant running in a local kubernetes cluster.

## Getting started

Prerequisites:

- [k3d](https://k3d.io/) (for creating a local kubernetes cluster)
- kubectl
- helm

Create k3d cluster and deploy qdrant:

```
make kubes
```

## Usage

Endpoints:

- [Web UI](https://qdrant.tech/documentation/interfaces/#qdrant-web-ui): [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- [Metrics](https://qdrant.tech/documentation/guides/monitoring/): [http://localhost:6333/metrics](http://localhost:6333/metrics)
- [Telemetry](https://qdrant.tech/documentation/guides/telemetry/): [http://localhost:6333/telemetry](http://localhost:6333/telemetry)
