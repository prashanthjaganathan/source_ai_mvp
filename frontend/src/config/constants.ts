// API Configuration
export const API_CONFIG = {
  BASE_URLS: {
    USERS: 'http://localhost:8001',
    PHOTOS: 'http://localhost:8002',
    SCHEDULER: 'http://localhost:8003',
  },
  TIMEOUT: 10000,
};

// App Configuration
export const APP_CONFIG = {
  NAME: 'Source AI',
  VERSION: '1.0.0',
  SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/jpg'],
  MAX_IMAGE_SIZE: 10 * 1024 * 1024, // 10MB
  DEFAULT_PHOTO_LIMIT: 20,
  DEFAULT_SCHEDULE_FREQUENCY: 24, // hours
};

// Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  SETTINGS: 'app_settings',
};

// Colors
export const COLORS = {
  PRIMARY: '#007AFF',
  SECONDARY: '#34C759',
  DANGER: '#ff3b30',
  WARNING: '#FF9500',
  INFO: '#5AC8FA',
  SUCCESS: '#34C759',
  LIGHT: '#f8f9fa',
  DARK: '#333333',
  GRAY: '#666666',
  LIGHT_GRAY: '#cccccc',
  WHITE: '#ffffff',
  BLACK: '#000000',
};

// Font Sizes
export const FONT_SIZES = {
  SMALL: 12,
  MEDIUM: 14,
  LARGE: 16,
  XLARGE: 18,
  XXLARGE: 20,
  TITLE: 24,
  HEADER: 32,
};

// Spacing
export const SPACING = {
  XS: 4,
  SM: 8,
  MD: 12,
  LG: 16,
  XL: 20,
  XXL: 24,
  XXXL: 32,
};
