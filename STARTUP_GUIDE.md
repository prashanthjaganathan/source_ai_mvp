# 🚀 Source AI MVP - Complete Startup Guide

This guide will help you start and run the entire Source AI MVP system with S3 photo storage integration.

## 📋 Prerequisites

- **Docker** (for PostgreSQL and Redis)
- **Python 3.11+** (for backend services)
- **Node.js 18+** (for frontend)
- **AWS Account** (for S3 photo storage)
- **Mac Camera** (for photo capture)

## 🔧 Environment Setup

### 1. AWS Credentials
Make sure your `.env` file contains valid AWS credentials:

```bash
# S3 Configuration
USE_S3_STORAGE=true
S3_BUCKET_NAME=source-ai-photos
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/source_ai_mvp
ENVIRONMENT=development
```

### 2. Install Dependencies

```bash
# Backend dependencies
cd backend/services/users && pip install -r requirements.txt
cd ../photos && pip install -r requirements.txt
cd ../scheduler && pip install -r requirements.txt

# Frontend dependencies
cd ../../frontend && npm install
```

## 🚀 Quick Start (Recommended)

### Option 1: Automated Startup Script

```bash
# Start all services
./start_all_services.sh

# Stop all services
./stop_all_services.sh
```

### Option 2: Manual Startup

#### Step 1: Start Database Services
```bash
cd backend
docker-compose up -d postgres redis
```

#### Step 2: Start Backend Services

**Users Service (Port 8001):**
```bash
cd services/users
set -a && source ../../../.env && set +a
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Photos Service (Port 8002):**
```bash
cd services/photos
set -a && source ../../../.env && set +a
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Scheduler Service (Port 8003):**
```bash
cd services/scheduler
set -a && source ../../../.env && set +a
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

#### Step 3: Start Frontend
```bash
cd frontend
npm start
```

## 🔍 Service Verification

### Health Checks
```bash
# Check all services
curl http://localhost:8001/health  # Users Service
curl http://localhost:8002/health  # Photos Service
curl http://localhost:8003/health  # Scheduler Service
```

### Expected Responses
- **Users Service**: `{"status":"healthy","service":"users","version":"1.0.0"}`
- **Photos Service**: `{"status":"healthy","service":"photos","version":"1.0.0"}`
- **Scheduler Service**: `{"status":"healthy","service":"scheduler","version":"1.0.0","scheduler_running":true}`

## 📱 Frontend Access

### React Native (Mobile)
- **Metro Bundler**: http://localhost:8081
- **Expo Dev Tools**: http://localhost:19002
- **iOS Simulator**: Press `i` in Metro terminal
- **Android Emulator**: Press `a` in Metro terminal

### Streamlit App (Web)
```bash
cd streamlit-app
pip install -r requirements.txt
streamlit run app.py
```

## 🧪 Testing the System

### 1. Create a User
```bash
curl -X POST "http://localhost:8001/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "age": 25,
    "gender": "other"
  }'
```

### 2. Create a Schedule
```bash
curl -X POST "http://localhost:8003/scheduler/schedules/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id-here",
    "frequency_hours": 1,
    "notifications_enabled": true,
    "silent_mode_enabled": false
  }'
```

### 3. Capture a Photo
```bash
curl -X POST "http://localhost:8003/capture/capture" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-user-id-here"}'
```

### 4. View Captured Photos
```bash
curl http://localhost:8003/capture/photos/your-user-id-here
```

## 📊 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Users API | http://localhost:8001 | User management |
| Photos API | http://localhost:8002 | Photo management |
| Scheduler API | http://localhost:8003 | Photo capture scheduling |
| Frontend | http://localhost:8081 | React Native Metro |
| Streamlit | http://localhost:8501 | Web dashboard |

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -ti:8001

# Kill process
kill $(lsof -ti:8001)
```

#### 2. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart database
docker-compose restart postgres
```

#### 3. S3 Connection Issues
```bash
# Test S3 configuration
cd backend/services/scheduler
python test_s3_config.py
```

#### 4. Mac Camera Permission Issues
- Go to System Preferences > Security & Privacy > Camera
- Allow Terminal/Python to access camera

### Logs
- **Service Logs**: Check `logs/` directory
- **Docker Logs**: `docker-compose logs`
- **Frontend Logs**: Check Metro bundler terminal

## 🛑 Stopping Services

### Automated Stop
```bash
./stop_all_services.sh
```

### Manual Stop
```bash
# Stop backend services
pkill -f "uvicorn.*app.main:app"

# Stop frontend
pkill -f "npm start"

# Stop Docker services
cd backend && docker-compose down
```

## 📁 Project Structure

```
source_ai_mvp/
├── backend/
│   ├── services/
│   │   ├── users/          # User management service
│   │   ├── photos/         # Photo management service
│   │   └── scheduler/      # Photo capture scheduler (with S3)
│   └── docker-compose.yml  # Database services
├── frontend/               # React Native mobile app
├── streamlit-app/          # Web dashboard
├── logs/                   # Service logs
├── start_all_services.sh   # Automated startup
├── stop_all_services.sh    # Automated shutdown
└── .env                    # Environment variables
```

## 🎯 Key Features

- ✅ **S3 Photo Storage**: Photos automatically uploaded to AWS S3
- ✅ **Mac Camera Integration**: Real camera capture on Mac
- ✅ **Scheduled Photo Capture**: Automated photo capture at intervals
- ✅ **User Management**: Complete user CRUD operations
- ✅ **Mobile App**: React Native frontend
- ✅ **Web Dashboard**: Streamlit web interface
- ✅ **Health Monitoring**: Service health checks
- ✅ **Logging**: Comprehensive logging system

## 🚀 Next Steps

1. **Test the complete flow**: Create user → Create schedule → Capture photo → View in S3
2. **Customize schedules**: Adjust frequency, notifications, silent mode
3. **Monitor logs**: Check service logs for any issues
4. **Scale up**: Add more users and schedules
5. **Deploy**: Consider deploying to cloud infrastructure

---

**Need help?** Check the logs in the `logs/` directory or run the health checks to diagnose issues.
