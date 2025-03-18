'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { ROUTES } from '@/constants/routes';

export default function ProfilePicture() {
  const { user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  console.log('ProfilePicture - User data:', user);

  if (!user) {
    console.log('ProfilePicture - No user data available');
    return null;
  }

  // Format Cloudinary URL
  const getProfilePictureUrl = (url: string | undefined | null): string | null => {
    if (!url) return null;
    // If it's already a full URL, return it
    if (url.startsWith('http')) return url;
    // If it's a Cloudinary path, construct the full URL
    return `https://res.cloudinary.com/${process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME}/image/upload/${url}`;
  };

  const profilePictureUrl = getProfilePictureUrl(user.profile_picture);

  return (
    <div className="relative">
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center focus:outline-none"
      >
        <div className="relative w-14 h-14 overflow-hidden border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all duration-200">
          {profilePictureUrl ? (
            <Image
              src={profilePictureUrl}
              alt={user.full_name || user.username}
              fill
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="w-full h-full bg-white flex items-center justify-center">
              <span className="text-black text-xl font-medium">
                {(user.full_name || user.username).charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </div>
      </button>

      {/* Dropdown Menu */}
      <div 
        className={`absolute right-0 mt-2 w-64 bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50 transform transition-all duration-300 ease-in-out ${
          isDropdownOpen 
            ? 'opacity-100 translate-y-0' 
            : 'opacity-0 -translate-y-2 pointer-events-none'
        }`}
      >
        {/* User Info Section */}
        <div className="px-6 py-3 border-b-2 border-black">
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 overflow-hidden border-2 border-black">
              {profilePictureUrl ? (
                <Image
                  src={profilePictureUrl}
                  alt={user.full_name || user.username}
                  fill
                  className="object-cover"
                  unoptimized
                />
              ) : (
                <div className="w-full h-full bg-white flex items-center justify-center">
                  <span className="text-black text-lg font-medium">
                    {(user.full_name || user.username).charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-black font-medium truncate">{user.full_name || user.username}</p>
              <p className="text-sm text-gray-500">@{user.username}</p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <Link
          href={ROUTES.PROFILE.BASE}
          className="block px-6 py-3 text-base text-black hover:bg-black hover:text-white transition-all duration-200"
          onClick={() => setIsDropdownOpen(false)}
        >
          Profile
        </Link>
        <button
          onClick={() => {
            logout();
            setIsDropdownOpen(false);
          }}
          className="block w-full text-left px-6 py-3 text-base text-black hover:bg-black hover:text-white transition-all duration-200"
        >
          Logout
        </button>
      </div>
    </div>
  );
} 