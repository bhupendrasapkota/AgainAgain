import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import  Navbar  from '@/components/layout/Navbar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Art Show Experience',
  description: 'Discover and showcase contemporary art exhibitions',
};

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen w-full">
          <Navbar />
          <main className="pt-[80px] w-full">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
