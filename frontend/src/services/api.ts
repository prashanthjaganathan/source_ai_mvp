import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Base URLs for different services
const API_BASE_URLS = {
  users: 'http://localhost:8001',
  photos: 'http://localhost:8002', 
  scheduler: 'http://localhost:8003',
};

// Create axios instances for each service
const createApiInstance = (baseURL: string): AxiosInstance => {
  const instance = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use(
    (config) => {
      const token = authService.getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Token expired or invalid
        authService.clearAuthToken();
      }
      return Promise.reject(error);
    }
  );

  return instance;
};

// API instances
const usersApi = createApiInstance(API_BASE_URLS.users);
const photosApi = createApiInstance(API_BASE_URLS.photos);
const schedulerApi = createApiInstance(API_BASE_URLS.scheduler);

// Types
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  username: string;
}

interface User {
  id: number;
  uid: string;
  email: string;
  name: string;
  age?: number;
  gender?: string;
  incentives_earned: number;
  incentives_redeemed: number;
  incentives_available: number;
  created_at: string;
  updated_at?: string;
}

interface Photo {
  id: number;
  title: string;
  description: string;
  filename: string;
  url: string;
  file_size: number;
  mime_type: string;
  width: number;
  height: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

interface Schedule {
  id: number;
  user_id: string;
  frequency_hours: number;
  notifications_enabled: boolean;
  silent_mode_enabled: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_triggered_at: string | null;
  trigger_count: number;
}

interface PhotoCaptureRequest {
  user_id: string;
}

interface PhotoCaptureResponse {
  success: boolean;
  capture_session_id: string;
  user_id: string;
  message: string;
}

// Auth Service
class AuthService {
  private authToken: string | null = null;

  setAuthToken(token: string) {
    this.authToken = token;
  }

  getAuthToken(): string | null {
    return this.authToken;
  }

  clearAuthToken() {
    this.authToken = null;
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await usersApi.post('/users/login', {
      email,
      password,
    });
    return response.data;
  }

  async register(email: string, password: string, fullName: string, username: string): Promise<User> {
    const response: AxiosResponse<User> = await usersApi.post('/users/register', {
      email,
      password,
      full_name: fullName,
      username,
    });
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response: AxiosResponse<User> = await usersApi.get('/users/profile');
    return response.data;
  }

  async updateProfile(userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await usersApi.put('/users/profile', userData);
    return response.data;
  }

  async getUserSettings(): Promise<any> {
    const response = await usersApi.get('/users/profile/settings');
    return response.data;
  }

  async updateUserSettings(settings: any): Promise<User> {
    const response: AxiosResponse<User> = await usersApi.put('/users/profile/settings', settings);
    return response.data;
  }

  async getUserStats(): Promise<any> {
    const response = await usersApi.get('/users/profile/stats');
    return response.data;
  }
}

// Photos Service
class PhotosService {
  async getPhotos(userId?: number, skip: number = 0, limit: number = 20): Promise<{photos: Photo[], total: number, page: number, size: number, pages: number}> {
    const params: any = { skip, limit };
    if (userId) params.user_id = userId;
    
    const response = await photosApi.get('/photos/', { params });
    return response.data;
  }

  async getPhoto(photoId: number): Promise<Photo> {
    const response: AxiosResponse<Photo> = await photosApi.get(`/photos/${photoId}`);
    return response.data;
  }

  async uploadPhoto(photoUri: string, title?: string, description?: string, userId?: number): Promise<Photo> {
    const formData = new FormData();
    formData.append('file', {
      uri: photoUri,
      type: 'image/jpeg',
      name: 'photo.jpg',
    } as any);
    
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);
    if (userId) formData.append('user_id', userId.toString());

    const response: AxiosResponse<{photo: Photo}> = await photosApi.post('/photos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.photo;
  }

  async updatePhoto(photoId: number, photoData: Partial<Photo>): Promise<Photo> {
    const response: AxiosResponse<Photo> = await photosApi.put(`/photos/${photoId}`, photoData);
    return response.data;
  }

  async deletePhoto(photoId: number): Promise<void> {
    await photosApi.delete(`/photos/${photoId}`);
  }
}

// Scheduler Service
class SchedulerService {
  async getSchedules(userId?: string): Promise<Schedule[]> {
    const params: any = {};
    if (userId) params.user_id = userId;
    
    const response = await schedulerApi.get('/scheduler/schedules/', { params });
    return response.data;
  }

  async createSchedule(scheduleData: Partial<Schedule>): Promise<Schedule> {
    const response: AxiosResponse<Schedule> = await schedulerApi.post('/scheduler/schedules/', scheduleData);
    return response.data;
  }

  async updateSchedule(scheduleId: number, scheduleData: Partial<Schedule>): Promise<Schedule> {
    const response: AxiosResponse<Schedule> = await schedulerApi.put(`/scheduler/schedules/${scheduleId}`, scheduleData);
    return response.data;
  }

  async deleteSchedule(scheduleId: number): Promise<void> {
    await schedulerApi.delete(`/scheduler/schedules/${scheduleId}`);
  }

  async pauseSchedule(scheduleId: number): Promise<void> {
    await schedulerApi.post(`/scheduler/schedules/${scheduleId}/pause`);
  }

  async resumeSchedule(scheduleId: number): Promise<void> {
    await schedulerApi.post(`/scheduler/schedules/${scheduleId}/resume`);
  }

  async triggerManualCapture(userId: string): Promise<PhotoCaptureResponse> {
    const response: AxiosResponse<PhotoCaptureResponse> = await schedulerApi.post('/capture/capture', {
      user_id: userId,
    });
    return response.data;
  }

  async getCapturedPhotos(userId?: string): Promise<any> {
    const params: any = {};
    if (userId) params.user_id = userId;
    
    const response = await schedulerApi.get('/capture/photos', { params });
    return response.data;
  }

  async getCaptureSessions(userId: string, limit: number = 10): Promise<any> {
    const response = await schedulerApi.get(`/capture/sessions/${userId}`, {
      params: { limit }
    });
    return response.data;
  }

  async sendNotification(userId: string, message: string): Promise<any> {
    const response = await schedulerApi.post('/notifications/send', {
      user_id: userId,
      message,
    });
    return response.data;
  }
}

// Export service instances
export const authService = new AuthService();
export const photosService = new PhotosService();
export const schedulerService = new SchedulerService();

// Export types
export type { User, Photo, Schedule, PhotoCaptureRequest, PhotoCaptureResponse };
