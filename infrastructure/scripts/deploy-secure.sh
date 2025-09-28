#!/bin/bash

# Secure Deployment Script for Microservices Testing Suite
set -euo pipefail  # Exit on error, undefined vars, pipe failures

echo "🔒 Starting secure deployment of Microservices Testing Suite..."

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found. Please install kubectl."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Create namespace
create_namespace() {
    echo "🏗️ Creating namespace..."
    kubectl create namespace microservices --dry-run=client -o yaml | kubectl apply -f -
}

# Deploy secrets first
deploy_secrets() {
    echo "🔐 Deploying secrets..."
    
    # Elasticsearch secret
    if kubectl get secret elasticsearch-secret -n microservices &> /dev/null; then
        echo "⚠️ Elasticsearch secret already exists, skipping..."
    else
        kubectl apply -f ../logging/elasticsearch-secret.yaml
        echo "✅ Elasticsearch secret deployed"
    fi
    
    # Grafana secret
    if kubectl get secret grafana-secret -n microservices &> /dev/null; then
        echo "⚠️ Grafana secret already exists, skipping..."
    else
        kubectl apply -f ../monitoring/grafana-secret.yaml
        echo "✅ Grafana secret deployed"
    fi
    
    # TLS secret for Istio
    if kubectl get secret microservices-tls-secret -n istio-system &> /dev/null; then
        echo "⚠️ TLS secret already exists, skipping..."
    else
        kubectl apply -f ../istio/tls-secret.yaml
        echo "✅ TLS secret deployed"
    fi
}

# Build and push images with specific tags
build_images() {
    echo "🏗️ Building Docker images with specific tags..."
    
    cd ../../services
    
    # Build user service
    echo "Building user-service:v1.0.0..."
    if docker build -t user-service:v1.0.0 ./user-service/; then
        echo "✅ User service built successfully"
    else
        echo "❌ Failed to build user service"
        exit 1
    fi
    
    # Build order service
    echo "Building order-service:v1.0.0..."
    if docker build -t order-service:v1.0.0 ./order-service/; then
        echo "✅ Order service built successfully"
    else
        echo "❌ Failed to build order service"
        exit 1
    fi
    
    # Build payment service
    echo "Building payment-service:v1.0.0..."
    if docker build -t payment-service:v1.0.0 ./payment-service/; then
        echo "✅ Payment service built successfully"
    else
        echo "❌ Failed to build payment service"
        exit 1
    fi
    
    cd ../infrastructure/scripts
}

# Deploy infrastructure
deploy_infrastructure() {
    echo "🏗️ Deploying infrastructure components..."
    
    # Deploy monitoring stack
    echo "Deploying monitoring stack..."
    kubectl apply -f ../monitoring/
    
    # Deploy logging stack
    echo "Deploying logging stack..."
    kubectl apply -f ../logging/
    
    # Deploy services
    echo "Deploying microservices..."
    kubectl apply -f ../kubernetes/
    
    # Deploy Istio configuration
    echo "Deploying Istio configuration..."
    kubectl apply -f ../istio/
    
    echo "✅ Infrastructure deployed"
}

# Wait for deployments
wait_for_deployments() {
    echo "⏳ Waiting for deployments to be ready..."
    
    kubectl wait --for=condition=available --timeout=300s deployment/user-service -n microservices
    kubectl wait --for=condition=available --timeout=300s deployment/order-service -n microservices
    kubectl wait --for=condition=available --timeout=300s deployment/payment-service -n microservices
    kubectl wait --for=condition=available --timeout=300s deployment/grafana -n microservices
    
    echo "✅ All deployments are ready"
}

# Verify deployment
verify_deployment() {
    echo "🔍 Verifying deployment..."
    
    echo "Services status:"
    kubectl get pods -n microservices
    
    echo "Checking service health endpoints..."
    kubectl port-forward svc/user-service 8001:8001 -n microservices &
    PF_PID1=$!
    sleep 5
    
    if curl -f http://localhost:8001/health &> /dev/null; then
        echo "✅ User service health check passed"
    else
        echo "⚠️ User service health check failed"
    fi
    
    kill $PF_PID1 2>/dev/null || true
    
    echo "✅ Deployment verification completed"
}

# Main execution
main() {
    check_prerequisites
    create_namespace
    deploy_secrets
    build_images
    deploy_infrastructure
    wait_for_deployments
    verify_deployment
    
    echo "🎉 Secure deployment completed successfully!"
    echo ""
    echo "📊 Access dashboards:"
    echo "• Grafana: kubectl port-forward svc/grafana 3000:3000 -n microservices"
    echo "• Kibana: kubectl port-forward svc/kibana 5601:5601 -n microservices"
    echo ""
    echo "🧪 Run tests:"
    echo "cd ../../testing-suite && python utils/test_runner.py --test-type all"
}

# Execute main function
main "$@"