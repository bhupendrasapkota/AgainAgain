export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    SIGNUP: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH_TOKEN: '/auth/refresh-token',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password'
  },
  USER: {
    PROFILE: '/users/profile',
    UPDATE_PROFILE: '/users/profile',
    UPDATE_AVATAR: '/users/avatar',
    FOLLOW: (userId: string) => `/users/${userId}/follow`,
    UNFOLLOW: (userId: string) => `/users/${userId}/follow`,
    FOLLOWERS: (userId: string) => `/users/${userId}/followers`,
    FOLLOWING: (userId: string) => `/users/${userId}/following`
  },
  COLLECTIONS: {
    BASE: '/collections',
    BY_ID: (id: string) => `/collections/${id}`,
    LIKE: (id: string) => `/collections/${id}/like`,
    UNLIKE: (id: string) => `/collections/${id}/like`,
    PHOTOS: (id: string) => `/collections/${id}/photos`,
    REMOVE_PHOTO: (id: string, photoId: string) => `/collections/${id}/photos/${photoId}`
  },
  PHOTOS: {
    BASE: '/photos',
    BY_ID: (id: string) => `/photos/${id}`,
    UPLOAD: '/photos/upload',
    LIKE: (id: string) => `/photos/${id}/like`,
    UNLIKE: (id: string) => `/photos/${id}/like`,
    DOWNLOAD: (id: string) => `/photos/${id}/download`
  },
  CATEGORIES: {
    BASE: '/categories',
    BY_ID: (id: string) => `/categories/${id}`
  },
  TAGS: {
    BASE: '/tags',
    BY_ID: (id: string) => `/tags/${id}`
  }
};

export const API_ERROR_MESSAGES = {
  DEFAULT: 'An error occurred. Please try again.',
  NETWORK: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Please log in to continue.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  RATE_LIMIT: 'Too many requests. Please try again later.',
  INVALID_TOKEN: 'Your session has expired. Please log in again.',
  FILE_TOO_LARGE: 'File size exceeds the maximum limit.',
  INVALID_FILE_TYPE: 'Invalid file type. Please upload a supported format.'
}; 