import { useState, useEffect } from 'react';
import Image from 'next/image';

interface CreateCollectionFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (collection: {
    title: string;
    description: string;
    coverImage: string;
    exhibitionDate?: string;
    location?: string;
    type: 'solo' | 'group';
  }) => void;
}

export default function CreateCollectionForm({ isOpen, onClose, onSubmit }: CreateCollectionFormProps) {
  const [mounted, setMounted] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setMounted(true);
      // Small delay to ensure mount happens before animation
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsAnimating(true);
        });
      });
    } else {
      setIsAnimating(false);
      const timer = setTimeout(() => setMounted(false), 500);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    coverImage: '',
    exhibitionDate: '',
    location: '',
    type: 'solo' as 'solo' | 'group'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (!mounted) return null;

  return (
    <>
      <div 
        className={`fixed inset-0 bg-black transition-opacity duration-500 ${
          isAnimating ? 'opacity-50' : 'opacity-0'
        } z-[39]`}
        onClick={onClose}
      />
      <div 
        className={`fixed top-[64px] right-0 w-[1400px] h-[calc(100vh-64px)] bg-white transform transition-transform duration-500 ease-in-out shadow-lg ${
          isAnimating ? 'translate-x-0' : 'translate-x-full'
        } z-[40] overflow-y-auto`}
      >
        <div className="p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Create Collection</h2>
            <button 
              onClick={onClose}
              className="text-2xl hover:text-gray-600 transition-colors duration-200"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-8">
              {/* Left Column */}
              <div className="space-y-6">
                {/* Cover Image Upload */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Cover Image</h3>
                  <div className="flex items-start gap-8">
                    <div className="relative w-48 h-48 border-2 border-gray-300 flex items-center justify-center overflow-hidden group">
                      {formData.coverImage ? (
                        <>
                          <Image
                            src={formData.coverImage}
                            alt="Cover preview"
                            fill
                            className="object-cover"
                          />
                          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center">
                            <span className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">Change Image</span>
                          </div>
                        </>
                      ) : (
                        <div className="flex flex-col items-center justify-center text-gray-400">
                          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span className="text-sm mt-2">No image</span>
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <label className="block text-sm font-medium mb-3">Upload Cover Image</label>
                      <div className="relative">
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          id="cover-image"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              // TODO: Implement file upload logic
                              setFormData(prev => ({
                                ...prev,
                                coverImage: URL.createObjectURL(file)
                              }));
                            }
                          }}
                        />
                        <label
                          htmlFor="cover-image"
                          className="block w-full px-6 py-4 border-2 border-dashed border-gray-300 text-center cursor-pointer hover:border-black transition-colors duration-300"
                        >
                          <div className="flex flex-col items-center gap-3">
                            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <span className="text-sm text-gray-600">Drag and drop your image here</span>
                            <span className="text-xs text-gray-400">or click to browse</span>
                          </div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Basic Information */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Title</label>
                      <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Description</label>
                      <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        required
                        rows={4}
                        className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-6">
                {/* Exhibition Details */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Exhibition Details</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Exhibition Type</label>
                      <select
                        name="type"
                        value={formData.type}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      >
                        <option value="solo">Solo Exhibition</option>
                        <option value="group">Group Exhibition</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Exhibition Date</label>
                      <input
                        type="date"
                        name="exhibitionDate"
                        value={formData.exhibitionDate}
                        onChange={handleChange}
                        className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Location</label>
                      <input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleChange}
                        className="w-full px-4 py-2.5 border border-gray-300 focus:outline-none focus:border-black text-sm"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex justify-end gap-4 pt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-8 py-2.5 border border-gray-300 hover:border-black transition-all duration-300 text-sm"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-8 py-2.5 bg-black text-white hover:bg-white hover:text-black border-2 border-black transition-all duration-300 text-sm"
              >
                Create Collection
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
} 