include *.mk
include .envrc

cluster?=qdrant

## install demo, create k3d cluster and deploy
all: install kubes deploy

## create k3d cluster
kubes:
	k3d cluster create $(cluster) --config k3d-cluster.yaml --wait
	@k3d kubeconfig write $(cluster) > /dev/null
	@echo -e "\nTo use your cluster set:\n"
	@echo "export KUBECONFIG=$(KUBECONFIG)"

## deploy qdrant to kubes
deploy:
	kubectl apply -f infra/ingress.yaml
	helm upgrade --install --repo https://qdrant.github.io/qdrant-helm qdrant qdrant --version=0.7.4 --values infra/values.yaml --wait --debug > /dev/null

## fetch cluster endpoint
ping:
	curl -sS -m 5 http://localhost:6333/cluster
	@curl -sS -m 5 http://localhost:6333/cluster | jq -e '.status == "ok"' > /dev/null

## create birds collection
birds: $(venv)
	$(venv)/bin/python -m demo.qdrant

## search birds collection
search:
	@curl -sS -X POST 'http://localhost:6333/collections/birds/points/search' -H 'Content-Type: application/json' --data-raw '{"vector": [0.1,0.1,0.1,0.1], "top": 3, "with_payload":true}'

## list all points in the birds collection
scroll:
	@curl -sS 'http://localhost:6333/collections/birds/points/scroll' -H 'Content-Type: application/json' --data-raw '{"limit":10,"offset":null,"with_payload":true,"with_vector":true}'

## list all points in the birds collection
count:
	@curl -sS 'http://localhost:6333/collections/birds/points/count' -H 'Content-Type: application/json' --data-raw '{}'

## show kube logs
logs:
	kubectl logs -l "app.kubernetes.io/name=qdrant,app.kubernetes.io/instance=qdrant" -f --tail=-1

## perf test:
perf:
	k6 run --duration 60s infra/perf/k6.js
