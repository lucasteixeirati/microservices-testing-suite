#!/bin/bash

# ANSI Color Codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 Checking Services Status...${NC}"
echo ""

check_service() {
    local service_name=$1
    local port=$2
    local url="http://localhost:${port}/health"

    # Use curl with a timeout and silent mode
    if curl -s --fail --max-time 5 "$url" > /dev/null; then
        echo -e "✅ ${GREEN}${service_name} is running on port ${port}${NC}"
    else
        echo -e "❌ ${RED}${service_name} is not responding on port ${port}${NC}"
    fi
}

echo -e "${YELLOW}📊 Service Health Checks:${NC}"
check_service "User Service" 8001
check_service "Order Service" 8002
check_service "Payment Service" 8003

echo ""
echo -e "${YELLOW}📊 Docker Status (if used):${NC}"
if ! command -v docker &> /dev/null; then
    echo "Docker command not found. Skipping Docker checks."
else
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

echo -e "\n${GREEN}Health check complete.${NC}"