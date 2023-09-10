include *.mk

cluster=qdrant
export KUBECONFIG=$(HOME)/.k3d/kubeconfig-$(cluster).yaml

## create cluster and deploy qdrant
kubes: cluster qdrant

## create k3s cluster
cluster:
	k3d cluster create $(cluster) --registry-create $(cluster)-registry:0.0.0.0:5550 \
		-p 6333:80@loadbalancer --wait
	@k3d kubeconfig write $(cluster) > /dev/null
	@echo "Probing until cluster is ready (~60 secs)..."
	@while ! kubectl get crd ingressroutes.traefik.containo.us 2> /dev/null ; do sleep 10 && echo $$((i=i+10)); done
	@echo -e "\nTo use your cluster set:\n"
	@echo "export KUBECONFIG=$(KUBECONFIG)"

## deploy qdrant to kubes
qdrant:
	helm repo add qdrant https://qdrant.github.io/qdrant-helm
	helm repo update qdrant
	helm upgrade --install qdrant qdrant/qdrant --version=0.5.0 --values infra/values.yaml --wait --debug > /dev/null

## fetch cluster endpoint
ping:
	curl -s http://localhost:6333/cluster | jq .

## show kube logs
logs:
	kubectl logs -l "app.kubernetes.io/name=qdrant,app.kubernetes.io/instance=qdrant" -f --tail=-1

## forward traefik dashboard
tdashboard:
	@echo Forwarding traefik dashboard to http://localhost:8999/dashboard/
	tpod=$$(kubectl get pod -n kube-system -l app.kubernetes.io/name=traefik -o custom-columns=:metadata.name --no-headers=true) && \
		kubectl -n kube-system port-forward $$tpod 8999:9000
