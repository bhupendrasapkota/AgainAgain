'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';

interface Category {
  id: string;
  name: string;
  description: string;
  coverImage: string;
  artworkCount: number;
  curator: string;
  lastUpdated: string;
  tags: string[];
  likes: number;
  views: number;
  isLiked: boolean;
  featuredArtworks: {
    id: string;
    title: string;
    artist: string;
    imageUrl: string;
    likes: number;
  }[];
}

export default function CategoriesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'recent' | 'popular' | 'trending'>('recent');

  // Sample categories data
  const categories: Category[] = [
    {
      id: 'contemporary',
      name: 'Contemporary Art',
      description: 'Explore the cutting-edge world of contemporary art, featuring works from today\'s most innovative artists.',
      coverImage: '/contemporary-art.jpg',
      artworkCount: 234,
      curator: 'Dr. Emily Thompson',
      lastUpdated: '2024-03-15',
      tags: ['modern', 'contemporary', 'installation'],
      likes: 1234,
      views: 5678,
      isLiked: false,
      featuredArtworks: [
        {
          id: '1',
          title: 'Abstract Harmony',
          artist: 'Sarah Chen',
          imageUrl: '/artwork1.jpg',
          likes: 123
        },
        {
          id: '2',
          title: 'Digital Dreams',
          artist: 'Alex Rivera',
          imageUrl: '/artwork2.jpg',
          likes: 89
        }
      ]
    },
    {
      id: 'modern',
      name: 'Modern Art',
      description: 'Journey through the revolutionary movements of modern art, from Impressionism to Abstract Expressionism.',
      coverImage: '/modern-art.jpg',
      artworkCount: 156,
      curator: 'James Wilson',
      lastUpdated: '2024-03-14',
      tags: ['modern', 'impressionism', 'expressionism'],
      likes: 987,
      views: 4321,
      isLiked: true,
      featuredArtworks: [
        {
          id: '3',
          title: 'Color Theory',
          artist: 'Maria Garcia',
          imageUrl: '/artwork3.jpg',
          likes: 156
        },
        {
          id: '4',
          title: 'Urban Landscape',
          artist: 'David Kim',
          imageUrl: '/artwork4.jpg',
          likes: 92
        }
      ]
    },
    {
      id: 'classical',
      name: 'Classical Art',
      description: 'Discover the timeless masterpieces of classical art, from ancient sculptures to Renaissance paintings.',
      coverImage: '/classical-art.jpg',
      artworkCount: 89,
      curator: 'Prof. Michael Brown',
      lastUpdated: '2024-03-13',
      tags: ['classical', 'renaissance', 'sculpture'],
      likes: 765,
      views: 3456,
      isLiked: false,
      featuredArtworks: [
        {
          id: '5',
          title: 'Venus Rising',
          artist: 'Ancient Master',
          imageUrl: '/artwork5.jpg',
          likes: 234
        },
        {
          id: '6',
          title: 'The Last Supper',
          artist: 'Leonardo da Vinci',
          imageUrl: '/artwork6.jpg',
          likes: 567
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="w-full bg-black text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/90 z-10" />
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[url('/art-categories-hero.jpg')] bg-cover bg-center animate-ken-burns" />
        </div>
        <div className="relative z-20 py-32">
          <div className="max-w-[1500px] mx-auto px-4">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="text-6xl font-bold mb-8 leading-tight"
            >
              Explore Art Categories
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1, ease: "easeOut" }}
              className="text-xl text-white/80 mb-12 max-w-2xl"
            >
              Discover diverse artistic movements, styles, and periods. From classical masterpieces to contemporary innovations.
            </motion.p>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2, ease: "easeOut" }}
              className="flex gap-4 max-w-2xl"
            >
              <div className="flex-1 relative group">
                <input
                  type="text"
                  placeholder="Search categories, movements, or styles..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-6 py-4 bg-white/5 text-white placeholder-white/40 focus:outline-none group-hover:bg-white/10 transition-all duration-300"
                />
                <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40 group-hover:text-white/80 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Categories Bar */}
      <div className="sticky top-0 z-30 bg-white border-b">
        <div className="max-w-[1500px] mx-auto px-4">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 transition-all duration-300 ${
                    viewMode === 'grid' ? 'text-black' : 'text-black/40 hover:text-black'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 transition-all duration-300 ${
                    viewMode === 'list' ? 'text-black' : 'text-black/40 hover:text-black'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'recent' | 'popular' | 'trending')}
                className="px-4 py-2 border border-gray-200 focus:outline-none focus:border-black transition-colors duration-200"
              >
                <option value="recent">Most Recent</option>
                <option value="popular">Most Popular</option>
                <option value="trending">Trending</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Categories Display */}
      <div className="max-w-[1500px] mx-auto px-4 py-12">
        <div className={`grid gap-8 ${
          viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'
        }`}>
          {categories.map((category) => (
            <motion.div
              key={category.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`group relative overflow-hidden ${
                viewMode === 'list' ? 'flex gap-8' : ''
              }`}
            >
              <div className={`relative overflow-hidden ${
                viewMode === 'list' ? 'w-1/3' : 'aspect-[4/3]'
              }`}>
                <Image
                  src={category.coverImage}
                  alt={category.name}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
              <div className={`p-6 ${
                viewMode === 'list' ? 'flex-1' : 'absolute bottom-0 left-0 right-0'
              }`}>
                <h3 className="text-2xl font-bold text-white mb-2">{category.name}</h3>
                <p className="text-white/80 text-sm mb-4">{category.description}</p>
                <div className="flex items-center justify-between text-sm text-white/60">
                  <span>Curated by {category.curator}</span>
                  <span>{category.artworkCount} artworks</span>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {category.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 text-xs font-medium text-white/80 bg-white/10 hover:bg-white/20 transition-colors duration-200"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="mt-4 flex items-center gap-4 text-sm text-white/60">
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    {category.likes}
                  </span>
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {category.views}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
} 