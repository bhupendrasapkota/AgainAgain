export const ROUTES = {
  HOME: '/',
  AUTH: {
    LOGIN: '/login',
    SIGNUP: '/signup',
    FORGOT_PASSWORD: '/forgot-password',
    RESET_PASSWORD: '/reset-password'
  },
  PROFILE: {
    BASE: '/profile',
    EDIT: '/profile/edit',
    FOLLOWERS: (userId: string) => `/profile/${userId}/followers`,
    FOLLOWING: (userId: string) => `/profile/${userId}/following`
  },
  COLLECTIONS: {
    BASE: '/collections',
    NEW: '/collections/new',
    BY_ID: (id: string) => `/collections/${id}`,
    EDIT: (id: string) => `/collections/${id}/edit`,
    PHOTOS: (id: string) => `/collections/${id}/photos`
  },
  PHOTOS: {
    BASE: '/photos',
    NEW: '/photos/new',
    BY_ID: (id: string) => `/photos/${id}`,
    EDIT: (id: string) => `/photos/${id}/edit`,
    UPLOAD: '/photos/upload',
    DOWNLOAD: (id: string) => `/photos/${id}/download`
  },
  CATEGORIES: {
    BASE: '/categories',
    BY_ID: (id: string) => `/categories/${id}`,
    NEW: '/categories/new',
    EDIT: (id: string) => `/categories/${id}/edit`
  },
  TAGS: {
    BASE: '/tags',
    BY_ID: (id: string) => `/tags/${id}`,
    NEW: '/tags/new',
    EDIT: (id: string) => `/tags/${id}/edit`
  },
  LEGAL: {
    TERMS: '/terms',
    PRIVACY: '/privacy',
    COPYRIGHT: '/copyright'
  },
  SUPPORT: {
    HELP: '/help',
    CONTACT: '/contact',
    FAQ: '/faq'
  },
  ABOUT: {
    BASE: '/about',
    CAREERS: '/careers',
    PRESS: '/press'
  }
}; 