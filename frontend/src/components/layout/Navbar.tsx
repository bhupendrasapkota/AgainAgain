'use client';

import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { ROUTES } from '@/constants/routes';
import ProfileMenu from '../client/ProfileMenu';

export default function Navbar() {
  const { isAuthenticated, loading } = useAuth();

  return (
    <nav className="fixed top-0 left-0 right-0 w-full bg-white border-b border-black h-20 z-50">
      <div className="max-w-[1750px] mx-auto h-full px-10">
        <div className="flex items-center justify-between h-full">
          <div className="flex items-center gap-10">
            <Link 
              href={ROUTES.HOME} 
              className="hover:opacity-80 transition-all duration-300"
            >
              <svg 
                width="40" 
                height="40" 
                viewBox="0 0 40 40" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
                className="animate-pulse"
              >
                {/* A */}
                <path 
                  d="M8 32L20 8L32 32" 
                  stroke="black" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                  className="animate-draw"
                />
                {/* V */}
                <path 
                  d="M12 32L20 16L28 32" 
                  stroke="black" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                  className="animate-draw"
                />
              </svg>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-6">
              <Link 
                href={ROUTES.HOME} 
                className="text-base text-black hover:text-gray-600 transition-all duration-300 relative group"
              >
                Home
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-black group-hover:w-full transition-all duration-300"></span>
              </Link>
              <Link 
                href={ROUTES.PHOTOS.BASE} 
                className="text-base text-black hover:text-gray-600 transition-all duration-300 relative group"
              >
                Photos
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-black group-hover:w-full transition-all duration-300"></span>
              </Link>
              <Link 
                href={ROUTES.COLLECTIONS.BASE} 
                className="text-base text-black hover:text-gray-600 transition-all duration-300 relative group"
              >
                Collections
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-black group-hover:w-full transition-all duration-300"></span>
              </Link>
              <Link 
                href={ROUTES.CATEGORIES.BASE} 
                className="text-base text-black hover:text-gray-600 transition-all duration-300 relative group"
              >
                Categories
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-black group-hover:w-full transition-all duration-300"></span>
              </Link>
            </div>
          </div>

          {/* Auth Buttons or Profile Menu */}
          <div className="flex items-center gap-6">
            {loading ? (
              <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
            ) : isAuthenticated ? (
              <ProfileMenu />
            ) : (
              <>
                <Link 
                  href={ROUTES.AUTH.LOGIN} 
                  className="bg-white text-black px-6 py-2 text-base font-medium border-2 border-black hover:bg-black hover:text-white transition-all duration-300"
                >
                  Login
                </Link>
                <Link 
                  href={ROUTES.AUTH.SIGNUP} 
                  className="bg-black text-white px-6 py-2 text-base font-medium border-2 border-black hover:bg-white hover:text-black transition-all duration-300"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
} 