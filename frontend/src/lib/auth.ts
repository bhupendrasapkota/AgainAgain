import { User } from '@/types';
import { api } from './api';

export async function login(email: string, password: string) {
  try {
    const response = await api.auth.login({ email, password });
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      return response.data.user;
    }
    throw new Error('No token received');
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

export async function signup(userData: {
  email: string;
  password: string;
  fullName: string;
  role: string;
}) {
  try {
    const response = await api.auth.signup(userData);
    if (response.data && response.data.token) {
      localStorage.setItem('token', response.data.token);
      return response.data.user;
    }
    throw new Error('No token received');
  } catch (error) {
    console.error('Signup error:', error);
    throw error;
  }
}

export async function logout() {
  try {
    await api.auth.logout();
    localStorage.removeItem('token');
  } catch (error) {
    console.error('Logout error:', error);
    throw error;
  }
}

export async function refreshToken() {
  try {
    const response = await api.auth.refreshToken();
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      return response;
    }
    throw new Error('No token received');
  } catch (error) {
    console.error('Token refresh error:', error);
    throw error;
  }
}

export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export async function getCurrentUser(): Promise<User | null> {
  try {
    if (!isAuthenticated()) {
      return null;
    }
    const response = await api.user.getProfile();
    return response.data;
  } catch (error) {
    console.error('Get current user error:', error);
    return null;
  }
}

export function requireAuth(callback: () => void) {
  if (!isAuthenticated()) {
    window.location.href = '/login';
    return;
  }
  callback();
} 