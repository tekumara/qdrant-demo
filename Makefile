include *.mk

cluster?=qdrant
export KUBECONFIG=$(HOME)/.k3d/kubeconfig-$(cluster).yaml

## create cluster and deploy qdrant
kubes: cluster qdrant

## create k3s cluster
cluster:
	k3d cluster create $(cluster) -p 6333:80@loadbalancer --wait
	@k3d kubeconfig write $(cluster) > /dev/null
	@echo "Probing until cluster is ready (~60 secs)..."
	@while ! kubectl get crd ingressroutes.traefik.containo.us 2> /dev/null ; do sleep 10 && echo $$((i=i+10)); done
	@echo -e "\nTo use your cluster set:\n"
	@echo "export KUBECONFIG=$(KUBECONFIG)"

## deploy qdrant to kubes
qdrant:
	helm repo add qdrant https://qdrant.github.io/qdrant-helm
	helm repo update qdrant
	helm upgrade --install qdrant qdrant/qdrant --version=0.5.1 --values infra/values.yaml --wait --debug > /dev/null

## fetch cluster endpoint
ping:
	curl -s http://localhost:6333/cluster | jq .

## show kube logs
logs:
	kubectl logs -l "app.kubernetes.io/name=qdrant,app.kubernetes.io/instance=qdrant" -f --tail=-1
