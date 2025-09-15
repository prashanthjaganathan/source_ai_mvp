# Source AI Streamlit Dashboard

A simple, clean Streamlit interface for the Source AI platform that provides easy access to all features without complex setup.

## 🚀 Quick Start

1. **Start the Streamlit app:**
   ```bash
   cd streamlit-app
   streamlit run app.py
   ```

2. **Open your browser** to: http://localhost:8501

3. **Register/Login** and start using the platform!

## ✨ Features

### 🔐 Authentication
- User registration and login
- Secure session management
- User profile display

### 📊 Dashboard
- Real-time statistics display
- Photo count, earnings, and schedule metrics
- Quick action buttons

### 📷 Photo Gallery
- View all captured photos
- Photo metadata display
- Grid layout for easy browsing

### ⏰ Schedule Management
- Create new photo capture schedules
- View existing schedules
- Schedule status and statistics
- Frequency configuration

### ⚙️ Settings & Status
- System health monitoring
- App information
- Data refresh options

## 🎯 Key Benefits

- **Simple Setup** - No complex dependencies or configuration
- **Clean Interface** - Easy to use and navigate
- **Real-time Data** - Live updates from your backend services
- **Mobile Friendly** - Responsive design works on all devices
- **No Installation** - Runs directly in your browser

## 🔧 Backend Requirements

Make sure your backend services are running:

```bash
# Users Service (Port 8001)
cd backend/services/users
python -m uvicorn app.main:app --port 8001 --reload

# Photos Service (Port 8002)
cd backend/services/photos
python -m uvicorn app.main:app --port 8002 --reload

# Scheduler Service (Port 8003)
cd backend/services/scheduler
python -m uvicorn app.main:app --port 8003 --reload
```

## 📱 Usage

1. **Register** a new account or **login** with existing credentials
2. **View your dashboard** with statistics and quick actions
3. **Create schedules** for automatic photo capture
4. **Browse your photo gallery** to see captured images
5. **Monitor system status** and manage settings

## 🛠️ Customization

The Streamlit app is easily customizable:

- **Colors & Styling**: Modify the Streamlit theme in `app.py`
- **API Endpoints**: Update `API_BASE_URLS` for different backend locations
- **Features**: Add new tabs or sections as needed
- **Layout**: Adjust column layouts and page structure

## 🔍 Troubleshooting

- **Connection Errors**: Ensure all backend services are running
- **Authentication Issues**: Check user credentials and backend connectivity
- **Display Issues**: Refresh the browser or restart the Streamlit app

## 📈 Next Steps

- Add photo upload functionality
- Implement real-time notifications
- Add more detailed analytics
- Create export features for data

This Streamlit interface provides a simple, effective way to interact with your Source AI platform without the complexity of mobile app development!
