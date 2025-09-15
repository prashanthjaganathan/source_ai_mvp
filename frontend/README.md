# Source AI Mobile App

A React Native mobile application for the Source AI MVP platform that allows users to capture, manage, and schedule photos with automated earning opportunities.

## Features

### 🔐 Authentication
- User registration and login
- Secure token-based authentication
- Profile management

### 📸 Photo Management
- Photo gallery with grid view
- Photo upload and capture
- Photo metadata management
- Delete photos functionality

### ⏰ Scheduling
- Create and manage photo capture schedules
- Set capture frequency (hourly, daily, etc.)
- Enable/disable notifications
- Silent mode for capture
- Pause/resume schedules

### 📊 Dashboard
- User statistics and earnings
- Recent photos overview
- Quick capture action
- Real-time data refresh

### ⚙️ Settings
- Notification preferences
- Capture settings
- App preferences
- Privacy and security options

## Tech Stack

- **React Native** - Mobile app framework
- **TypeScript** - Type safety
- **React Navigation** - Navigation library
- **React Native Vector Icons** - Icon library
- **AsyncStorage** - Local data persistence
- **Axios** - HTTP client for API calls
- **React Native Image Picker** - Camera and photo selection
- **React Native Push Notifications** - Push notifications

## Backend Integration

The app integrates with three microservices:

1. **Users Service** (Port 8001)
   - Authentication endpoints
   - User profile management
   - User settings and statistics

2. **Photos Service** (Port 8002)
   - Photo upload and management
   - Photo gallery endpoints
   - Photo metadata operations

3. **Scheduler Service** (Port 8003)
   - Schedule management
   - Photo capture automation
   - Notification handling

## Project Structure

```
src/
├── components/          # Reusable UI components
├── context/            # React Context providers
│   └── AuthContext.tsx # Authentication state management
├── navigation/         # Navigation configuration
│   └── AppNavigator.tsx
├── screens/           # Screen components
│   ├── auth/          # Authentication screens
│   │   ├── LoginScreen.tsx
│   │   └── RegisterScreen.tsx
│   └── main/          # Main app screens
│       ├── HomeScreen.tsx
│       ├── PhotoGalleryScreen.tsx
│       ├── ScheduleScreen.tsx
│       ├── ProfileScreen.tsx
│       └── SettingsScreen.tsx
└── services/          # API services
    └── api.ts         # API client and service classes
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- React Native CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

### Installation

1. Install dependencies:
```bash
npm install
```

2. For iOS, install CocoaPods dependencies:
```bash
cd ios && pod install && cd ..
```

3. Start the Metro bundler:
```bash
npm start
```

4. Run on iOS:
```bash
npm run ios
```

5. Run on Android:
```bash
npm run android
```

## API Configuration

Update the API base URLs in `src/services/api.ts` to match your backend services:

```typescript
const API_BASE_URLS = {
  users: 'http://localhost:8001',
  photos: 'http://localhost:8002', 
  scheduler: 'http://localhost:8003',
};
```

For production, replace `localhost` with your actual server URLs.

## Key Features Implementation

### Authentication Flow
- JWT token-based authentication
- Automatic token refresh
- Secure token storage using AsyncStorage
- Protected routes and navigation

### Photo Management
- Grid-based photo gallery
- Image modal with full-screen view
- Photo upload with progress indication
- Photo deletion with confirmation

### Scheduling System
- Create/edit/delete schedules
- Toggle schedule active/inactive
- Frequency configuration
- Notification and silent mode settings

### Real-time Updates
- Pull-to-refresh functionality
- Automatic data synchronization
- Loading states and error handling

## Development Notes

- The app uses TypeScript for type safety
- All API calls are centralized in the services layer
- Context API is used for global state management
- Material Design icons are used throughout the app
- Responsive design for different screen sizes

## Future Enhancements

- Push notifications for scheduled captures
- Offline photo storage and sync
- Advanced photo editing features
- Social sharing capabilities
- Analytics and insights dashboard
- Multi-language support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Source AI MVP platform.