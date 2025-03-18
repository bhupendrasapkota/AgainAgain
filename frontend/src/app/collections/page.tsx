'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';

interface Exhibition {
  id: string;
  title: string;
  description: string;
  coverImage: string;
  artworkCount: number;
  curator: {
    name: string;
    role: string;
  };
  exhibitionDate: string;
  location: string;
  tags: string[];
  likes: number;
  views: number;
  isLiked: boolean;
  featuredArtworks: {
    id: string;
    title: string;
    artist: string;
    imageUrl: string;
  }[];
}

export default function CollectionsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'recent' | 'popular' | 'trending'>('recent');
  const [isLoading, setIsLoading] = useState(true);

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Sample exhibitions data
  const exhibitions: Exhibition[] = [
    {
      id: "1",
      title: "Contemporary Masters",
      description: "A groundbreaking exhibition showcasing the works of leading contemporary artists from around the world.",
      coverImage: "/exhibition-1.jpg",
      artworkCount: 45,
      curator: {
        name: "Sarah Johnson",
        role: "Senior Curator"
      },
      exhibitionDate: "2024-04-15",
      location: "Modern Art Gallery, New York",
      tags: ["contemporary", "modern", "international"],
      likes: 234,
      views: 1234,
      isLiked: false,
      featuredArtworks: [
        {
          id: "1",
          title: "Abstract Harmony",
          artist: "Michael Chen",
          imageUrl: "/artwork-1.jpg"
        },
        {
          id: "2",
          title: "Digital Dreams",
          artist: "Emma Rodriguez",
          imageUrl: "/artwork-2.jpg"
        }
      ]
    },
    {
      id: "2",
      title: "Renaissance Revisited",
      description: "A modern interpretation of classical Renaissance art, featuring contemporary artists' takes on iconic masterpieces.",
      coverImage: "/exhibition-2.jpg",
      artworkCount: 30,
      curator: {
        name: "David Thompson",
        role: "Art History Professor"
      },
      exhibitionDate: "2024-05-01",
      location: "Classical Museum, London",
      tags: ["renaissance", "classical", "historical"],
      likes: 189,
      views: 856,
      isLiked: true,
      featuredArtworks: [
        {
          id: "3",
          title: "Modern Mona Lisa",
          artist: "Sophie Anderson",
          imageUrl: "/artwork-3.jpg"
        },
        {
          id: "4",
          title: "Digital David",
          artist: "James Wilson",
          imageUrl: "/artwork-4.jpg"
        }
      ]
    },
    {
      id: "3",
      title: "Digital Frontiers",
      description: "Exploring the intersection of technology and art through immersive digital installations and interactive experiences.",
      coverImage: "/exhibition-3.jpg",
      artworkCount: 25,
      curator: {
        name: "Lisa Chen",
        role: "Digital Art Curator"
      },
      exhibitionDate: "2024-05-15",
      location: "Tech Art Center, San Francisco",
      tags: ["digital", "interactive", "technology"],
      likes: 312,
      views: 1567,
      isLiked: false,
      featuredArtworks: [
        {
          id: "5",
          title: "Virtual Reality",
          artist: "Alex Kumar",
          imageUrl: "/artwork-5.jpg"
        },
        {
          id: "6",
          title: "AI Dreams",
          artist: "Nina Patel",
          imageUrl: "/artwork-6.jpg"
        }
      ]
    },
    {
      id: "4",
      title: "Sculpture Garden",
      description: "An outdoor exhibition featuring contemporary sculptures in a natural setting, creating a dialogue between art and environment.",
      coverImage: "/exhibition-4.jpg",
      artworkCount: 20,
      curator: {
        name: "Robert Martinez",
        role: "Sculpture Specialist"
      },
      exhibitionDate: "2024-06-01",
      location: "Botanical Gardens, Chicago",
      tags: ["sculpture", "outdoor", "contemporary"],
      likes: 278,
      views: 945,
      isLiked: false,
      featuredArtworks: [
        {
          id: "7",
          title: "Metal Flow",
          artist: "Carlos Rivera",
          imageUrl: "/artwork-7.jpg"
        },
        {
          id: "8",
          title: "Stone Harmony",
          artist: "Maria Garcia",
          imageUrl: "/artwork-8.jpg"
        }
      ]
    }
  ];

  const categories = [
    { name: 'Contemporary', count: 12 },
    { name: 'Classical', count: 8 },
    { name: 'Digital', count: 6 },
    { name: 'Sculpture', count: 4 },
    { name: 'Photography', count: 5 },
    { name: 'Mixed Media', count: 7 }
  ];

  const filteredExhibitions = exhibitions.filter(exhibition => {
    const matchesSearch = exhibition.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      exhibition.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      exhibition.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = !selectedCategory || exhibition.tags.includes(selectedCategory.toLowerCase());
    return matchesSearch && matchesCategory;
  });

  const sortedExhibitions = [...filteredExhibitions].sort((a, b) => {
    switch (sortBy) {
      case 'popular':
        return b.likes - a.likes;
      case 'trending':
        return b.views - a.views;
      default:
        return new Date(b.exhibitionDate).getTime() - new Date(a.exhibitionDate).getTime();
    }
  });

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative h-[400px] bg-black">
        <div className="absolute inset-0">
          <Image
            src="/exhibition-hero.jpg"
            alt="Art Exhibitions"
            fill
            className="object-cover opacity-50"
          />
        </div>
        <div className="relative max-w-[1500px] mx-auto px-4 h-full flex flex-col justify-center">
          <h1 className="text-6xl font-bold text-white mb-6">Art Exhibitions</h1>
          <p className="text-xl text-gray-300 max-w-2xl">
            Discover and explore curated art exhibitions from around the world. From contemporary masterpieces to classical collections.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1500px] mx-auto px-4 py-12">
        {/* Search and Create */}
        <div className="flex justify-between items-center mb-8">
          <div className="relative w-[400px]">
            <input
              type="text"
              placeholder="Search exhibitions, artists, or locations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 pl-12 border border-gray-300 focus:outline-none focus:border-black"
            />
            <svg
              className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <button className="bg-black text-white px-8 py-3 hover:bg-gray-900 transition-colors">
            Create Exhibition
          </button>
        </div>

        {/* Categories Bar */}
        <div className="flex gap-4 mb-8 overflow-x-auto pb-4">
          {categories.map((category) => (
            <button
              key={category.name}
              onClick={() => setSelectedCategory(selectedCategory === category.name ? null : category.name)}
              className={`px-6 py-2 rounded-full whitespace-nowrap ${
                selectedCategory === category.name
                  ? 'bg-black text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.name} ({category.count})
            </button>
          ))}
        </div>

        {/* View Options */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex gap-4">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 ${
                viewMode === 'grid'
                  ? 'bg-black text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Grid View
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 ${
                viewMode === 'list'
                  ? 'bg-black text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              List View
            </button>
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'recent' | 'popular' | 'trending')}
            className="px-4 py-2 border border-gray-300 focus:outline-none focus:border-black"
          >
            <option value="recent">Most Recent</option>
            <option value="popular">Most Popular</option>
            <option value="trending">Trending</option>
          </select>
        </div>

        {/* Exhibitions Grid/List */}
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8' : 'space-y-6'}>
          {sortedExhibitions.map((exhibition) => (
            <motion.div
              key={exhibition.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`bg-white border border-gray-200 overflow-hidden ${
                viewMode === 'grid' ? 'rounded-lg' : 'rounded-lg flex'
              }`}
            >
              <div className={`relative ${viewMode === 'grid' ? 'h-64' : 'w-64 h-64'}`}>
                <Image
                  src={exhibition.coverImage}
                  alt={exhibition.title}
                  fill
                  className="object-cover"
                />
              </div>
              <div className={`p-6 ${viewMode === 'list' ? 'flex-1' : ''}`}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold mb-2">{exhibition.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">
                      Curated by {exhibition.curator.name} • {exhibition.curator.role}
                    </p>
                    <p className="text-gray-600 text-sm">
                      {new Date(exhibition.exhibitionDate).toLocaleDateString()} • {exhibition.location}
                    </p>
                  </div>
                  <button
                    className={`p-2 ${
                      exhibition.isLiked
                        ? 'text-red-500'
                        : 'text-gray-400 hover:text-red-500'
                    }`}
                  >
                    <svg
                      className="w-6 h-6"
                      fill={exhibition.isLiked ? 'currentColor' : 'none'}
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                      />
                    </svg>
                  </button>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-2">{exhibition.description}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {exhibition.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>{exhibition.artworkCount} artworks</span>
                  <div className="flex items-center gap-4">
                    <span>{exhibition.likes} likes</span>
                    <span>{exhibition.views} views</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
} 