'use client';

import { useState, useEffect } from 'react';
import LandingPage from '@/components/LandingPage';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [view, setView] = useState<'landing' | 'dashboard'>('landing');

  // Handle hydration - only render content after mount
  useEffect(() => {
    setMounted(true);
  }, []);

  // Simple hash router
  useEffect(() => {
    if (!mounted) return;

    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      if (hash === 'dashboard') {
        setView('dashboard');
      } else {
        setView('landing');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange(); // Initial check

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, [mounted]);

  // Show nothing during SSR to prevent hydration mismatch
  if (!mounted) {
    return (
      <div className="min-h-screen bg-[#0A0F1C]" />
    );
  }

  return (
    <div className="min-h-screen transition-all duration-700 ease-in-out">
      {view === 'landing' ? (
        <LandingPage onLaunch={() => window.location.hash = 'dashboard'} />
      ) : (
        <Dashboard onExit={() => window.location.hash = ''} />
      )}
    </div>
  );
}
