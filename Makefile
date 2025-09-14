# Makefile for Source AI MVP
# Provides convenient commands for development and deployment

.PHONY: help install start stop restart build test clean logs deploy

# Default target
help: ## Show this help message
	@echo "Source AI MVP - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install all dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing backend dependencies..."
	cd backend/services/users && pip install -r requirements.txt
	cd backend/services/photos && pip install -r requirements.txt

# Development
start: ## Start all services with Docker Compose
	@echo "Starting all services..."
	cd backend && docker-compose up -d
	@echo "Starting frontend development server..."
	cd frontend && npm start &

start-backend: ## Start only backend services
	@echo "Starting backend services..."
	cd backend && docker-compose up -d

start-frontend: ## Start only frontend development server
	@echo "Starting frontend development server..."
	cd frontend && npm start

start-dev: ## Start services in development mode with logs
	@echo "Starting services in development mode..."
	cd backend && docker-compose up

# Service management
stop: ## Stop all services
	@echo "Stopping all services..."
	cd backend && docker-compose down

restart: ## Restart all services
	@echo "Restarting all services..."
	cd backend && docker-compose restart

# Building
build: ## Build all Docker images
	@echo "Building Docker images..."
	cd backend && docker-compose build

build-no-cache: ## Build all Docker images without cache
	@echo "Building Docker images without cache..."
	cd backend && docker-compose build --no-cache

# Testing
test: ## Run all tests
	@echo "Running all tests..."
	cd backend && ./scripts/run_tests.sh

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	cd frontend && npm test

test-backend: ## Run backend tests
	@echo "Running backend tests..."
	cd backend && ./scripts/run_tests.sh

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	cd backend && docker-compose up -d && sleep 10 && ./scripts/run_tests.sh && docker-compose down

# Database
db-setup: ## Set up database with initial data
	@echo "Setting up database..."
	cd backend && docker-compose up -d postgres
	@sleep 10
	@echo "Database is ready!"

db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	cd backend && docker-compose exec postgres psql -U user -d source_ai_mvp -f /docker-entrypoint-initdb.d/20231027_initial_schema.sql

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "Resetting database..."
	cd backend && docker-compose down -v && docker-compose up -d postgres

# Logs
logs: ## Show logs for all services
	@echo "Showing logs for all services..."
	cd backend && docker-compose logs -f

logs-users: ## Show logs for users service
	@echo "Showing logs for users service..."
	cd backend && docker-compose logs -f users_service

logs-photos: ## Show logs for photos service
	@echo "Showing logs for photos service..."
	cd backend && docker-compose logs -f photos_service

logs-db: ## Show logs for database
	@echo "Showing logs for database..."
	cd backend && docker-compose logs -f postgres

# Deployment
deploy: ## Deploy all services
	@echo "Deploying all services..."
	cd backend && ./scripts/deploy.sh

deploy-prod: ## Deploy to production
	@echo "Deploying to production..."
	cd backend && ENVIRONMENT=production ./scripts/deploy.sh

# Health checks
health: ## Check health of all services
	@echo "Checking service health..."
	@echo "Users Service:"
	@curl -s http://localhost:8001/health | jq . || echo "Users service not responding"
	@echo "Photos Service:"
	@curl -s http://localhost:8002/health | jq . || echo "Photos service not responding"
	@echo "API Gateway:"
	@curl -s http://localhost/health || echo "API Gateway not responding"

# Cleanup
clean: ## Clean up Docker containers and images
	@echo "Cleaning up Docker resources..."
	cd backend && docker-compose down -v --remove-orphans
	docker system prune -f

clean-all: ## Clean up all Docker resources (WARNING: This will remove all unused Docker resources)
	@echo "Cleaning up all Docker resources..."
	cd backend && docker-compose down -v --remove-orphans
	docker system prune -a -f

# Development utilities
shell-users: ## Open shell in users service container
	@echo "Opening shell in users service..."
	cd backend && docker-compose exec users_service /bin/bash

shell-photos: ## Open shell in photos service container
	@echo "Opening shell in photos service..."
	cd backend && docker-compose exec photos_service /bin/bash

shell-db: ## Open shell in database container
	@echo "Opening shell in database..."
	cd backend && docker-compose exec postgres psql -U user -d source_ai_mvp

# Status
status: ## Show status of all services
	@echo "Service Status:"
	cd backend && docker-compose ps

# Quick setup for new developers
setup: install db-setup build start ## Complete setup for new developers
	@echo "Setup complete! Services are starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "Users API: http://localhost:8001"
	@echo "Photos API: http://localhost:8002"
	@echo "API Gateway: http://localhost"

# Production setup
prod-setup: ## Setup for production deployment
	@echo "Setting up production environment..."
	@cp env.example .env
	@echo "Please edit .env file with production values"
	@echo "Then run: make deploy-prod"
