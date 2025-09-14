# Development Guide - Source AI MVP

This guide provides detailed information for developers working on the Source AI MVP project.

## Quick Start for New Developers

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd source_ai_mvp
   make setup
   ```

2. **Access the Application**:
   - Frontend: http://localhost:3000
   - Users API: http://localhost:8001/docs
   - Photos API: http://localhost:8002/docs
   - API Gateway: http://localhost

## Development Workflow

### Daily Development Commands

```bash
# Start all services
make start

# View logs
make logs

# Run tests
make test

# Check service health
make health

# Stop services
make stop
```

### Working on Frontend

```bash
# Start only frontend
make start-frontend

# Run frontend tests
make test-frontend

# Build for production
cd frontend && npm run build
```

### Working on Backend Services

```bash
# Start only backend
make start-backend

# Run backend tests
make test-backend

# Access service shell
make shell-users
make shell-photos
```

## Project Structure Deep Dive

### Frontend Architecture

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page-level components
│   ├── services/          # API communication layer
│   └── assets/            # Images, styles, etc.
```

**Key Components**:
- `Header.js`: Navigation and branding
- `UserDashboard.js`: User profile display
- `PhotoGallery.js`: Photo upload and display
- `api.js`: Centralized API service layer

### Backend Architecture

```
backend/
├── services/              # Microservices
│   ├── users/            # User management service
│   └── photos/           # Photo management service
├── config/               # Shared configuration
└── scripts/              # Deployment and utility scripts
```

**Service Structure**:
```
service_name/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── api/
│   │   ├── endpoints/   # Route handlers
│   │   └── schemas/     # Pydantic models
│   ├── crud/            # Database operations
│   ├── models/          # SQLAlchemy models
│   └── config/          # Service-specific config
├── tests/               # Test files
├── Dockerfile          # Container definition
└── requirements.txt    # Python dependencies
```

## API Development

### Adding New Endpoints

1. **Define Schema** (in `api/schemas/`):
   ```python
   class NewResourceCreate(BaseModel):
       name: str
       description: Optional[str] = None
   ```

2. **Create CRUD Operations** (in `crud/`):
   ```python
   def create_new_resource(db: Session, resource: NewResourceCreate):
       # Implementation
   ```

3. **Add Route Handler** (in `api/endpoints/`):
   ```python
   @router.post("/new-resources/", response_model=NewResource)
   def create_resource(resource: NewResourceCreate, db: Session = Depends(get_db)):
       return create_new_resource(db=db, resource=resource)
   ```

### API Design Guidelines

- Use RESTful conventions
- Include proper HTTP status codes
- Implement pagination for list endpoints
- Add comprehensive error handling
- Include request/response validation

### Testing APIs

```bash
# Test specific service
cd backend/services/users
python -m pytest tests/ -v

# Test with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## Database Development

### Schema Changes

1. **Update JSON Schema** (in `db/schemas/`)
2. **Create Migration** (in `db/migrations/`)
3. **Test Migration** on development database
4. **Update SQLAlchemy Models**

### Running Migrations

```bash
# Apply migrations
make db-migrate

# Reset database (development only)
make db-reset
```

### Database Access

```bash
# Access database shell
make shell-db

# View database status
docker-compose exec postgres psql -U user -d source_ai_mvp -c "\dt"
```

## Frontend Development

### Component Development

1. **Create Component** in `src/components/`
2. **Add to Page** in `src/pages/`
3. **Update Routing** in `App.js`
4. **Add API Integration** in `services/api.js`

### State Management

Currently using React's built-in state management. For complex state, consider:
- Context API for global state
- Redux Toolkit for complex state logic
- React Query for server state

### Styling

- Global styles in `src/assets/styles/main.css`
- Component-specific styles using CSS classes
- Consider CSS modules or styled-components for larger projects

## Testing Strategy

### Frontend Testing

```bash
# Run tests
cd frontend && npm test

# Run tests with coverage
cd frontend && npm test -- --coverage

# Run specific test
cd frontend && npm test -- --testNamePattern="UserDashboard"
```

### Backend Testing

```bash
# Run all tests
make test-backend

# Run specific service tests
cd backend/services/users && python -m pytest tests/ -v

# Run with coverage
cd backend/services/users && python -m pytest tests/ --cov=app --cov-report=html
```

### Integration Testing

```bash
# Run integration tests
make test-integration
```

## Debugging

### Frontend Debugging

- Use React Developer Tools browser extension
- Add `console.log` statements for debugging
- Use browser dev tools for network and performance debugging

### Backend Debugging

```bash
# View service logs
make logs-users
make logs-photos

# Access service shell
make shell-users
make shell-photos

# Enable debug mode
cd backend && ENVIRONMENT=development docker-compose up
```

### Database Debugging

```bash
# Access database
make shell-db

# View database logs
make logs-db

# Check table contents
SELECT * FROM users LIMIT 5;
SELECT * FROM photos LIMIT 5;
```

## Performance Optimization

### Frontend Optimization

- Use React.memo for expensive components
- Implement lazy loading for routes
- Optimize bundle size with code splitting
- Use image optimization for photos

### Backend Optimization

- Implement database connection pooling
- Add Redis caching for frequently accessed data
- Optimize database queries with proper indexing
- Use async/await for I/O operations

## Security Considerations

### Authentication

- Implement JWT-based authentication
- Use secure password hashing (bcrypt)
- Add rate limiting to prevent abuse
- Implement CORS properly

### Data Protection

- Validate all input data
- Sanitize file uploads
- Use HTTPS in production
- Implement proper error handling

## Deployment

### Development Deployment

```bash
# Deploy to development
make deploy
```

### Production Deployment

```bash
# Deploy to production
make deploy-prod
```

### Environment Configuration

1. Copy `env.example` to `.env`
2. Update configuration values
3. Ensure secrets are properly secured

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 3000, 8001, 8002, 5432 are available
2. **Database Connection**: Check DATABASE_URL and PostgreSQL status
3. **File Permissions**: Ensure upload directories are writable
4. **Memory Issues**: Increase Docker memory allocation

### Getting Help

1. Check service logs: `make logs`
2. Verify service health: `make health`
3. Review configuration in `.env` file
4. Check Docker container status: `make status`

## Contributing Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Add type hints in Python
- Use meaningful variable names

### Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit with descriptive message
4. Push and create pull request

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add appropriate labels
4. Request code review
5. Merge after approval

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
