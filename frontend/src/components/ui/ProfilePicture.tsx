import Image from 'next/image';

interface ProfilePictureProps {
  imageUrl: string | null;
  alt: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'w-10 h-10',
  md: 'w-14 h-14',
  lg: 'w-16 h-16'
};

const textSizeClasses = {
  sm: 'text-lg',
  md: 'text-xl',
  lg: 'text-2xl'
};

export default function ProfilePicture({ 
  imageUrl, 
  alt, 
  size = 'md',
  className = ''
}: ProfilePictureProps) {
  return (
    <div className={`relative ${sizeClasses[size]} overflow-hidden border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] ${className}`}>
      {imageUrl ? (
        <Image
          src={imageUrl}
          alt={alt}
          fill
          className="object-cover"
          unoptimized
        />
      ) : (
        <div className="w-full h-full bg-white flex items-center justify-center">
          <span className={`text-black ${textSizeClasses[size]} font-medium`}>
            {alt.charAt(0).toUpperCase()}
          </span>
        </div>
      )}
    </div>
  );
} 