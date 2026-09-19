import React, { useEffect, useState } from 'react';
import { EnergyInnovationTerminalLogo } from './EnergyInnovationTerminalLogo';

interface GhostSplashScreenProps {
  onComplete: () => void;
}

export function GhostSplashScreen({ onComplete }: GhostSplashScreenProps) {
  const [visible, setVisible] = useState(true);
  const [fadingOut, setFadingOut] = useState(false);

  useEffect(() => {
    // Show for exactly 1.5 seconds, then fade out
    const timer = setTimeout(() => {
      setFadingOut(true);
      setTimeout(() => {
        setVisible(false);
        onComplete();
      }, 500); // 500ms fade duration
    }, 1500);

    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!visible) return null;

  return (
    <div 
      className={`fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[#090e17] transition-opacity duration-500 ${fadingOut ? 'opacity-0' : 'opacity-100'}`}
    >
      <div className="flex flex-col items-center justify-center space-y-6 animate-pulse">
        <div className="relative">
          <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full scale-150 animate-pulse"></div>
          <div className="relative bg-[#0b101c] p-4 rounded-2xl border border-white/10 shadow-2xl">
            <EnergyInnovationTerminalLogo size="lg" showText={false} />
          </div>
        </div>
        <div className="flex flex-col items-center">
          <h1 className="text-xl font-bold tracking-tight text-white mb-1">
            Energy Innovation Intelligence Terminal
          </h1>
          <p className="text-sm text-cyan-400 font-mono tracking-wider">
            INITIALIZING SECURE SESSION
          </p>
        </div>
        
        {/* Loading bar */}
        <div className="w-48 h-1 bg-white/10 rounded-full overflow-hidden mt-4 relative">
          <div className="absolute top-0 bottom-0 left-0 bg-cyan-400 rounded-full animate-pulse" style={{ width: '100%' }}></div>
        </div>
      </div>
    </div>
  );
}
