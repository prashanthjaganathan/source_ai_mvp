# Database Schema and Migrations

This directory contains the database schema definitions and migration scripts for the Source AI MVP project.

## Structure

```
db/
├── schemas/          # JSON schema definitions for each table
│   ├── users.json    # User table schema
│   └── photos.json   # Photos table schema
├── migrations/       # SQL migration scripts
│   └── 20231027_initial_schema.sql
└── README.md         # This file
```

## Schema Definitions

### Users Table (`schemas/users.json`)
- **Purpose**: Store user profiles and authentication data
- **Key Fields**: id, name, email, bio, hashed_password
- **Relationships**: One-to-many with photos table

### Photos Table (`schemas/photos.json`)
- **Purpose**: Store photo metadata and file information
- **Key Fields**: id, title, description, filename, file_path, user_id
- **Relationships**: Many-to-one with users table

## Migrations

### Initial Schema (`migrations/20231027_initial_schema.sql`)
- Creates the initial database structure
- Sets up tables, indexes, and triggers
- Includes sample data for development

## Database Setup

### Prerequisites
- PostgreSQL 12+ (recommended)
- Database user with CREATE privileges

### Running Migrations

1. **Create the database**:
   ```sql
   CREATE DATABASE source_ai_mvp;
   ```

2. **Run the initial migration**:
   ```bash
   psql -d source_ai_mvp -f migrations/20231027_initial_schema.sql
   ```

3. **Verify the setup**:
   ```sql
   \dt  -- List tables
   \d users  -- Describe users table
   \d photos  -- Describe photos table
   ```

### Using Docker

If you're using Docker Compose (recommended), the database will be automatically created and migrations will be handled by the application startup.

## Environment Variables

Configure these environment variables for your database connection:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/source_ai_mvp
```

## Development Notes

- **Sample Data**: The initial migration includes sample users for development
- **Passwords**: Default password is 'password123' (change in production!)
- **File Storage**: Photos are stored in the `uploads/` directory
- **Indexes**: Proper indexes are created for common query patterns

## Production Considerations

1. **Security**: Change default passwords and remove sample data
2. **Backups**: Set up regular database backups
3. **Monitoring**: Monitor database performance and query patterns
4. **File Storage**: Consider using cloud storage (S3, etc.) for photo files
5. **Connection Pooling**: Configure appropriate connection pool sizes

## Schema Changes

When making schema changes:

1. Update the JSON schema files in `schemas/`
2. Create a new migration file in `migrations/`
3. Test the migration on a copy of production data
4. Document any breaking changes

### Migration Naming Convention
```
YYYYMMDD_description.sql
```
Example: `20231115_add_user_preferences.sql`

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure your database user has CREATE privileges
2. **Connection Refused**: Check if PostgreSQL is running and accessible
3. **Duplicate Key**: Sample data conflicts - use `ON CONFLICT DO NOTHING`

### Useful Commands

```sql
-- Check table sizes
SELECT schemaname,tablename,attname,n_distinct,correlation FROM pg_stats;

-- Check index usage
SELECT * FROM pg_stat_user_indexes;

-- Check active connections
SELECT * FROM pg_stat_activity;
```
