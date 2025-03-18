'use client';

import { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

interface ActionButtonProps {
  icon: ReactNode;
  onClick: () => void;
  variant?: 'default' | 'like';
  isActive?: boolean;
  className?: string;
}

export function ActionButton({
  icon,
  onClick,
  variant = 'default',
  isActive = false,
  className,
}: ActionButtonProps) {
  const baseClasses = 'p-2 rounded-full transition-colors duration-200 ease-in-out';
  const variantClasses = {
    default: 'hover:bg-gray-100 text-gray-700 hover:text-gray-900',
    like: twMerge(
      'hover:bg-red-100 text-gray-700 hover:text-red-600',
      isActive && 'bg-red-100 text-red-600'
    ),
  };

  return (
    <button
      onClick={onClick}
      className={twMerge(
        baseClasses,
        variantClasses[variant],
        className
      )}
    >
      {icon}
    </button>
  );
} 