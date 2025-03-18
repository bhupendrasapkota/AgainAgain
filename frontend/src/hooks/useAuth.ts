import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User, SignupData } from '@/types';
import * as authUtils from '@/lib/auth';
import { ROUTES } from '@/constants/routes';
import { API_ERROR_MESSAGES } from '@/constants/api';

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export function useAuth() {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
    isAuthenticated: false
  });

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  const checkAuth = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      // First check if we have a token
      const hasToken = authUtils.isAuthenticated();
      if (!hasToken) {
        setState(prev => ({
          ...prev,
          user: null,
          isAuthenticated: false,
          loading: false
        }));
        return;
      }

      // If we have a token, try to get the user profile
      const currentUser = await authUtils.getCurrentUser();
      console.log('useAuth - Current user:', currentUser);
      
      setState(prev => ({
        ...prev,
        user: currentUser,
        isAuthenticated: !!currentUser,
        loading: false
      }));
    } catch (err) {
      console.error('useAuth - Check auth error:', err);
      setState(prev => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        loading: false,
        error: err instanceof Error ? err.message : API_ERROR_MESSAGES.UNAUTHORIZED
      }));
    }
  }, []);

  // Check auth status on mount and when token changes
  useEffect(() => {
    console.log('useAuth - Initial check');
    checkAuth();
  }, [checkAuth]);

  // Listen for storage events to sync auth state across tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [checkAuth]);

  const refreshToken = useCallback(async () => {
    try {
      const response = await authUtils.refreshToken();
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        await checkAuth(); // Check auth status after token refresh
        return true;
      }
      return false;
    } catch (err) {
      console.error('Token refresh error:', err);
      return false;
    }
  }, [checkAuth]);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const user = await authUtils.login(email, password);
      console.log('useAuth - Login successful:', user);
      await checkAuth(); // Check auth status after login
      setState(prev => ({
        ...prev,
        user,
        isAuthenticated: true,
        loading: false
      }));
      router.push(ROUTES.PROFILE.BASE);
    } catch (err) {
      console.error('useAuth - Login error:', err);
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : API_ERROR_MESSAGES.UNAUTHORIZED
      }));
      throw err;
    }
  }, [router, checkAuth]);

  const signup = useCallback(async (userData: SignupData) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const user = await authUtils.signup(userData);
      await checkAuth(); // Check auth status after signup
      setState(prev => ({
        ...prev,
        user,
        isAuthenticated: true,
        loading: false
      }));
      router.push(ROUTES.PROFILE.BASE);
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : API_ERROR_MESSAGES.DEFAULT
      }));
      throw err;
    }
  }, [router, checkAuth]);

  const logout = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      await authUtils.logout();
      setState(prev => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        loading: false
      }));
      router.push(ROUTES.HOME);
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : API_ERROR_MESSAGES.DEFAULT
      }));
      throw err;
    }
  }, [router]);

  const requireAuth = useCallback((callback: () => void) => {
    if (!state.isAuthenticated) {
      router.push(ROUTES.AUTH.LOGIN);
      return;
    }
    callback();
  }, [state.isAuthenticated, router]);

  return {
    ...state,
    login,
    signup,
    logout,
    requireAuth,
    refreshToken,
    checkAuth
  };
} 