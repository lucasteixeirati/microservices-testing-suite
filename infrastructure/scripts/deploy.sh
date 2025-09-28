#!/bin/bash

set -e

echo "🚀 Deploying Microservices Testing Suite to Kubernetes"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Check if istioctl is available
if ! command -v istioctl &> /dev/null; then
    echo -e "${YELLOW}⚠️ istioctl not found. Istio features will be skipped.${NC}"
    SKIP_ISTIO=true
else
    SKIP_ISTIO=false
fi

echo -e "${YELLOW}📋 Step 1: Creating namespace...${NC}"
kubectl apply -f ../kubernetes/namespace.yaml

echo -e "${YELLOW}📋 Step 2: Building and loading Docker images...${NC}"
cd ../../

# Build images
echo "Building user-service..."
docker build -t user-service:latest ./services/user-service/

echo "Building order-service..."
docker build -t order-service:latest ./services/order-service/

echo "Building payment-service..."
docker build -t payment-service:latest ./services/payment-service/

# Load images to kind cluster (if using kind)
if kubectl config current-context | grep -q "kind"; then
    echo "Loading images to kind cluster..."
    kind load docker-image user-service:latest
    kind load docker-image order-service:latest
    kind load docker-image payment-service:latest
fi

cd infrastructure/scripts/

echo -e "${YELLOW}📋 Step 3: Deploying services...${NC}"
kubectl apply -f ../kubernetes/user-service.yaml
kubectl apply -f ../kubernetes/order-service.yaml
kubectl apply -f ../kubernetes/payment-service.yaml

echo -e "${YELLOW}📋 Step 4: Waiting for services to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/user-service -n microservices
kubectl wait --for=condition=available --timeout=300s deployment/order-service -n microservices
kubectl wait --for=condition=available --timeout=300s deployment/payment-service -n microservices

if [ "$SKIP_ISTIO" = false ]; then
    echo -e "${YELLOW}📋 Step 5: Deploying Istio configuration...${NC}"
    kubectl apply -f ../istio/gateway.yaml
    kubectl apply -f ../istio/destination-rules.yaml
    kubectl apply -f ../istio/security-policies.yaml
    
    echo -e "${GREEN}✅ Istio configuration applied${NC}"
else
    echo -e "${YELLOW}⚠️ Step 5: Skipping Istio configuration${NC}"
fi

echo -e "${YELLOW}📋 Step 6: Deploying monitoring stack...${NC}"
kubectl apply -f ../monitoring/prometheus.yaml
kubectl apply -f ../monitoring/grafana.yaml

echo -e "${YELLOW}📋 Step 7: Deploying logging stack (ELK)...${NC}"
kubectl apply -f ../logging/elasticsearch.yaml
kubectl apply -f ../logging/kibana.yaml
kubectl apply -f ../logging/fluentd.yaml

echo -e "${YELLOW}📋 Step 8: Waiting for monitoring to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n microservices
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n microservices
kubectl wait --for=condition=available --timeout=300s deployment/kibana -n microservices

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "📊 Access Information:"
echo "====================="

# Get service URLs
if [ "$SKIP_ISTIO" = false ]; then
    GATEWAY_URL=$(kubectl get svc istio-ingressgateway -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -z "$GATEWAY_URL" ]; then
        GATEWAY_URL="localhost"
        echo "🌐 Services (via Istio Gateway): http://$GATEWAY_URL"
        echo "   - User Service: http://$GATEWAY_URL/users"
        echo "   - Order Service: http://$GATEWAY_URL/orders"  
        echo "   - Payment Service: http://$GATEWAY_URL/payments"
    fi
else
    echo "🌐 Services (port-forward required):"
    echo "   - User Service: kubectl port-forward svc/user-service 8001:8001 -n microservices"
    echo "   - Order Service: kubectl port-forward svc/order-service 8002:8002 -n microservices"
    echo "   - Payment Service: kubectl port-forward svc/payment-service 8003:8003 -n microservices"
fi

echo ""
echo "📊 Monitoring:"
echo "   - Grafana: kubectl port-forward svc/grafana 3000:3000 -n microservices"
echo "   - Prometheus: kubectl port-forward svc/prometheus 9090:9090 -n microservices"
echo ""
echo "📝 Logging:"
echo "   - Kibana: kubectl port-forward svc/kibana 5601:5601 -n microservices"
echo "   - Elasticsearch: kubectl port-forward svc/elasticsearch 9200:9200 -n microservices"
echo ""
echo "🧪 Run tests:"
echo "   cd ../../testing-suite && python utils/test_runner.py --test-type integration"