# Backend - Source AI MVP

Microservices backend architecture for the Source AI MVP project.

## Architecture Overview

The backend follows a microservices architecture with the following services:

- **Users Service** (Port 8001): User management, authentication, and profiles
- **Photos Service** (Port 8002): Photo upload, storage, and metadata management
- **Database**: PostgreSQL for persistent storage
- **Redis**: Caching and session management (optional)
- **Nginx**: Reverse proxy and API gateway

## Services

### Users Service
- **Port**: 8001
- **Technology**: FastAPI + SQLAlchemy
- **Features**:
  - User registration and authentication
  - Profile management
  - User CRUD operations
  - Password hashing with bcrypt

### Photos Service
- **Port**: 8002
- **Technology**: FastAPI + SQLAlchemy + Pillow
- **Features**:
  - Photo upload and storage
  - Image processing and metadata extraction
  - Photo gallery management
  - File size and type validation

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL 12+ (if running without Docker)

### Using Docker (Recommended)

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Check service health**:
   ```bash
   curl http://localhost:8001/health  # Users service
   curl http://localhost:8002/health  # Photos service
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f users_service
   docker-compose logs -f photos_service
   ```

### Local Development

1. **Set up database**:
   ```bash
   # Start PostgreSQL
   docker-compose up -d postgres
   
   # Run migrations
   psql -h localhost -U user -d source_ai_mvp -f ../db/migrations/20231027_initial_schema.sql
   ```

2. **Start individual services**:
   ```bash
   # Users service
   cd services/users
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   
   # Photos service
   cd services/photos
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
   ```

## API Documentation

Once services are running, access the interactive API documentation:

- **Users Service**: http://localhost:8001/docs
- **Photos Service**: http://localhost:8002/docs
- **API Gateway**: http://localhost (via Nginx)

## Testing

### Run All Tests
```bash
./scripts/run_tests.sh
```

### Run Tests for Specific Service
```bash
cd services/users
python -m pytest tests/ -v
```

### Run Integration Tests
```bash
# Start services
docker-compose up -d

# Run tests
pytest tests/integration/ -v
```

## Deployment

### Development Deployment
```bash
./scripts/deploy.sh
```

### Production Deployment
```bash
ENVIRONMENT=production ./scripts/deploy.sh
```

## Configuration

### Environment Variables

**Database**:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/source_ai_mvp
```

**Service Configuration**:
```bash
ENVIRONMENT=development  # or production
```

**Photos Service**:
```bash
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif
```

## Database Management

### Migrations
Database schema changes are managed through migration files in `../db/migrations/`.

### Backup
```bash
# Backup database
docker-compose exec postgres pg_dump -U user source_ai_mvp > backup.sql

# Restore database
docker-compose exec -T postgres psql -U user source_ai_mvp < backup.sql
```

## Monitoring and Logging

### Health Checks
All services expose health check endpoints:
- `GET /health` - Returns service status and version

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f users_service
docker-compose logs -f photos_service
```

## Development Guidelines

### Adding a New Service

1. Create service directory in `services/`
2. Add `Dockerfile`, `requirements.txt`, and application code
3. Update `docker-compose.yml` with new service
4. Add health check endpoint
5. Update nginx configuration if needed

### Code Structure

Each service follows this structure:
```
service_name/
├── app/
│   ├── main.py           # FastAPI application
│   ├── api/
│   │   ├── endpoints/    # API route handlers
│   │   └── schemas/      # Pydantic models
│   ├── crud/             # Database operations
│   ├── models/           # SQLAlchemy models
│   └── config/           # Configuration
├── tests/                # Test files
├── Dockerfile
└── requirements.txt
```

### API Design

- Use RESTful conventions
- Include proper HTTP status codes
- Implement pagination for list endpoints
- Add request/response validation with Pydantic
- Include comprehensive error handling

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8001, 8002, 5432, 6379 are available
2. **Database connection**: Check DATABASE_URL and ensure PostgreSQL is running
3. **File permissions**: Ensure upload directories are writable
4. **Memory issues**: Increase Docker memory allocation if needed

### Debug Mode

Enable debug logging:
```bash
ENVIRONMENT=development docker-compose up
```

### Service Dependencies

Services have the following dependencies:
- Users Service → PostgreSQL
- Photos Service → PostgreSQL + File System
- All Services → Redis (optional)

## Contributing

1. Follow the established code structure
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass before submitting PR
5. Use conventional commit messages
