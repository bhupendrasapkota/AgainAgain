'use client';

import { useState } from 'react';
import { ImageContainer } from '../shared/ImageContainer';
import { ActionButton } from '../shared/ActionButton';
import { DateDisplay } from '../shared/DateDisplay';
import Icon from '../shared/Icon';
import { DescriptionToggle } from '../shared/DescriptionToggle';

interface PhotoCardProps {
  title: string;
  photographer?: string;
  downloads: number;
  uploadedAt: string;
  imageUrl?: string;
  onView?: () => void;
  onDownload?: () => void;
  onLike?: () => void;
  isLiked?: boolean;
  likes?: number;
  onShare?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  isOwner?: boolean;
  tags?: string[];
  description?: string;
}

export default function PhotoCard({
  title,
  photographer,
  downloads,
  uploadedAt,
  imageUrl = '/placeholder-photo.jpg',
  onView,
  onDownload,
  onLike,
  isLiked = false,
  likes = 0,
  onShare,
  onEdit,
  onDelete,
  isOwner = false,
  tags = [],
  description
}: PhotoCardProps) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div 
      className="group relative bg-white border border-gray-200 overflow-hidden transition-all duration-500 hover:border-black hover:shadow-2xl hover:-translate-y-1"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <ImageContainer
        src={imageUrl}
        alt={title}
        aspectRatio="square"
      >
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
          <button 
            onClick={onView}
            className="bg-white text-black px-8 py-3 font-medium transform -translate-y-4 group-hover:translate-y-0 transition-all duration-500 hover:bg-black hover:text-white hover:shadow-lg"
          >
            View Photo
          </button>
          <button 
            onClick={onDownload}
            className="bg-white text-black px-6 py-2 font-medium transform translate-y-4 group-hover:translate-y-0 transition-all duration-500 hover:bg-black hover:text-white hover:shadow-lg"
          >
            Download
          </button>
        </div>

        {/* Tags Overlay */}
        {tags.length > 0 && (
          <div className="absolute bottom-4 left-4 flex flex-wrap gap-2">
            {tags.map((tag, index) => (
              <span 
                key={index}
                className="bg-white/90 text-black px-2 py-1 text-xs font-medium"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Quick Actions Menu */}
        <div 
          className={`absolute top-3 right-3 flex flex-col gap-2 transition-all duration-300 ${
            showActions ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'
          }`}
        >
          <ActionButton
            icon={<Icon name="heart" size="sm" fill={isLiked ? "currentColor" : "none"} />}
            onClick={onLike}
            variant="like"
            isActive={isLiked}
            size="sm"
          />
          <ActionButton
            icon={<Icon name="share" size="sm" />}
            onClick={onShare}
            size="sm"
          />
        </div>
      </ImageContainer>

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold group-hover:text-black transition-colors duration-300">
              {title}
            </h3>
            {photographer && (
              <p className="text-sm text-gray-500">By {photographer}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <ActionButton
              icon={<Icon name="heart" fill={isLiked ? "currentColor" : "none"} />}
              onClick={onLike}
              variant="like"
              isActive={isLiked}
            />
            <ActionButton
              icon={<Icon name="share" />}
              onClick={onShare}
            />
          </div>
        </div>
        
        {/* Description Toggle */}
        {description && (
          <DescriptionToggle description={description} />
        )}
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Icon name="download" size="sm" />
              {downloads}
            </span>
            <span className="flex items-center gap-1">
              <Icon name="heart" size="sm" />
              {likes}
            </span>
            <DateDisplay date={uploadedAt} format="relative" />
          </div>
          {isOwner && (
            <div className="flex items-center gap-2">
              {onEdit && (
                <ActionButton
                  icon={<Icon name="edit" size="sm" />}
                  onClick={onEdit}
                  size="sm"
                />
              )}
              {onDelete && (
                <ActionButton
                  icon={<Icon name="delete" size="sm" />}
                  onClick={onDelete}
                  variant="danger"
                  size="sm"
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 