#!/bin/bash

set -e

echo "🧹 Cleaning up Microservices Testing Suite"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📋 Removing Kubernetes resources...${NC}"

# Remove Istio configurations
echo "Removing Istio configurations..."
kubectl delete -f ../istio/ --ignore-not-found=true

# Remove monitoring stack
echo "Removing monitoring stack..."
kubectl delete -f ../monitoring/ --ignore-not-found=true

# Remove services
echo "Removing services..."
kubectl delete -f ../kubernetes/user-service.yaml --ignore-not-found=true
kubectl delete -f ../kubernetes/order-service.yaml --ignore-not-found=true
kubectl delete -f ../kubernetes/payment-service.yaml --ignore-not-found=true

# Remove namespace (this will remove everything in the namespace)
echo "Removing namespace..."
kubectl delete namespace microservices --ignore-not-found=true

echo -e "${GREEN}✅ Cleanup completed!${NC}"