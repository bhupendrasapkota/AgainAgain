'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Collection, ApiResponse } from '@/types';
import { api } from '@/lib/api';
import { ActionButton } from '@/components/ui/shared/ActionButton';
import { DateDisplay } from '@/components/ui/shared/DateDisplay';
import Icon from '@/components/ui/shared/Icon';
import PhotoCard from '@/components/ui/cards/PhotoCard';

interface CollectionDetailProps {
  params: {
    id: string;
  };
}

export default function CollectionDetail({ params }: CollectionDetailProps) {
  const router = useRouter();
  const [collection, setCollection] = useState<Collection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCollection();
  }, [params.id]);

  const fetchCollection = async () => {
    try {
      setLoading(true);
      const response = await api.collections.getById(params.id) as ApiResponse<Collection>;
      setCollection(response.data);
    } catch (err: any) {
      setError('Failed to load collection');
      console.error('Error fetching collection:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!collection) return;
    try {
      if (collection.isLiked) {
        await api.collections.unlike(collection.id);
      } else {
        await api.collections.like(collection.id);
      }
      setCollection({
        ...collection,
        isLiked: !collection.isLiked,
        likes: collection.isLiked ? collection.likes - 1 : collection.likes + 1
      });
    } catch (err: any) {
      console.error('Error liking collection:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error || !collection) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-xl text-red-600">{error || 'Collection not found'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Collection Header */}
      <div className="w-full bg-black text-white py-8">
        <div className="max-w-[auto] mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-4xl font-bold">{collection.title}</h1>
            <div className="flex items-center gap-4">
              <ActionButton
                icon={<Icon name="heart" fill={collection.isLiked ? "currentColor" : "none"} />}
                onClick={handleLike}
                variant="like"
                isActive={collection.isLiked}
              />
              <ActionButton
                icon={<Icon name="share" />}
                onClick={() => console.log('Share collection')}
              />
            </div>
          </div>
          <div className="flex items-center gap-4 text-gray-300">
            <span>Curated by {collection.curator}</span>
            <span>•</span>
            <DateDisplay date={collection.exhibitionDate} format="short" />
            <span>•</span>
            <span>{collection.artworkCount} artworks</span>
          </div>
        </div>
      </div>

      {/* Collection Content */}
      <div className="max-w-[auto] mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4">About this collection</h2>
          <p className="text-gray-600 leading-relaxed">{collection.description}</p>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4">Details</h2>
          <dl className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <dt className="text-sm text-gray-500">Location</dt>
              <dd className="text-gray-900">{collection.location}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Exhibition Date</dt>
              <dd className="text-gray-900">
                <DateDisplay date={collection.exhibitionDate} format="long" />
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Views</dt>
              <dd className="text-gray-900">{collection.views}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500">Likes</dt>
              <dd className="text-gray-900">{collection.likes}</dd>
            </div>
          </dl>
        </div>

        <div>
          <h2 className="text-xl font-bold mb-6">Artworks in this collection</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {collection.photos?.map((photo) => (
              <PhotoCard
                key={photo.id}
                photo={photo}
                onClick={() => router.push(`/photos/${photo.id}`)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 