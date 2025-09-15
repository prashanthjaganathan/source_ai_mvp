#!/bin/bash

# Source AI MVP - Complete Startup Script
# This script starts all backend services and the frontend

echo "🚀 Starting Source AI MVP Services..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Navigate to project root
cd "$(dirname "$0")"

echo -e "${BLUE}📁 Project directory: $(pwd)${NC}"

# Step 1: Start Database Services
echo -e "\n${BLUE}🗄️  Step 1: Starting Database Services...${NC}"
cd backend
docker-compose up -d postgres redis
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database services started${NC}"
else
    echo -e "${RED}❌ Failed to start database services${NC}"
    exit 1
fi

# Wait for database to be ready
sleep 5

# Step 2: Start Users Service
echo -e "\n${BLUE}👥 Step 2: Starting Users Service...${NC}"
if check_port 8001; then
    cd services/users
    set -a && source ../../../.env && set +a
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > ../../../logs/users_service.log 2>&1 &
    USERS_PID=$!
    echo $USERS_PID > ../../../logs/users_service.pid
    wait_for_service 8001 "Users Service"
else
    echo -e "${YELLOW}⚠️  Users Service already running on port 8001${NC}"
fi

# Step 3: Start Photos Service
echo -e "\n${BLUE}📸 Step 3: Starting Photos Service...${NC}"
if check_port 8002; then
    cd ../photos
    set -a && source ../../../.env && set +a
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > ../../../logs/photos_service.log 2>&1 &
    PHOTOS_PID=$!
    echo $PHOTOS_PID > ../../../logs/photos_service.pid
    wait_for_service 8002 "Photos Service"
else
    echo -e "${YELLOW}⚠️  Photos Service already running on port 8002${NC}"
fi

# Step 4: Start Scheduler Service (with S3)
echo -e "\n${BLUE}⏰ Step 4: Starting Scheduler Service (with S3)...${NC}"
if check_port 8003; then
    cd ../scheduler
    set -a && source ../../../.env && set +a
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload > ../../../logs/scheduler_service.log 2>&1 &
    SCHEDULER_PID=$!
    echo $SCHEDULER_PID > ../../../logs/scheduler_service.pid
    wait_for_service 8003 "Scheduler Service"
else
    echo -e "${YELLOW}⚠️  Scheduler Service already running on port 8003${NC}"
fi

# Step 5: Start Frontend
echo -e "\n${BLUE}📱 Step 5: Starting Frontend...${NC}"
cd ../../frontend
if check_port 8081; then
    nohup npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    echo -e "${GREEN}✅ Frontend started (Metro bundler)${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend already running on port 8081${NC}"
fi

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Final Status Check
echo -e "\n${BLUE}🔍 Final Status Check...${NC}"
echo "========================"

# Check all services
services=("8001:Users Service" "8002:Photos Service" "8003:Scheduler Service")
all_healthy=true

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name (Port $port) - Healthy${NC}"
    else
        echo -e "${RED}❌ $name (Port $port) - Not responding${NC}"
        all_healthy=false
    fi
done

echo -e "\n${BLUE}📋 Service URLs:${NC}"
echo "=================="
echo "Users Service:     http://localhost:8001"
echo "Photos Service:    http://localhost:8002"
echo "Scheduler Service: http://localhost:8003"
echo "Frontend:          http://localhost:8081 (Metro bundler)"
echo ""

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}🎉 All services started successfully!${NC}"
    echo -e "${BLUE}💡 To stop all services, run: ./stop_all_services.sh${NC}"
else
    echo -e "${RED}⚠️  Some services may not be running properly. Check the logs in the logs/ directory.${NC}"
fi

echo -e "\n${BLUE}📝 Logs are available in: logs/${NC}"
echo "  - users_service.log"
echo "  - photos_service.log"
echo "  - scheduler_service.log"
echo "  - frontend.log"

