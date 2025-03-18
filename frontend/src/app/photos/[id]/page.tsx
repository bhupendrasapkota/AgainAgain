'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Photo, ApiResponse } from '@/types';
import { api } from '@/lib/api';
import { ActionButton } from '@/components/ui/shared/ActionButton';
import { DateDisplay } from '@/components/ui/shared/DateDisplay';
import Icon from '@/components/ui/shared/Icon';

interface PhotoDetailProps {
  params: {
    id: string;
  };
}

export default function PhotoDetail({ params }: PhotoDetailProps) {
  const router = useRouter();
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPhoto();
  }, [params.id]);

  const fetchPhoto = async () => {
    try {
      setLoading(true);
      const response = await api.photos.getById(params.id) as ApiResponse<Photo>;
      setPhoto(response.data);
    } catch (err: any) {
      setError('Failed to load photo');
      console.error('Error fetching photo:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!photo) return;
    try {
      if (photo.isLiked) {
        await api.photos.unlike(photo.id);
      } else {
        await api.photos.like(photo.id);
      }
      setPhoto({
        ...photo,
        isLiked: !photo.isLiked,
        likes: photo.isLiked ? photo.likes - 1 : photo.likes + 1
      });
    } catch (err: any) {
      console.error('Error liking photo:', err);
    }
  };

  const handleDownload = () => {
    if (!photo) return;
    api.photos.download(photo.id);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error || !photo) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-xl text-red-600">{error || 'Photo not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Photo Header */}
      <div className="w-full bg-black text-white py-8">
        <div className="max-w-[auto] mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-4xl font-bold">{photo.title}</h1>
            <div className="flex items-center gap-4">
              <ActionButton
                icon={<Icon name="heart" fill={photo.isLiked ? "currentColor" : "none"} />}
                onClick={handleLike}
                variant="like"
                isActive={photo.isLiked}
              />
              <ActionButton
                icon={<Icon name="share" />}
                onClick={() => console.log('Share photo')}
              />
              <ActionButton
                icon={<Icon name="download" />}
                onClick={handleDownload}
              />
            </div>
          </div>
          <div className="flex items-center gap-4 text-gray-300">
            <span>By {photo.artist}</span>
            <span>•</span>
            <DateDisplay date={photo.year} format="short" />
          </div>
        </div>
      </div>

      {/* Photo Content */}
      <div className="max-w-[auto] mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Photo Image */}
          <div className="lg:col-span-2">
            <div className="relative aspect-square w-full overflow-hidden">
              <Image
                src={photo.imageUrl}
                alt={photo.title}
                fill
                className="object-cover"
              />
            </div>
          </div>

          {/* Photo Info */}
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold mb-4">About this artwork</h2>
              <p className="text-gray-600 leading-relaxed">{photo.description}</p>
            </div>

            <div>
              <h2 className="text-xl font-bold mb-4">Details</h2>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm text-gray-500">Medium</dt>
                  <dd className="text-gray-900">{photo.medium}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Year</dt>
                  <dd className="text-gray-900">{photo.year}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Views</dt>
                  <dd className="text-gray-900">{photo.views}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-500">Likes</dt>
                  <dd className="text-gray-900">{photo.likes}</dd>
                </div>
              </dl>
            </div>

            {photo.tags && photo.tags.length > 0 && (
              <div>
                <h2 className="text-xl font-bold mb-4">Tags</h2>
                <div className="flex flex-wrap gap-2">
                  {photo.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 