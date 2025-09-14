#!/bin/bash

# Test runner script for Source AI MVP
# This script runs tests for all backend services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES_DIR="$PROJECT_ROOT/services"

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_path="$SERVICES_DIR/$service_name"
    
    if [ ! -d "$service_path" ]; then
        print_error "Service directory not found: $service_path"
        return 1
    fi
    
    print_info "Running tests for $service_name service..."
    
    # Check if tests directory exists
    if [ ! -d "$service_path/tests" ]; then
        print_warning "No tests directory found for $service_name service"
        return 0
    fi
    
    # Change to service directory
    cd "$service_path"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found for $service_name service"
        return 1
    fi
    
    # Install dependencies if virtual environment doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment for $service_name..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    print_info "Installing dependencies for $service_name..."
    pip install -q -r requirements.txt
    
    # Run tests
    print_info "Running pytest for $service_name..."
    if python -m pytest tests/ -v --tb=short; then
        print_status "Tests passed for $service_name service"
    else
        print_error "Tests failed for $service_name service"
        return 1
    fi
    
    # Deactivate virtual environment
    deactivate
    
    return 0
}

# Function to run integration tests
run_integration_tests() {
    print_info "Running integration tests..."
    
    # Start services with Docker Compose for integration testing
    cd "$PROJECT_ROOT"
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found"
        return 1
    fi
    
    # Start services
    print_info "Starting services for integration tests..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    sleep 10
    
    # Run integration tests (you can add specific integration test commands here)
    print_info "Running basic integration tests..."
    
    # Test database connection
    if docker-compose exec -T postgres pg_isready -U user -d source_ai_mvp; then
        print_status "Database connection test passed"
    else
        print_error "Database connection test failed"
        return 1
    fi
    
    # Test Redis connection
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        print_status "Redis connection test passed"
    else
        print_error "Redis connection test failed"
        return 1
    fi
    
    # Stop services
    docker-compose down
    
    return 0
}

# Main execution
echo -e "${BLUE}🧪 Running tests for Source AI MVP${NC}"
echo -e "${BLUE}Project Root: $PROJECT_ROOT${NC}"

# Check if we're in the right directory
if [ ! -d "$SERVICES_DIR" ]; then
    print_error "Services directory not found. Please run this script from the backend directory."
    exit 1
fi

# Get list of services
services=($(ls -d $SERVICES_DIR/*/ | xargs -n 1 basename))

if [ ${#services[@]} -eq 0 ]; then
    print_warning "No services found in $SERVICES_DIR"
    exit 0
fi

print_info "Found services: ${services[*]}"

# Run tests for each service
failed_services=()
for service in "${services[@]}"; do
    if ! run_service_tests "$service"; then
        failed_services+=("$service")
    fi
done

# Run integration tests
if ! run_integration_tests; then
    print_error "Integration tests failed"
    exit 1
fi

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
if [ ${#failed_services[@]} -eq 0 ]; then
    print_status "All tests passed! 🎉"
    exit 0
else
    print_error "Tests failed for the following services: ${failed_services[*]}"
    exit 1
fi
