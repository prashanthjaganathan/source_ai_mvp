#!/bin/bash

# Source AI MVP - Stop All Services Script
# This script stops all running services

echo "🛑 Stopping Source AI MVP Services..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to project root
cd "$(dirname "$0")"

# Function to stop service by PID file
stop_service_by_pid() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${BLUE}🛑 Stopping $service_name (PID: $pid)...${NC}"
            kill $pid
            sleep 2
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️  Force killing $service_name...${NC}"
                kill -9 $pid
            fi
            echo -e "${GREEN}✅ $service_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name was not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No PID file found for $service_name${NC}"
    fi
}

# Function to stop service by port
stop_service_by_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${BLUE}🛑 Stopping $service_name on port $port (PID: $pid)...${NC}"
        kill $pid
        sleep 2
        if lsof -ti:$port >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Force killing $service_name...${NC}"
            kill -9 $pid
        fi
        echo -e "${GREEN}✅ $service_name stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  $service_name was not running on port $port${NC}"
    fi
}

# Stop services by PID files (if they exist)
echo -e "${BLUE}📋 Stopping services by PID files...${NC}"
stop_service_by_pid "Users Service" "logs/users_service.pid"
stop_service_by_pid "Photos Service" "logs/photos_service.pid"
stop_service_by_pid "Scheduler Service" "logs/scheduler_service.pid"
stop_service_by_pid "Frontend" "logs/frontend.pid"

# Stop services by port (fallback)
echo -e "\n${BLUE}📋 Stopping services by port...${NC}"
stop_service_by_port 8001 "Users Service"
stop_service_by_port 8002 "Photos Service"
stop_service_by_port 8003 "Scheduler Service"
stop_service_by_port 8081 "Frontend (Metro)"

# Stop Docker services
echo -e "\n${BLUE}🐳 Stopping Docker services...${NC}"
cd backend
docker-compose down
echo -e "${GREEN}✅ Docker services stopped${NC}"

# Clean up any remaining processes
echo -e "\n${BLUE}🧹 Cleaning up remaining processes...${NC}"

# Kill any remaining uvicorn processes
pkill -f "uvicorn.*app.main:app" 2>/dev/null && echo -e "${GREEN}✅ Remaining uvicorn processes stopped${NC}" || echo -e "${YELLOW}⚠️  No remaining uvicorn processes${NC}"

# Kill any remaining npm processes
pkill -f "npm start" 2>/dev/null && echo -e "${GREEN}✅ Remaining npm processes stopped${NC}" || echo -e "${YELLOW}⚠️  No remaining npm processes${NC}"

# Final status check
echo -e "\n${BLUE}🔍 Final Status Check...${NC}"
echo "========================"

services=("8001:Users Service" "8002:Photos Service" "8003:Scheduler Service" "8081:Frontend")

all_stopped=true
for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${RED}❌ $name (Port $port) - Still running${NC}"
        all_stopped=false
    else
        echo -e "${GREEN}✅ $name (Port $port) - Stopped${NC}"
    fi
done

echo ""
if [ "$all_stopped" = true ]; then
    echo -e "${GREEN}🎉 All services stopped successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some services may still be running. Check manually if needed.${NC}"
fi

echo -e "\n${BLUE}💡 To start all services again, run: ./start_all_services.sh${NC}"

