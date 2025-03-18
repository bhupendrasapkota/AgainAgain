'use client';

import { useState } from 'react';
import Icon from './Icon';

interface DescriptionToggleProps {
  description: string;
  className?: string;
}

export function DescriptionToggle({ description, className = '' }: DescriptionToggleProps) {
  const [showDescription, setShowDescription] = useState(false);

  return (
    <div className={`mb-3 ${className}`}>
      <button
        onClick={() => setShowDescription(!showDescription)}
        className="text-sm text-gray-500 hover:text-black transition-colors duration-300 flex items-center gap-1"
      >
        <Icon 
          name="chevron-down" 
          size="sm" 
          className={`transition-transform duration-300 ${showDescription ? 'rotate-180' : ''}`}
        />
        {showDescription ? 'Hide Description' : 'Show Description'}
      </button>
      {showDescription && (
        <p className="mt-2 text-sm text-gray-600">{description}</p>
      )}
    </div>
  );
} 