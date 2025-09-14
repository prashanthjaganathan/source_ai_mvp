#!/bin/bash

# Deployment script for Source AI MVP
# This script handles building and deploying all services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="source_ai_mvp"
ENVIRONMENT=${ENVIRONMENT:-"development"}
BUILD_TAG=${BUILD_TAG:-$(date +%Y%m%d_%H%M%S)}

echo -e "${BLUE}🚀 Starting deployment for ${PROJECT_NAME}${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Build Tag: ${BUILD_TAG}${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build images
print_status "Building Docker images..."
docker-compose build --no-cache

# Run database migrations
print_status "Running database migrations..."
docker-compose up -d postgres

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 10

# Check database connection
until docker-compose exec -T postgres pg_isready -U user -d source_ai_mvp; do
    print_warning "Waiting for database..."
    sleep 2
done

print_status "Database is ready!"

# Start all services
print_status "Starting all services..."
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 15

# Health checks
print_status "Running health checks..."

# Check users service
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_status "Users service is healthy"
else
    print_error "Users service health check failed"
    docker-compose logs users_service
    exit 1
fi

# Check photos service
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    print_status "Photos service is healthy"
else
    print_error "Photos service health check failed"
    docker-compose logs photos_service
    exit 1
fi

# Check nginx
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_status "Nginx proxy is healthy"
else
    print_warning "Nginx proxy health check failed (this is optional)"
fi

# Show running containers
print_status "Deployment completed successfully!"
echo -e "${BLUE}📊 Running containers:${NC}"
docker-compose ps

echo -e "${BLUE}🌐 Service URLs:${NC}"
echo -e "  Users Service:    http://localhost:8001"
echo -e "  Photos Service:   http://localhost:8002"
echo -e "  API Gateway:      http://localhost"
echo -e "  Database:         localhost:5432"
echo -e "  Redis:            localhost:6379"

echo -e "${BLUE}📚 API Documentation:${NC}"
echo -e "  Users API Docs:   http://localhost:8001/docs"
echo -e "  Photos API Docs:  http://localhost:8002/docs"

# Clean up old images (optional)
if [ "$CLEANUP" = "true" ]; then
    print_status "Cleaning up old Docker images..."
    docker image prune -f
fi

print_status "Deployment completed! 🎉"
