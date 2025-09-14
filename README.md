# Source AI MVP

A full-stack application with microservices architecture, featuring a modern React frontend and FastAPI backend services.

## Project Structure

```
├── frontend/          # React frontend application
├── backend/           # Microservices backend (FastAPI)
│   ├── services/      # Individual microservices
│   │   ├── users/     # User management service
│   │   └── photos/    # Photo handling service
│   ├── config/        # Shared configuration
│   └── scripts/       # Deployment and utility scripts
├── db/                # Database schemas and migrations
└── README.md          # This file
```

## Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.9+
- Docker & Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd source_ai_mvp
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Or run services individually:**

   **Backend Services:**
   ```bash
   cd backend/services/users
   pip install -r requirements.txt
   python -m app.main
   
   cd ../photos
   pip install -r requirements.txt
   python -m app.main
   ```

   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Service Endpoints

- **Frontend**: http://localhost:3000
- **Users Service**: http://localhost:8001
- **Photos Service**: http://localhost:8002
- **Database**: localhost:5432

## Development Workflow

### For Frontend Developers
- Work in the `frontend/` directory
- Use `npm start` for development server
- Components go in `src/components/`
- Pages go in `src/pages/`
- API calls use `src/services/api.js`

### For Backend Developers
- Each service is independent in `backend/services/`
- Add new services by creating a new directory
- Each service has its own `requirements.txt` and `Dockerfile`
- Use `backend/config/settings.py` for shared configuration

### For Database Changes
- Update schemas in `db/schemas/`
- Add migrations in `db/migrations/`
- Coordinate with backend teams for model changes

## Testing

```bash
# Run all tests
./backend/scripts/run_tests.sh

# Frontend tests
cd frontend && npm test

# Individual service tests
cd backend/services/users && python -m pytest
cd backend/services/photos && python -m pytest
```

## Deployment

```bash
# Build and deploy all services
./backend/scripts/deploy.sh
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `./backend/scripts/run_tests.sh`
4. Commit changes: `git commit -m "Add your feature"`
5. Push to branch: `git push origin feature/your-feature`
6. Create a Pull Request

## Architecture Overview

- **Frontend**: React SPA with modern UI components
- **Backend**: Microservices architecture with FastAPI
- **Database**: PostgreSQL with defined schemas
- **Containerization**: Docker for consistent environments
- **API**: RESTful APIs with OpenAPI documentation

## Team Collaboration

- Each service can be developed independently
- Shared database schemas ensure consistency
- Docker Compose enables local full-stack development
- Clear separation of concerns for parallel development