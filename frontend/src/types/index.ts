export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  profile_picture?: string;
  bio?: string;
  about?: string;
  followers_count: number;
  following_count: number;
  photos_count: number;
  is_following?: boolean;
  created_at: string;
  role?: string;
  contact?: string;
}

export interface Photo {
  id: string;
  title: string;
  description?: string;
  image_url: string;
  user: string;
  categories: Category[];
  tags: Tag[];
  created_at: string;
  updated_at: string;
  likes: number;
  views: number;
  featured: boolean;
  is_public: boolean;
  is_liked?: boolean;
  width?: number;
  height?: number;
  format?: string;
  location?: string;
  camera_info?: any;
  medium?: string;
  year?: string;
  artist?: string;
}

export interface Collection {
  id: string;
  name: string;
  description?: string;
  user: string;
  curator: string;
  cover_image?: string;
  created_at: string;
  updated_at: string;
  artwork_count: number;
  likes: number;
  views: number;
  is_public: boolean;
  is_liked?: boolean;
  exhibition_date?: string;
  location?: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
}

export interface SignupData {
  email: string;
  password: string;
  fullName: string;
  role: string;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedData<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

export type PaginatedResponse<T> = ApiResponse<PaginatedData<T>>; 