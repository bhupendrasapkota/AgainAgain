import { ApiResponse, PaginatedResponse, User, Photo, Collection, Category, Tag, SignupData } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const REQUEST_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

async function handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
  const data = await response.json();
  console.log('API Response:', data); // Add detailed logging
  
  if (!response.ok) {
    // If it's a Django validation error, it will have a non-empty data object
    if (data && Object.keys(data).length > 0) {
      throw new Error(JSON.stringify(data));
    }
    throw new Error(data.message || 'An error occurred');
  }

  // If the response is successful, return the data directly
  return {
    data: data,
    status: response.status,
    message: data.message
  };
}

function buildUrl(endpoint: string, params?: Record<string, any>): string {
  const url = new URL(`${API_URL}${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, value.toString());
      }
    });
  }
  return url.toString();
}

interface RequestOptions extends RequestInit {
  params?: Record<string, any>;
  timeout?: number;
  retries?: number;
}

async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { params, timeout = REQUEST_TIMEOUT, retries = MAX_RETRIES, ...fetchOptions } = options;
  const token = localStorage.getItem('token');
  const headers = new Headers({
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...fetchOptions.headers
  });

  // Remove Content-Type header for FormData
  if (fetchOptions.body instanceof FormData) {
    headers.delete('Content-Type');
  }

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(buildUrl(endpoint, params), {
        ...fetchOptions,
        headers,
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return await handleResponse<T>(response);
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on certain errors
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new Error('Network error: Please check your internet connection');
      }

      // If this was the last attempt, throw the error
      if (attempt === retries) {
        throw lastError;
      }

      // Wait before retrying
      await delay(RETRY_DELAY * (attempt + 1));
    }
  }

  throw lastError;
}

export const api = {
  get: <T>(endpoint: string, options: RequestOptions = {}) => 
    request<T>(endpoint, { ...options, method: 'GET' }),
  
  post: <T>(endpoint: string, data: any, options: RequestOptions = {}) => 
    request<T>(endpoint, { ...options, method: 'POST', body: data instanceof FormData ? data : JSON.stringify(data) }),
  
  put: <T>(endpoint: string, data: any, options: RequestOptions = {}) => 
    request<T>(endpoint, { ...options, method: 'PUT', body: JSON.stringify(data) }),
  
  delete: <T>(endpoint: string, options: RequestOptions = {}) => 
    request<T>(endpoint, { ...options, method: 'DELETE' }),

  // Auth endpoints
  auth: {
    login: (credentials: { email: string; password: string }) => 
      api.post<{ token: string; user: User }>('/auth/login/', credentials),
    
    signup: (userData: SignupData) => 
      api.post<{ token: string; user: User }>('/auth/register/', userData),
    
    logout: () => {
      localStorage.removeItem('token');
      return Promise.resolve();
    },

    refreshToken: () => api.post<{ token: string }>('/auth/refresh-token/', {}),
    
    forgotPassword: (email: string) => 
      api.post('/auth/forgot-password/', { email }),
    
    resetPassword: (token: string, password: string) => 
      api.post('/auth/reset-password/', { token, password })
  },

  // User endpoints
  user: {
    getProfile: () => api.get<User>('/users/profile/'),
    updateProfile: (data: Partial<User>) => api.put<User>('/users/profile/', data),
    updateAvatar: (data: FormData) => api.post<User>('/users/avatar/', data),
    follow: (userId: string) => api.post(`/users/${userId}/follow/`, {}),
    unfollow: (userId: string) => api.delete(`/users/${userId}/follow/`, {}),
    getFollowers: (userId: string) => api.get<PaginatedResponse<User>>(`/users/${userId}/followers/`),
    getFollowing: (userId: string) => api.get<PaginatedResponse<User>>(`/users/${userId}/following/`)
  },

  // Collection endpoints
  collections: {
    getAll: (params?: { user?: string; search?: string; page?: number }) => 
      api.get<PaginatedResponse<Collection>>('/collections', { 
        params: { ...params, page: params?.page || 1 }
      }),
    getById: (id: string) => api.get<Collection>(`/collections/${id}`),
    create: (data: {
      name: string;
      description?: string;
      is_public?: boolean;
    }) => api.post<Collection>('/collections', data),
    update: (id: string, data: {
      name?: string;
      description?: string;
      cover_photo?: string;
      is_public?: boolean;
    }) => api.put<Collection>(`/collections/${id}`, data),
    delete: (id: string) => api.delete(`/collections/${id}`, {}),
    like: (id: string) => api.post<Collection>(`/collections/${id}/like`, {}),
    unlike: (id: string) => api.delete<Collection>(`/collections/${id}/like`, {}),
    addPhoto: (id: string, photoId: string) => 
      api.post<Collection>(`/collections/${id}/photos`, { photo_id: photoId }),
    removePhoto: (id: string, photoId: string) => 
      api.delete<Collection>(`/collections/${id}/photos/${photoId}`, {})
  },

  // Photo endpoints
  photos: {
    getAll: (params?: {
      category?: string;
      tag?: string;
      user?: string;
      search?: string;
      featured?: boolean;
      page?: number;
    }) => api.get<PaginatedResponse<Photo>>('/photos', { 
      params: { ...params, page: params?.page || 1 }
    }),
    getById: (id: string) => api.get<Photo>(`/photos/${id}`),
    upload: (data: FormData) => api.post<Photo>('/photos/upload', data),
    update: (id: string, data: {
      title?: string;
      description?: string;
      categories?: string[];
      tags?: string[];
      is_public?: boolean;
    }) => api.put<Photo>(`/photos/${id}`, data),
    delete: (id: string) => api.delete(`/photos/${id}`, {}),
    like: (id: string) => api.post<Photo>(`/photos/${id}/like`, {}),
    unlike: (id: string) => api.delete<Photo>(`/photos/${id}/like`, {}),
    download: (id: string, size?: 'small' | 'medium' | 'large' | 'original') => {
      const url = buildUrl(`/photos/${id}/download`, size ? { size } : undefined);
      window.open(url, '_blank');
      return Promise.resolve();
    }
  },

  // Category endpoints
  categories: {
    getAll: () => api.get<Category[]>('/categories'),
    getById: (id: string) => api.get<Category>(`/categories/${id}`),
    create: (data: { name: string; description?: string }) => 
      api.post<Category>('/categories', data),
    update: (id: string, data: { name?: string; description?: string }) => 
      api.put<Category>(`/categories/${id}`, data),
    delete: (id: string) => api.delete(`/categories/${id}`, {})
  },

  // Tag endpoints
  tags: {
    getAll: () => api.get<Tag[]>('/tags'),
    getById: (id: string) => api.get<Tag>(`/tags/${id}`),
    create: (data: { name: string; description?: string }) => 
      api.post<Tag>('/tags', data),
    update: (id: string, data: { name?: string; description?: string }) => 
      api.put<Tag>(`/tags/${id}`, data),
    delete: (id: string) => api.delete(`/tags/${id}`, {})
  }
}; 