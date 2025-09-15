# Backend-Database Sync Changes

This document summarizes the changes made to sync the backend models with the database schema.

## Overview

The backend services were using different database configurations and had models that didn't match the actual database schema. This has been fixed with both **Path A** (backend model updates) and **Path B** (minimal migration).

## Changes Made

### 1. Database Configuration Fix
- **File**: `backend/services/users/app/config/database.py`
- **Change**: Updated users service to use PostgreSQL instead of SQLite
- **Before**: `sqlite:///./test_users.db`
- **After**: `postgresql://user:password@localhost:5432/source_ai_mvp`

### 2. User Model Updates
- **File**: `backend/services/users/app/models/user.py`
- **Added**:
  - `uid` (UUID field) - matches database schema
  - `incentives_earned`, `incentives_redeemed`, `incentives_available` - financial tracking
- **Removed**:
  - `bio`, `profile_picture_url` - not in database
  - `capture_frequency_hours`, `notifications_enabled`, `silent_mode_enabled`, `max_daily_captures` - handled by scheduler service
  - `total_earnings`, `total_photos_captured`, `streak_days`, `last_capture_date` - not in database
  - `is_active`, `is_verified`, `last_login` - not in database
- **Added**: Computed property `total_earnings` for backward compatibility

### 3. Photo Model Updates
- **File**: `backend/services/photos/app/models/photo.py`
- **Added**:
  - `uid` (UUID field) - matches database schema
- **Changed**:
  - `file_path` → `original_key` - matches database schema
- **Added**: Backward-compat property `file_path` that returns `original_key`

### 4. Schema Updates
- **Files**: 
  - `backend/services/users/app/api/schemas/user.py`
  - `backend/services/photos/app/api/schemas/photo.py`
- **Changes**: Updated Pydantic schemas to match new model fields
- **Added**: UUID imports and fields
- **Updated**: Field names to match database schema

### 5. CRUD Code Updates
- **Files**:
  - `backend/services/photos/app/crud/photo_crud.py`
  - `backend/services/photos/app/api/endpoints/photo_routes.py`
  - `backend/services/users/app/crud/user_crud.py`
  - `backend/services/users/app/api/endpoints/user_routes.py`
- **Changes**: Updated function parameters and field references to use new field names

### 6. Alembic Migration
- **Files**:
  - `backend/alembic.ini` - configured for PostgreSQL
  - `backend/alembic/env.py` - updated to import models
  - `backend/alembic/versions/9a63515141f6_ensure_uid_on_users_original_key_on_.py` - migration script
- **Migration Features**:
  - Idempotent (safe to run multiple times)
  - Adds `uid` to users table if missing
  - Adds `uid` to photos table if missing
  - Renames `file_path` to `original_key` in photos table if needed
  - Creates necessary indexes

## How to Apply Changes

### Option 1: Path A Only (No Migration)
If your database already has the correct schema:
```bash
# Just restart your services - the backend models now match the DB
```

### Option 2: Path B (With Migration)
If you need to update the database:
```bash
cd backend
alembic upgrade head
```

### Verify Changes
Run the sanity check script:
```bash
cd backend
python check_sync.py
```

## Expected Results

After applying changes, you should see:
- ✅ Missing user UIDs: 0
- ✅ Missing photo UIDs: 0  
- ✅ Missing original_key: 0
- All backend models match database schema
- Services can read/write data without errors

## Backward Compatibility

- User model has `total_earnings` property that returns `incentives_earned`
- Photo model has `file_path` property that returns `original_key`
- This allows existing code to continue working while transitioning to new field names

## Next Steps

1. **Test the changes** with your existing data
2. **Update any remaining code** that references old field names
3. **Consider adding the missing fields** (face detection, consent, etc.) in a future migration
4. **Add scheduler service tables** to the main database when ready

## Files Modified

```
backend/
├── alembic.ini
├── alembic/env.py
├── alembic/versions/9a63515141f6_ensure_uid_on_users_original_key_on_.py
├── check_sync.py
├── services/
│   ├── users/
│   │   ├── app/
│   │   │   ├── config/database.py
│   │   │   ├── models/user.py
│   │   │   ├── api/schemas/user.py
│   │   │   ├── crud/user_crud.py
│   │   │   └── api/endpoints/user_routes.py
│   └── photos/
│       ├── app/
│       │   ├── models/photo.py
│       │   ├── api/schemas/photo.py
│       │   ├── crud/photo_crud.py
│       │   └── api/endpoints/photo_routes.py
└── SYNC_CHANGES.md
```

## Database Schema Alignment

The backend models now exactly match the database schema defined in:
- `db/schemas/users.json`
- `db/schemas/photos.json`
- `db/migrations/20231027_initial_schema.sql`

This ensures no more sync issues between backend and database.
