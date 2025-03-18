'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';

interface Filter {
  category: string;
  medium: string;
  style: string;
  sortBy: string;
  price: string;
  availability: string;
  year: string;
}

interface Category {
  id: string;
  name: string;
  icon: string;
  count: number;
}

export default function ArtworksPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Filter>({
    category: 'all',
    medium: 'all',
    style: 'all',
    sortBy: 'newest',
    price: 'all',
    availability: 'all',
    year: 'all'
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'masonry'>('grid');

  // Sample categories data
  const categories: Category[] = [
    { id: 'contemporary', name: 'Contemporary', icon: '🎨', count: 1234 },
    { id: 'modern', name: 'Modern', icon: '🖼️', count: 856 },
    { id: 'classical', name: 'Classical', icon: '🏛️', count: 2341 },
    { id: 'digital', name: 'Digital Art', icon: '💻', count: 567 },
    { id: 'sculpture', name: 'Sculpture', icon: '🗿', count: 789 },
    { id: 'painting', name: 'Painting', icon: '🖌️', count: 1456 },
  ];

  // Sample artworks data
  const artworks = [
    {
      id: '1',
      title: 'Abstract Harmony',
      artist: 'Sarah Chen',
      likes: 1234,
      views: 5678,
      imageUrl: '/artwork1.jpg',
      tags: ['abstract', 'contemporary', 'painting'],
      description: 'A mesmerizing exploration of color and form in contemporary art.',
      medium: 'Oil on Canvas',
      year: '2024',
      price: 12000,
      availability: 'Available',
      style: 'Abstract Expressionism'
    },
    {
      id: '2',
      title: 'Digital Dreams',
      artist: 'Alex Rivera',
      likes: 856,
      views: 3421,
      imageUrl: '/artwork2.jpg',
      tags: ['digital', 'surreal', 'technology'],
      description: 'A fusion of technology and artistic expression.',
      medium: 'Digital Art',
      year: '2024',
      price: 8000,
      availability: 'Available',
      style: 'Digital Art'
    },
    // Add more sample artworks...
  ];

  // Simulate loading state
  useEffect(() => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1500);
  }, [filters, searchQuery]);

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section with Dynamic Background */}
      <div className="w-full bg-black text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/90 z-10" />
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[url('/artworks-hero.jpg')] bg-cover bg-center animate-ken-burns" />
        </div>
        <div className="relative z-20 py-32">
          <div className="max-w-[1500px] mx-auto px-4">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="text-6xl font-bold mb-8 leading-tight"
            >
              Discover Extraordinary<br />
              <span className="text-white">
                Artworks
              </span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1, ease: "easeOut" }}
              className="text-xl text-white/80 mb-12 max-w-2xl"
            >
              Explore a curated collection of exceptional artworks from talented artists worldwide.
              Find the perfect piece for your collection or exhibition.
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
                  placeholder="Search artworks, artists, or styles..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-6 py-4 bg-white/5 text-white placeholder-white/40 focus:outline-none group-hover:bg-white/10 transition-all duration-300"
                />
                <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40 group-hover:text-white/80 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="px-6 py-4 bg-white/5 hover:bg-white/10 transition-all duration-300 flex items-center gap-2 group"
              >
                <svg className="w-5 h-5 text-white/40 group-hover:text-white/80 group-hover:rotate-180 transition-all duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                Filters
              </button>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Categories Bar */}
      <div className="sticky top-0 z-30 bg-white border-b">
        <div className="max-w-[1500px] mx-auto px-4">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-8 overflow-x-auto scrollbar-hide">
              {categories.map((category) => (
                <motion.button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center gap-2 px-4 py-2 relative group ${
                    selectedCategory === category.id
                      ? 'text-black'
                      : 'text-black/60 hover:text-black'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  transition={{ duration: 0.2, ease: "easeOut" }}
                >
                  <span className="text-xl transform group-hover:scale-110 transition-transform duration-200">{category.icon}</span>
                  <span className="font-medium whitespace-nowrap">{category.name}</span>
                  <span className="text-sm text-black/40 group-hover:text-black/60 transition-colors duration-200">({category.count})</span>
                  {selectedCategory === category.id && (
                    <motion.div
                      layoutId="activeCategory"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-black"
                      initial={false}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                    />
                  )}
                </motion.button>
              ))}
            </div>
            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 text-sm font-medium text-black/60 hover:text-black transition-colors duration-200 flex items-center gap-2 group"
              >
                <svg className="w-4 h-4 group-hover:rotate-12 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                Favorites
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 text-sm font-medium text-black/60 hover:text-black transition-colors duration-200 flex items-center gap-2 group"
              >
                <svg className="w-4 h-4 group-hover:rotate-12 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Recent
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 text-sm font-medium text-black/60 hover:text-black transition-colors duration-200 flex items-center gap-2 group"
              >
                <svg className="w-4 h-4 group-hover:rotate-12 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Popular
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="w-full bg-white overflow-hidden backdrop-blur-sm bg-white/98"
          >
            <motion.div
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -20, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeOut", delay: 0.1 }}
              className="max-w-[1500px] mx-auto px-4 py-8"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {[
                  { label: 'Category', value: filters.category, options: [
                    { value: 'all', label: 'All Categories' },
                    ...categories.map(cat => ({ value: cat.id, label: cat.name }))
                  ]},
                  { label: 'Medium', value: filters.medium, options: [
                    { value: 'all', label: 'All Mediums' },
                    { value: 'painting', label: 'Painting' },
                    { value: 'sculpture', label: 'Sculpture' },
                    { value: 'digital', label: 'Digital Art' },
                    { value: 'photography', label: 'Photography' },
                    { value: 'mixed', label: 'Mixed Media' }
                  ]},
                  { label: 'Style', value: filters.style, options: [
                    { value: 'all', label: 'All Styles' },
                    { value: 'contemporary', label: 'Contemporary' },
                    { value: 'modern', label: 'Modern' },
                    { value: 'classical', label: 'Classical' },
                    { value: 'abstract', label: 'Abstract' },
                    { value: 'realistic', label: 'Realistic' }
                  ]},
                  { label: 'Price Range', value: filters.price, options: [
                    { value: 'all', label: 'All Prices' },
                    { value: 'under1000', label: 'Under $1,000' },
                    { value: '1000to5000', label: '$1,000 - $5,000' },
                    { value: '5000to10000', label: '$5,000 - $10,000' },
                    { value: 'over10000', label: 'Over $10,000' }
                  ]},
                  { label: 'Availability', value: filters.availability, options: [
                    { value: 'all', label: 'All' },
                    { value: 'available', label: 'Available' },
                    { value: 'sold', label: 'Sold' },
                    { value: 'reserved', label: 'Reserved' }
                  ]},
                  { label: 'Year', value: filters.year, options: [
                    { value: 'all', label: 'All Years' },
                    { value: '2024', label: '2024' },
                    { value: '2023', label: '2023' },
                    { value: '2022', label: '2022' },
                    { value: '2021', label: '2021' }
                  ]},
                  { label: 'Sort By', value: filters.sortBy, options: [
                    { value: 'newest', label: 'Newest First' },
                    { value: 'popular', label: 'Most Popular' },
                    { value: 'trending', label: 'Trending' },
                    { value: 'price_asc', label: 'Price: Low to High' },
                    { value: 'price_desc', label: 'Price: High to Low' }
                  ]}
                ].map((filterGroup, index) => (
                  <motion.div
                    key={filterGroup.label}
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="relative group"
                  >
                    <label className="block text-sm font-medium text-black/80 mb-3">{filterGroup.label}</label>
                    <div className="relative">
                      <select
                        value={filterGroup.value}
                        onChange={(e) => setFilters({ ...filters, [filterGroup.label.toLowerCase()]: e.target.value })}
                        className="w-full px-4 py-3 bg-white focus:outline-none transition-all duration-200 appearance-none cursor-pointer hover:bg-black/5 group-hover:bg-black/5 text-black/80"
                      >
                        {filterGroup.options.map(option => (
                          <option 
                            key={option.value} 
                            value={option.value}
                            className="py-2 bg-white text-black/80"
                          >
                            {option.label}
                          </option>
                        ))}
                      </select>
                      <div className="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
                        <svg 
                          className="w-4 h-4 text-black/30 group-hover:text-black/60 transition-colors duration-200" 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                    <style jsx global>{`
                      select {
                        background-image: none;
                      }
                      select option {
                        padding: 12px;
                        background-color: white;
                        color: rgba(0, 0, 0, 0.8);
                        font-size: 14px;
                        transition: all 0.2s ease;
                      }
                      select option:hover {
                        background-color: rgba(0, 0, 0, 0.03);
                      }
                      select option:checked {
                        background-color: rgba(0, 0, 0, 0.03);
                        color: black;
                        font-weight: 500;
                      }
                      select:focus option:checked {
                        background-color: rgba(0, 0, 0, 0.03);
                      }
                    `}</style>
                  </motion.div>
                ))}
              </div>
              <div className="mt-8 flex justify-end gap-4">
                <button
                  onClick={() => setShowFilters(false)}
                  className="px-6 py-2.5 text-sm font-medium text-black/60 hover:text-black transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    // Reset filters logic here
                    setShowFilters(false);
                  }}
                  className="px-6 py-2.5 text-sm font-medium bg-black text-white hover:bg-black/80 transition-colors duration-200"
                >
                  Apply Filters
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* View Options and Results Count */}
      <div className="max-w-[1500px] mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-black/60">Showing 1-24 of 1,234 results</span>
            <div className="flex items-center gap-2">
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
                onClick={() => setViewMode('masonry')}
                className={`p-2 transition-all duration-300 ${
                  viewMode === 'masonry' ? 'text-black' : 'text-black/40 hover:text-black'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 text-sm font-medium text-black/60 hover:text-black transition-colors duration-300">
              Save Search
            </button>
            <button className="px-4 py-2 text-sm font-medium text-black/60 hover:text-black transition-colors duration-300">
              Share Search
            </button>
          </div>
        </div>
      </div>

      {/* Artworks Grid */}
      <div className="max-w-[1500px] mx-auto px-4 pb-12">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(12)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="aspect-square bg-black/5" />
                <div className="mt-4 h-4 bg-black/5 w-3/4" />
                <div className="mt-2 h-4 bg-black/5 w-1/2" />
              </div>
            ))}
          </div>
        ) : (
          <motion.div
            layout
            className={`grid gap-6 ${
              viewMode === 'grid'
                ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
                : 'columns-1 md:columns-2 lg:columns-3 xl:columns-4'
            }`}
          >
            {artworks.map((artwork) => (
              <motion.div
                key={artwork.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className={viewMode === 'masonry' ? 'mb-6 break-inside-avoid' : ''}
              >
                <div className="group relative overflow-hidden">
                  <div className="aspect-square relative overflow-hidden">
                    <Image
                      src={artwork.imageUrl}
                      alt={artwork.title}
                      fill
                      className="object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-6 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                    <h3 className="text-xl font-bold text-white mb-2">{artwork.title}</h3>
                    <p className="text-white/80 text-sm mb-4">by {artwork.artist}</p>
                    <div className="flex items-center justify-between text-sm text-white/60">
                      <span>{artwork.medium}</span>
                      <span>{artwork.year}</span>
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-medium">${artwork.price.toLocaleString()}</span>
                    <span className={`text-sm ${
                      artwork.availability === 'Available' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {artwork.availability}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-black/40">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                      {artwork.likes}
                    </span>
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      {artwork.views}
                    </span>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {artwork.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 text-xs font-medium text-black/60 bg-black/5 hover:bg-black/10 transition-colors duration-200"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
} 