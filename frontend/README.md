# Frontend - Source AI MVP

React frontend application for the Source AI MVP project.

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)

## Project Structure

```
src/
├── assets/
│   └── styles/
│       └── main.css          # Global styles
├── components/
│   ├── Header.js             # Navigation header
│   ├── UserDashboard.js      # User dashboard component
│   └── PhotoGallery.js       # Photo gallery component
├── pages/
│   ├── Home.js               # Home page
│   └── Profile.js            # User profile page
├── services/
│   └── api.js                # API service layer
├── App.js                    # Main app component
├── index.js                  # App entry point
└── index.css                 # Base styles
```

## API Integration

The frontend communicates with backend services through the `services/api.js` module. Update the base URL in this file to match your backend service endpoints.

## Development

- Components are organized by feature and reusability
- Pages represent full-page views
- Services handle all external API calls
- Styles are organized in the assets directory

## Building for Production

```bash
npm run build
```

This builds the app for production to the `build` folder. It correctly bundles React in production mode and optimizes the build for the best performance.
