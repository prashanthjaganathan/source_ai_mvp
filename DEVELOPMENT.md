# Development Guide - Source AI MVP

This guide provides detailed information for developers working on the Source AI MVP project.

## 🎉 Current Status: Backend-Database Sync Complete

**✅ SYNC STATUS**: Backend models and database schema are now perfectly synchronized!

### What Was Fixed:
- **Database Configuration**: All services now use PostgreSQL consistently
- **User Model**: Updated to match database schema with `uid`, `incentives_*` fields
- **Photo Model**: Updated to use `original_key` instead of `file_path`, added `uid`
- **CRUD Operations**: All field references updated to match new schema
- **Database Permissions**: Proper user permissions configured

### Verification:
```bash
cd backend
python check_sync.py
# Should show: ✅ All checks passed! Backend and database are in sync.
```

## Quick Start for New Developers

1. **Prerequisites**:
   ```bash
   # Ensure PostgreSQL is running
   brew services start postgresql
   
   # Create database and user (if not exists)
   psql -U postgres -c "CREATE USER \"user\" WITH PASSWORD 'password';"
   psql -U postgres -c "CREATE DATABASE source_ai_mvp OWNER \"user\";"
   psql -U postgres -d source_ai_mvp -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"user\";"
   ```

2. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd source_ai_mvp
   make setup
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Users API: http://localhost:8001/docs
   - Photos API: http://localhost:8002/docs
   - API Gateway: http://localhost

## Testing the Current Setup

### 1. Verify Database-Backend Sync
```bash
cd backend
python check_sync.py
```
**Expected Output**:
```
✅ Missing user UIDs: 0 (should be 0)
✅ Missing photo UIDs: 0 (should be 0)  
✅ Missing original_key: 0 (should be 0)
✅ All checks passed! Backend and database are in sync.
```

### 2. Test Backend Services
```bash
# Test Users Service
cd backend/services/users
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
curl http://localhost:8001/health

# Test Photos Service  
cd backend/services/photos
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 &
curl http://localhost:8002/health
```

### 3. Test API Endpoints
```bash
# Test Users API
curl http://localhost:8001/docs  # Should show Swagger UI
curl http://localhost:8001/users/  # Should return user list

# Test Photos API
curl http://localhost:8002/docs  # Should show Swagger UI
curl http://localhost:8002/photos/  # Should return photo list
```

### 4. Test Database Operations
```bash
# Connect to database
psql -U user -d source_ai_mvp

# Check tables
\dt

# Check sample data
SELECT id, uid, name, email, incentives_earned FROM users LIMIT 3;
SELECT id, uid, filename, original_key, user_id FROM photos LIMIT 3;
```

### 5. Run Comprehensive Test
```bash
# Run the automated test script
python test_app.py
```
**Expected Output**:
```
✅ Database-backend sync: PASSED
✅ users health: PASSED
✅ photos health: PASSED
✅ users docs: PASSED
✅ users API: PASSED - 5 items returned
✅ photos docs: PASSED
✅ photos API: PASSED - 5 items returned
🎉 ALL TESTS PASSED! Your app is working correctly.
```

**Status**: ✅ **ALL TESTS PASSING** - The app is fully functional!

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

## Recent Changes & Migration Notes

### Backend-Database Sync (Completed)
- **Date**: September 14, 2025
- **Status**: ✅ Complete
- **Changes**: See `SYNC_CHANGES.md` for detailed documentation

### Key Model Changes:
- **User Model**: Now uses `incentives_earned/redeemed/available` instead of `total_earnings`
- **Photo Model**: Now uses `original_key` instead of `file_path`
- **UUID Fields**: Both models now have `uid` fields for external references
- **Backward Compatibility**: Properties added for smooth transition

### Migration Status:
- **Database**: Already has correct schema (no migration needed)
- **Backend**: Updated to match database schema
- **Services**: All CRUD operations updated

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 3000, 8001, 8002, 5432 are available
2. **Database Connection**: Check DATABASE_URL and PostgreSQL status
3. **File Permissions**: Ensure upload directories are writable
4. **Memory Issues**: Increase Docker memory allocation

### Sync-Related Issues

1. **Import Errors**: If you see import errors, ensure all services use the same database
   ```bash
   # Check database configuration
   grep -r "DATABASE_URL" backend/services/*/app/config/
   ```

2. **Field Not Found**: If you see field errors, check the model definitions
   ```bash
   # Verify model fields match database
   python check_sync.py
   ```

3. **Permission Errors**: If database operations fail
   ```bash
   # Grant proper permissions
   psql -U postgres -d source_ai_mvp -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"user\";"
   ```

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
