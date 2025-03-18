'use client';

import { Collection } from '@/types';
import CollectionCard from './CollectionCard';
import { ActionButton } from '../shared/ActionButton';
import Icon from '../shared/Icon';

interface CollectionsGridProps {
  collections: Collection[];
  onCreateCollection?: () => void;
  onViewCollection?: (id: string) => void;
  onEditCollection?: (id: string) => void;
  onDeleteCollection?: (id: string) => void;
  isOwner?: boolean;
}

export function CollectionsGrid({
  collections,
  onCreateCollection,
  onViewCollection,
  onEditCollection,
  onDeleteCollection,
  isOwner = false
}: CollectionsGridProps) {
  return (
    <div className="w-full">
      <div className="max-w-[auto] mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Collections</h2>
          {isOwner && (
            <button 
              onClick={onCreateCollection}
              className="bg-black text-white px-4 py-2 text-sm font-medium border-2 border-black hover:bg-white hover:text-black transition-all duration-300 flex items-center gap-2"
            >
              <Icon name="plus" size="sm" />
              Create Collection
            </button>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((collection) => (
            <CollectionCard
              key={collection.id}
              {...collection}
              onView={() => onViewCollection?.(collection.id)}
              onEdit={() => onEditCollection?.(collection.id)}
              onDelete={() => onDeleteCollection?.(collection.id)}
              isOwner={isOwner}
            />
          ))}
        </div>
      </div>
    </div>
  );
} 