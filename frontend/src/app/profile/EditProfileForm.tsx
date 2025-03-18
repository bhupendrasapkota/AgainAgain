'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  bio: string;
  profile_picture: string;
  created_at: string;
  about: string;
  role: 'artist' | 'curator' | 'collector';
  artist_statement?: string;
  mediums?: string[];
  years_experience?: number;
  gallery_affiliations?: string[];
  exhibitions?: {
    title: string;
    date: string;
    location: string;
    type: 'solo' | 'group';
  }[];
  contact: {
    phone?: string;
    website?: string;
    instagram?: string;
    facebook?: string;
  };
  followers_count: number;
  following_count: number;
  is_active: boolean;
  stats: {
    artworks: number;
    exhibitions: number;
    views: number;
    followers: number;
    following: number;
  };
}

interface EditProfileFormProps {
  isOpen: boolean;
  onClose: () => void;
  user?: User;
  onSave: (updatedUser: Partial<User>) => void;
}

const defaultUser: User = {
  id: '',
  username: '',
  email: '',
  full_name: '',
  bio: '',
  profile_picture: '/placeholder-avatar.jpg',
  created_at: new Date().toISOString(),
  about: '',
  role: 'artist',
  artist_statement: '',
  mediums: [],
  years_experience: 0,
  gallery_affiliations: [],
  exhibitions: [],
  contact: {
    phone: '',
    website: '',
    instagram: '',
    facebook: ''
  },
  followers_count: 0,
  following_count: 0,
  is_active: true,
  stats: {
    artworks: 0,
    exhibitions: 0,
    views: 0,
    followers: 0,
    following: 0
  }
};

export default function EditProfileForm({ isOpen, onClose, user = defaultUser, onSave }: EditProfileFormProps) {
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    bio: '',
    about: '',
    role: 'artist' as 'artist' | 'curator' | 'collector',
    artist_statement: '',
    mediums: [] as string[],
    years_experience: 0,
    gallery_affiliations: [] as string[],
    exhibitions: [] as Array<{
      title: string;
      date: string;
      location: string;
      type: 'solo' | 'group';
    }>,
    contact: {
      phone: '',
      website: '',
      instagram: '',
      facebook: ''
    }
  });

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name,
        username: user.username,
        email: user.email,
        bio: user.bio,
        about: user.about,
        role: user.role,
        artist_statement: user.artist_statement || '',
        mediums: user.mediums || [],
        years_experience: user.years_experience || 0,
        gallery_affiliations: user.gallery_affiliations || [],
        exhibitions: user.exhibitions || [],
        contact: {
          phone: user.contact?.phone || '',
          website: user.contact?.website || '',
          instagram: user.contact?.instagram || '',
          facebook: user.contact?.facebook || ''
        }
      });
    }
  }, [user]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name.startsWith('contact.')) {
      const contactField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        contact: {
          ...prev.contact,
          [contactField]: value
        }
      }));
    } else if (name === 'mediums' || name === 'gallery_affiliations') {
      setFormData(prev => ({
        ...prev,
        [name]: value.split(',').map(item => item.trim())
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleExhibitionChange = (index: number, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      exhibitions: prev.exhibitions.map((exhibition, i) => 
        i === index ? { ...exhibition, [field]: value } : exhibition
      )
    }));
  };

  const addExhibition = () => {
    setFormData(prev => ({
      ...prev,
      exhibitions: [
        ...prev.exhibitions,
        {
          title: '',
          date: '',
          location: '',
          type: 'solo'
        }
      ]
    }));
  };

  const removeExhibition = (index: number) => {
    setFormData(prev => ({
      ...prev,
      exhibitions: prev.exhibitions.filter((_, i) => i !== index)
    }));
  };

  return (
    <div 
      className={`fixed top-0 right-0 w-[1400px] h-screen bg-white transform transition-all duration-500 ease-in-out shadow-lg ${
        isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full pointer-events-none'
      } z-40 overflow-y-auto`}
    >
      <div className="p-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Edit Profile</h2>
          <button 
            onClick={onClose}
            className="text-2xl hover:text-gray-600"
          >
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Profile Picture Upload */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Profile Picture</h3>
                <div className="flex items-start gap-8">
                  <div className="relative w-48 h-48 border-2 border-gray-300 flex items-center justify-center overflow-hidden group">
                    <Image
                      src={user.profile_picture}
                      alt={user.full_name}
                      fill
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center">
                      <span className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">Change Photo</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-3">Upload New Picture</label>
                    <div className="relative">
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        id="profile-picture"
                        onChange={(e) => {
                          // Handle file upload
                          const file = e.target.files?.[0];
                          if (file) {
                            // TODO: Implement file upload logic
                          }
                        }}
                      />
                      <label
                        htmlFor="profile-picture"
                        className="block w-full px-6 py-4 border-2 border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-black transition-colors duration-300"
                      >
                        <div className="flex flex-col items-center gap-3">
                          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                          </svg>
                          <span className="text-sm text-gray-600">Drag and drop your image here</span>
                          <span className="text-xs text-gray-400">or click to browse</span>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Full Name</label>
                    <input
                      type="text"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Username</label>
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Email</label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Role</label>
                    <select
                      name="role"
                      value={formData.role}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    >
                      <option value="artist">Artist</option>
                      <option value="curator">Curator</option>
                      <option value="collector">Collector</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Phone</label>
                    <input
                      type="tel"
                      name="contact.phone"
                      value={formData.contact.phone}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Website</label>
                    <input
                      type="url"
                      name="contact.website"
                      value={formData.contact.website}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Instagram</label>
                    <input
                      type="text"
                      name="contact.instagram"
                      value={formData.contact.instagram}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Facebook</label>
                    <input
                      type="text"
                      name="contact.facebook"
                      value={formData.contact.facebook}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Bio and About */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Bio & About</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Bio</label>
                    <textarea
                      name="bio"
                      value={formData.bio}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      rows={2}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">About</label>
                    <textarea
                      name="about"
                      value={formData.about}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      rows={4}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Artist Statement</label>
                    <textarea
                      name="artist_statement"
                      value={formData.artist_statement}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      rows={4}
                    />
                  </div>
                </div>
              </div>

              {/* Artist/Curator Specific Information */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Professional Information</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Mediums (comma-separated)</label>
                    <input
                      type="text"
                      name="mediums"
                      value={formData.mediums.join(', ')}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Years of Experience</label>
                    <input
                      type="number"
                      name="years_experience"
                      value={formData.years_experience}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Gallery Affiliations (comma-separated)</label>
                    <input
                      type="text"
                      name="gallery_affiliations"
                      value={formData.gallery_affiliations.join(', ')}
                      onChange={handleChange}
                      className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Exhibitions */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Exhibitions</h3>
                <div className="space-y-4">
                  {formData.exhibitions.map((exhibition, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="font-medium">Exhibition {index + 1}</h4>
                        <button
                          type="button"
                          onClick={() => removeExhibition(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Title</label>
                          <input
                            type="text"
                            value={exhibition.title}
                            onChange={(e) => handleExhibitionChange(index, 'title', e.target.value)}
                            className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Date</label>
                          <input
                            type="date"
                            value={exhibition.date}
                            onChange={(e) => handleExhibitionChange(index, 'date', e.target.value)}
                            className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Location</label>
                          <input
                            type="text"
                            value={exhibition.location}
                            onChange={(e) => handleExhibitionChange(index, 'location', e.target.value)}
                            className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Type</label>
                          <select
                            value={exhibition.type}
                            onChange={(e) => handleExhibitionChange(index, 'type', e.target.value)}
                            className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                          >
                            <option value="solo">Solo Exhibition</option>
                            <option value="group">Group Exhibition</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={addExhibition}
                    className="w-full px-6 py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-black hover:text-black transition-colors duration-300"
                  >
                    Add Exhibition
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-4 pt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-8 py-2.5 border border-gray-300 hover:border-black transition-all duration-300 text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-8 py-2.5 bg-black text-white hover:bg-white hover:text-black border-2 border-black transition-all duration-300 text-sm"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 