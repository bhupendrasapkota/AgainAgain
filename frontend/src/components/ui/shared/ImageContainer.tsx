'use client';

import Image from 'next/image';
import { useState } from 'react';

interface ImageContainerProps {
  src: string;
  alt: string;
  aspectRatio?: 'square' | '4/3';
  children?: React.ReactNode;
  onHoverChange?: (isHovered: boolean) => void;
}

export function ImageContainer({
  src,
  alt,
  aspectRatio = 'square',
  children,
  onHoverChange
}: ImageContainerProps) {
  const [isHovered, setIsHovered] = useState(false);

  const handleHoverChange = (hovered: boolean) => {
    setIsHovered(hovered);
    onHoverChange?.(hovered);
  };

  const aspectRatioClasses = {
    'square': 'aspect-square',
    '4/3': 'aspect-[4/3]'
  };

  return (
    <div 
      className="relative overflow-hidden"
      onMouseEnter={() => handleHoverChange(true)}
      onMouseLeave={() => handleHoverChange(false)}
    >
      <div className={aspectRatioClasses[aspectRatio]}>
        <Image
          src={src}
          alt={alt}
          fill
          className={`object-cover transition-transform duration-700 ${
            isHovered ? 'scale-110' : 'scale-100'
          }`}
        />
      </div>
      
      {/* Gradient Overlays */}
      <div className={`absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent transition-opacity duration-500 ${
        isHovered ? 'opacity-100' : 'opacity-0'
      }`} />
      <div className={`absolute inset-0 bg-gradient-to-b from-black/20 to-transparent transition-opacity duration-500 ${
        isHovered ? 'opacity-100' : 'opacity-0'
      }`} />
      
      {/* Content Overlay */}
      <div className={`absolute inset-0 transition-all duration-500 ${
        isHovered ? 'opacity-100' : 'opacity-0'
      }`}>
        {children}
      </div>
    </div>
  );
} 