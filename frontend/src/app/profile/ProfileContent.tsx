'use client';

import Image from 'next/image';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { User } from '@/types';
import EditProfileForm from './EditProfileForm';
import CreateCollectionForm from './CreateCollectionForm';
import UploadArtworkForm from './UploadArtworkForm';
import { CollectionsGrid } from '@/components/ui/cards/CollectionsGrid';
import PhotoCard from '@/components/ui/cards/PhotoCard';

export default function ProfileContent() {
  const { user } = useAuth();
  const [isEditFormOpen, setIsEditFormOpen] = useState(false);
  const [isCreateCollectionFormOpen, setIsCreateCollectionFormOpen] = useState(false);
  const [isUploadArtworkFormOpen, setIsUploadArtworkFormOpen] = useState(false);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      year: 'numeric' 
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <p className="text-xl text-gray-600">Please log in to view your profile</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <EditProfileForm 
        isOpen={isEditFormOpen} 
        onClose={() => setIsEditFormOpen(false)}
        onSave={(updatedUser) => {
          // TODO: Implement save logic
          console.log('Saving user:', updatedUser);
        }}
      />

      <UploadArtworkForm
        isOpen={isUploadArtworkFormOpen}
        onClose={() => setIsUploadArtworkFormOpen(false)}
        onSubmit={(artwork) => {
          // TODO: Implement artwork upload logic
          console.log('Uploading artwork:', artwork);
        }}
      />

      {/* Profile Header with max width */}
      <div className="w-full max-h-[900px] bg-black border-b border-white relative">
        <div className="max-w-[auto] mx-auto px-4 py-16">
          {/* Top Section - Profile Image and Name */}
          <div className="flex items-center gap-16 mb-16">
            <div className="relative w-72 h-72 overflow-hidden border-2 border-white">
              <Image
                src={`https://res.cloudinary.com/${process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME}/image/upload/v1/${user.profile_picture}`}
                alt={user.full_name}
                fill
                sizes="(max-width: 768px) 100vw, 288px"
                className="object-cover"
              />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-6 mb-6">
                <h1 className="text-6xl font-bold text-white tracking-tight">{user.full_name}</h1>
                <span className="px-4 py-1.5 bg-white text-black text-sm font-medium">{user.role?.toUpperCase() || 'USER'}</span>
              </div>
              <p className="text-2xl text-gray-300 mb-4">@{user.username}</p>
              <div className="text-gray-400 text-sm flex flex-col gap-2">
                <div className="flex items-center gap-3">
                  <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                  {user.email}
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                  Member since {formatDate(user.created_at)}
                </div>
              </div>
            </div>
            {/* Quantum Painting Animation */}
            <div className="relative w-96 h-96 overflow-visible border-l border-white">
              <svg
                viewBox="0 0 400 400"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="absolute right-0 top-0 w-full h-full"
              >
                {/* Quantum Grid Background */}
                <pattern
                  id="quantum-grid"
                  x="0"
                  y="0"
                  width="40"
                  height="40"
                  patternUnits="userSpaceOnUse"
                  patternTransform="rotate(45)"
                >
                  <path
                    d="M 40 0 L 0 0 0 40"
                    fill="none"
                    stroke="rgba(255,255,255,0.03)"
                    strokeWidth="0.5"
                  />
                </pattern>
                <rect width="400" height="400" fill="url(#quantum-grid)" />

                {/* Quantum Particles */}
                <g className="animate-quantum-particles">
                  {[...Array(12)].map((_, i) => (
                    <circle
                      key={i}
                      cx={200 + Math.cos(i * 30) * 120}
                      cy={200 + Math.sin(i * 30) * 120}
                      r="2"
                      fill="white"
                      className="animate-particle"
                    />
                  ))}
                </g>

                {/* Quantum Brush Strokes */}
                <path
                  d="M200,50 C250,50 300,100 350,150 C300,200 250,250 200,250 C150,250 100,200 50,150 C100,100 150,50 200,50"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="animate-quantum-stroke"
                />

                {/* Geometric Patterns */}
                <g className="animate-geometric">
                  <path
                    d="M100,100 L300,100 L200,300 Z"
                    stroke="white"
                    strokeWidth="1"
                    fill="none"
                    className="animate-geometric-1"
                  />
                  <path
                    d="M150,150 L250,150 L200,250 Z"
                    stroke="white"
                    strokeWidth="1"
                    fill="none"
                    className="animate-geometric-2"
                  />
                </g>

                {/* Energy Waves */}
                <path
                  d="M50,200 Q200,150 350,200"
                  stroke="white"
                  strokeWidth="1"
                  strokeLinecap="round"
                  className="animate-energy-wave"
                />

                {/* Quantum Splatters */}
                <g className="animate-quantum-splatters">
                  {[...Array(6)].map((_, i) => (
                    <circle
                      key={i}
                      cx={200 + Math.cos(i * 60) * 100}
                      cy={200 + Math.sin(i * 60) * 100}
                      r="1"
                      fill="white"
                      className="animate-splatter"
                    />
                  ))}
                </g>
              </svg>
            </div>
          </div>

          {/* Stats Section - Minimal Layout */}
          <div className="flex justify-between items-end mb-16">
            <div className="flex gap-16">
              {[
                { label: 'Photos', value: '0' },
                { label: 'Followers', value: user.followers_count.toString() },
                { label: 'Following', value: user.following_count.toString() },
                { label: 'Contact', value: user.contact || 'N/A' }
              ].map((stat, index) => (
                <div key={index} className="group">
                  <div className="text-6xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-gray-300 text-lg">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Bio Section with Action Buttons */}
          <div className="mb-16">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-white">About</h2>
              <div className="flex gap-2 pr-20">
                <button 
                  onClick={() => setIsEditFormOpen(true)}
                  className="bg-white text-black px-8 py-3 text-sm font-medium hover:bg-black hover:text-white transition-all duration-300"
                >
                  Edit Profile
                </button>
                <button className="bg-transparent text-white px-8 py-3 text-sm font-medium border border-white hover:bg-white hover:text-black transition-all duration-300">
                  Share Profile
                </button>
              </div>
            </div>
            {user.bio && (
              <p className="text-gray-300 text-xl leading-relaxed max-w-full">
                {user.bio}
              </p>
            )}
            {user.about && (
              <p className="text-gray-400 text-lg mt-4 leading-relaxed max-w-2xl">
                {user.about}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Sections - Full Width */}
      <div className="w-full space-y-8">
        {/* Collections Section */}
        <div className="border border-gray-200 p-8">
          <CollectionsGrid 
            collections={[
              {
                id: "1",
                name: "Digital Horizons Exhibition",
                description: "A showcase of digital art exploring the boundaries of technology and creativity",
                user: user.id,
                curator: user.id,
                artwork_count: 12,
                cover_image: "/placeholder-collection.jpg",
                likes: 0,
                views: 0,
                is_public: true,
                created_at: "2024-03-14T00:00:00Z",
                updated_at: "2024-03-14T00:00:00Z"
              }
            ]}
            onCreateCollection={() => setIsCreateCollectionFormOpen(true)}
            onViewCollection={(id) => {
              // TODO: Implement view collection logic
              console.log('Viewing collection:', id);
            }}
            isOwner={true}
          />

          <CreateCollectionForm
            isOpen={isCreateCollectionFormOpen}
            onClose={() => setIsCreateCollectionFormOpen(false)}
            onSubmit={(collection) => {
              // TODO: Implement collection creation logic
              console.log('Creating collection:', collection);
            }}
          />
        </div>

        {/* Photos Section */}
        <div className="border border-gray-200 p-8">
          <div className="max-w-[auto] mx-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">My Artworks</h2>
              <button 
                onClick={() => setIsUploadArtworkFormOpen(true)}
                className="bg-black text-white px-4 py-2 text-sm font-medium border-2 border-black hover:bg-white hover:text-black transition-all duration-300"
              >
                Upload Artwork
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <PhotoCard
                title="Digital Dreams"
                downloads={2}
                uploadedAt="2024-03-14T00:00:00Z"
                imageUrl="/placeholder-photo.jpg"
                isOwner={true}
                tags={['digital', 'contemporary', 'abstract']}
                description="A digital artwork exploring the intersection of technology and human consciousness."
                onView={() => console.log('View artwork')}
                onDownload={() => console.log('Download artwork')}
                onLike={() => console.log('Like artwork')}
                onShare={() => console.log('Share artwork')}
                onEdit={() => console.log('Edit artwork')}
                onDelete={() => console.log('Delete artwork')}
              />
              <PhotoCard
                title="Urban Canvas"
                downloads={5}
                uploadedAt="2024-03-13T00:00:00Z"
                imageUrl="/placeholder-photo.jpg"
                isOwner={true}
                tags={['urban', 'street', 'contemporary']}
                description="A mixed media piece capturing the energy and rhythm of city life."
                onView={() => console.log('View artwork')}
                onDownload={() => console.log('Download artwork')}
                onLike={() => console.log('Like artwork')}
                onShare={() => console.log('Share artwork')}
                onEdit={() => console.log('Edit artwork')}
                onDelete={() => console.log('Delete artwork')}
              />
            </div>
          </div>
        </div>

        {/* Downloaded Photos Section */}
        <div className="border border-gray-200 p-8">
          <div className="max-w-[auto] mx-auto">
            <h2 className="text-xl font-bold mb-6">Saved Artworks</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <PhotoCard
                title="Abstract Emotions"
                photographer="@artist"
                downloads={0}
                uploadedAt="2024-03-11T00:00:00Z"
                imageUrl="/placeholder-photo.jpg"
                tags={['abstract', 'contemporary', 'emotions']}
                description="An abstract piece that captures the complexity of human emotions."
                onView={() => console.log('View artwork')}
                onDownload={() => console.log('Download artwork')}
                onLike={() => console.log('Like artwork')}
                onShare={() => console.log('Share artwork')}
              />
              <PhotoCard
                title="Modern Perspectives"
                photographer="@contemporary_artist"
                downloads={0}
                uploadedAt="2024-03-10T00:00:00Z"
                imageUrl="/placeholder-photo.jpg"
                tags={['modern', 'contemporary', 'perspective']}
                description="A contemporary artwork that challenges traditional perspectives."
                onView={() => console.log('View artwork')}
                onDownload={() => console.log('Download artwork')}
                onLike={() => console.log('Like artwork')}
                onShare={() => console.log('Share artwork')}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 