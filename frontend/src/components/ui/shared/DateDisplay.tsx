'use client';

interface DateDisplayProps {
  date: string;
  format?: 'relative' | 'short' | 'full';
  className?: string;
  showIcon?: boolean;
}

export function DateDisplay({
  date,
  format = 'short',
  className = '',
  showIcon = true
}: DateDisplayProps) {
  const formatDate = (dateString: string, format: 'relative' | 'short' | 'full') => {
    const inputDate = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - inputDate.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (format === 'relative') {
      if (days === 0) return 'Today';
      if (days === 1) return 'Yesterday';
      if (days < 7) return `${days} days ago`;
      return inputDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    if (format === 'short') {
      return inputDate.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric'
      });
    }

    return inputDate.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const CalendarIcon = () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );

  return (
    <div className={`flex items-center gap-2 text-sm text-gray-500 ${className}`}>
      {showIcon && <CalendarIcon />}
      <span>{formatDate(date, format)}</span>
    </div>
  );
} 