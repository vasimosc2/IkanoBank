#!/usr/bin/env bash
set -euo pipefail

# Build the image inside Minikube's Docker daemon, deploy the manifests,
# and expose the service at a stable local URL.
#
# Usage:
#   ./scripts/run-k8s-local.sh
#
# Keep this terminal open while using http://localhost:8000.

minikube start

eval "$(minikube docker-env)"
docker build -t ikano-calc:latest .

kubectl apply -f kubernetes/deployment.yaml
kubectl rollout status deployment/ikano-calc

kubectl port-forward service/ikano-calc 8000:80
