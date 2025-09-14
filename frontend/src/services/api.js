import axios from 'axios';

// Configure base URLs for different services
const API_BASE_URLS = {
  users: process.env.REACT_APP_USERS_API_URL || 'http://localhost:8001',
  photos: process.env.REACT_APP_PHOTOS_API_URL || 'http://localhost:8002'
};

// Create axios instances for each service
const usersApi = axios.create({
  baseURL: API_BASE_URLS.users,
  headers: {
    'Content-Type': 'application/json',
  },
});

const photosApi = axios.create({
  baseURL: API_BASE_URLS.photos,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed)
const addAuthInterceptor = (apiInstance) => {
  apiInstance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
};

// Response interceptor for handling errors
const addErrorInterceptor = (apiInstance) => {
  apiInstance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Handle unauthorized access
        localStorage.removeItem('authToken');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
};

// Apply interceptors
[usersApi, photosApi].forEach(api => {
  addAuthInterceptor(api);
  addErrorInterceptor(api);
});

// User Service API calls
export const userApi = {
  // Get user profile
  getProfile: async () => {
    const response = await usersApi.get('/users/profile');
    return response.data;
  },

  // Update user profile
  updateProfile: async (userData) => {
    const response = await usersApi.put('/users/profile', userData);
    return response.data;
  },

  // Create new user
  createUser: async (userData) => {
    const response = await usersApi.post('/users/', userData);
    return response.data;
  },

  // Get user by ID
  getUser: async (userId) => {
    const response = await usersApi.get(`/users/${userId}`);
    return response.data;
  },

  // List all users
  getUsers: async (params = {}) => {
    const response = await usersApi.get('/users/', { params });
    return response.data;
  }
};

// Photo Service API calls
export const photoApi = {
  // Get all photos
  getPhotos: async (params = {}) => {
    const response = await photosApi.get('/photos/', { params });
    return response.data;
  },

  // Upload photo
  uploadPhoto: async (file, metadata = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add metadata
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    const response = await photosApi.post('/photos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get photo by ID
  getPhoto: async (photoId) => {
    const response = await photosApi.get(`/photos/${photoId}`);
    return response.data;
  },

  // Delete photo
  deletePhoto: async (photoId) => {
    const response = await photosApi.delete(`/photos/${photoId}`);
    return response.data;
  },

  // Update photo metadata
  updatePhoto: async (photoId, metadata) => {
    const response = await photosApi.put(`/photos/${photoId}`, metadata);
    return response.data;
  }
};

// Convenience functions for common operations
export const getUserProfile = userApi.getProfile;
export const updateUserProfile = userApi.updateProfile;
export const getPhotos = photoApi.getPhotos;
export const uploadPhoto = photoApi.uploadPhoto;

// Health check functions
export const checkServiceHealth = async () => {
  const healthChecks = await Promise.allSettled([
    usersApi.get('/health'),
    photosApi.get('/health')
  ]);

  return {
    users: healthChecks[0].status === 'fulfilled' ? 'healthy' : 'unhealthy',
    photos: healthChecks[1].status === 'fulfilled' ? 'healthy' : 'unhealthy'
  };
};

export default {
  users: userApi,
  photos: photoApi,
  health: checkServiceHealth
};
