'use client';

import { useState, useEffect } from 'react';
import { motion, useScroll } from 'framer-motion';
import Image from 'next/image';
import { Photo, Collection, Category } from '@/types';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollY } = useScroll();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(scrollY.get() > 50);
    };

    const unsubscribe = scrollY.on('change', handleScroll);
    return () => unsubscribe();
  }, [scrollY]);

  // Sample categories data
  const categories: Category[] = [
    { id: 'contemporary', name: 'Contemporary', count: 234 },
    { id: 'modern', name: 'Modern', count: 156 },
    { id: 'classical', name: 'Classical', count: 89 },
    { id: 'digital', name: 'Digital Art', count: 167 },
    { id: 'sculpture', name: 'Sculpture', count: 92 },
    { id: 'painting', name: 'Painting', count: 345 },
    { id: 'photography', name: 'Photography', count: 278 },
    { id: 'installation', name: 'Installation', count: 45 }
  ];

  // Sample artworks data
  const artworks: Photo[] = [
    {
      id: '1',
      title: 'Abstract Harmony',
      artist: 'Sarah Chen',
      likes: 1234,
      views: 5678,
      tags: ['abstract', 'contemporary', 'painting'],
      description: 'A mesmerizing exploration of color and form in contemporary art.',
      imageUrl: '/artwork1.jpg',
      medium: 'Oil on Canvas',
      year: '2024',
      featured: true
    },
    {
      id: '2',
      title: 'Digital Dreams',
      artist: 'Alex Rivera',
      likes: 856,
      views: 3421,
      tags: ['digital', 'surreal', 'technology'],
      description: 'A fusion of technology and artistic expression.',
      imageUrl: '/artwork2.jpg',
      medium: 'Digital Art',
      year: '2024',
      featured: true
    },
    // Add more sample artworks...
  ];

  // Sample collections data
  const collections: Collection[] = [
    {
      id: '1',
      title: 'Contemporary Masters',
      description: 'A showcase of the most influential contemporary artists of our time.',
      curator: 'Dr. Emily Thompson',
      artworkCount: 45,
      coverImage: '/collection1.jpg',
      likes: 2345,
      views: 12345,
      isLiked: false,
      exhibitionDate: '2024-04-15',
      location: 'Modern Art Gallery'
    },
    {
      id: '2',
      title: 'Digital Revolution',
      description: 'Exploring the intersection of technology and artistic expression.',
      curator: 'James Wilson',
      artworkCount: 32,
      coverImage: '/collection2.jpg',
      likes: 1876,
      views: 9876,
      isLiked: true,
      exhibitionDate: '2024-05-01',
      location: 'Digital Arts Center'
    },
    // Add more sample collections...
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="w-full h-screen bg-black text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/90 z-10" />
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[url('/art-show-hero.jpg')] bg-cover bg-center animate-ken-burns" />
        </div>
        <div className="relative z-20 h-full flex items-center">
          <div className="max-w-[1500px] mx-auto px-4">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="text-7xl font-bold mb-8 leading-tight"
            >
              Discover the World&apos;s Most<br />
              <span className="text-white">
                Extraordinary Art
              </span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1, ease: "easeOut" }}
              className="text-2xl text-white/80 mb-12 max-w-2xl"
            >
              Immerse yourself in a world of artistic excellence. Explore exhibitions, 
              discover emerging artists, and experience the transformative power of art.
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
                  placeholder="Search artworks, artists, or exhibitions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-6 py-4 bg-white/5 text-white placeholder-white/40 focus:outline-none group-hover:bg-white/10 transition-all duration-300"
                />
                <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40 group-hover:text-white/80 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <button className="px-8 py-4 bg-white text-black hover:bg-black hover:text-white transition-all duration-300">
                Explore Art
              </button>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Categories Bar */}
      <div className={`sticky top-0 z-30 bg-white border-b transition-all duration-300 ${
        isScrolled ? 'shadow-md' : ''
      }`}>
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
          </div>
        </div>
      </div>

      {/* Featured Collections */}
      <div className="w-full bg-black text-white py-24">
        <div className="max-w-[1500px] mx-auto px-4">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-4xl font-bold mb-4">Featured Exhibitions</h2>
              <p className="text-xl text-white/60">Discover the most anticipated art exhibitions</p>
            </div>
            <button className="px-6 py-2 text-sm font-medium text-white/60 hover:text-white transition-colors duration-200">
              View All Exhibitions
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {collections.map((collection) => (
              <motion.div
                key={collection.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3 }}
                className="group relative overflow-hidden"
              >
                <div className="aspect-[4/3] relative overflow-hidden">
                  <Image
                    src={collection.coverImage}
                    alt={collection.title}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
                <div className="absolute bottom-0 left-0 right-0 p-6 transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
                  <h3 className="text-xl font-bold mb-2">{collection.title}</h3>
                  <p className="text-white/80 text-sm mb-4">{collection.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/60">Curated by {collection.curator}</span>
                    <span className="text-white/60">{collection.artworkCount} artworks</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Latest Artworks */}
      <div className="w-full py-24">
        <div className="max-w-[1500px] mx-auto px-4">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-4xl font-bold mb-4">Latest Artworks</h2>
              <p className="text-xl text-black/60">Explore the newest additions to our collection</p>
            </div>
            <button className="px-6 py-2 text-sm font-medium text-black/60 hover:text-black transition-colors duration-200">
              View All Artworks
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {artworks.map((artwork) => (
              <motion.div
                key={artwork.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3 }}
                className="group"
              >
                <div className="aspect-square relative overflow-hidden mb-4">
                  <Image
                    src={artwork.imageUrl}
                    alt={artwork.title}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
                <h3 className="text-xl font-bold mb-2">{artwork.title}</h3>
                <p className="text-black/60 mb-4">by {artwork.artist}</p>
                <div className="flex items-center gap-4 text-sm text-black/40">
                  <span>{artwork.medium}</span>
                  <span>•</span>
                  <span>{artwork.year}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Newsletter Section */}
      <div className="w-full bg-black text-white py-24">
        <div className="max-w-[1500px] mx-auto px-4">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6">Stay Updated</h2>
            <p className="text-xl text-white/60 mb-8">
              Subscribe to our newsletter for the latest exhibitions, artist features, and art world insights.
            </p>
            <div className="flex gap-4">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-6 py-4 bg-white/5 text-white placeholder-white/40 focus:outline-none"
              />
              <button className="px-8 py-4 bg-white text-black hover:bg-black hover:text-white transition-all duration-300">
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
