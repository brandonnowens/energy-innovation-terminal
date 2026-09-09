import React from 'react';

export interface EnergyInnovationTerminalLogoProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  showText?: boolean;
  subtitle?: string;
  className?: string;
  useImage?: boolean;
}

export function EnergyInnovationTerminalLogo({
  size = 'md',
  showText = false,
  subtitle = 'by AIxEnergy',
  className = '',
  useImage = true,
}: EnergyInnovationTerminalLogoProps) {
  const sizeMap = {
    xs: { badge: 'w-6 h-6', text: 'text-xs', subText: 'text-[6.5px]' },
    sm: { badge: 'w-7 h-7', text: 'text-sm', subText: 'text-[7.5px]' },
    md: { badge: 'w-8 h-8', text: 'text-[14px]', subText: 'text-[8.5px]' },
    lg: { badge: 'w-11 h-11', text: 'text-lg', subText: 'text-[10.5px]' },
    xl: { badge: 'w-14 h-14', text: 'text-xl', subText: 'text-[12px]' },
    '2xl': { badge: 'w-20 h-20', text: 'text-2xl', subText: 'text-[14px]' },
  };

  const config = sizeMap[size] || sizeMap.md;

  return (
    <div className={`inline-flex items-center gap-2.5 select-none ${className}`}>
      {/* Primary Brand Icon */}
      <div className={`${config.badge} shrink-0 relative flex items-center justify-center rounded-lg overflow-hidden`}>
        {useImage ? (
          <img
            src="/energy-innovation-terminal-icon.png"
            alt="Energy Innovation Terminal"
            className="w-full h-full object-contain rounded-lg transition-transform duration-200 hover:scale-105 drop-shadow-[0_0_10px_rgba(0,210,255,0.45)]"
          />
        ) : (
          <svg
            viewBox="0 0 100 100"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-full h-full transition-transform duration-200 hover:scale-105 drop-shadow-[0_0_10px_rgba(0,210,255,0.45)]"
          >
            <defs>
              <linearGradient id="eitSquircleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00D2FF" />
                <stop offset="50%" stopColor="#00F5D4" />
                <stop offset="100%" stopColor="#0284C7" />
              </linearGradient>
              <linearGradient id="eitLeafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00F5D4" />
                <stop offset="100%" stopColor="#00D2FF" />
              </linearGradient>
              <linearGradient id="eitBarsGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#00D2FF" />
                <stop offset="100%" stopColor="#0369A1" />
              </linearGradient>
            </defs>

            {/* Squircle Base Frame */}
            <rect
              x="8"
              y="8"
              width="84"
              height="84"
              rx="24"
              fill="#04070E"
              stroke="url(#eitSquircleGrad)"
              strokeWidth="4.5"
            />
            {/* Satellite Node */}
            <circle cx="88" cy="24" r="4.5" fill="#00D2FF" />
            <circle cx="88" cy="24" r="2.2" fill="#FFFFFF" />
            {/* Top-Left Leaf Motif */}
            <path
              d="M26 48 C24 33 34 22 47 22 C48 27 46 36 39 42 C33 47 28 48 26 48 Z"
              fill="url(#eitLeafGrad)"
            />
            <path
              d="M26 48 C28 55 35 58 43 56 C39 51 34 49 26 48 Z"
              fill="#00D2B4"
            />
            {/* 3 Ascending Bar Chart Columns */}
            <rect x="42" y="53" width="6.5" height="18" rx="2" fill="url(#eitBarsGrad)" />
            <rect x="52" y="45" width="6.5" height="26" rx="2" fill="url(#eitBarsGrad)" />
            <rect x="62" y="37" width="6.5" height="34" rx="2" fill="url(#eitBarsGrad)" />
          </svg>
        )}
      </div>

      {showText && (
        <div className="flex flex-col justify-center leading-tight">
          <div className="flex items-center tracking-tight font-extrabold flex-wrap gap-x-1.5">
            <span className={`text-slate-900 dark:text-white ${config.text}`}>
              Energy
            </span>
            <span className={`bg-gradient-to-r from-[#00D2FF] to-[#00F5D4] bg-clip-text text-transparent ${config.text} font-black drop-shadow-[0_0_12px_rgba(0,210,255,0.4)]`}>
              Innovation Terminal
            </span>
          </div>
          <span
            className={`${config.subText} text-slate-500 dark:text-slate-400 font-medium tracking-[0.04em] mt-0.5 whitespace-nowrap`}
          >
            {subtitle}
          </span>
        </div>
      )}
    </div>
  );
}

// Backward compatibility export aliases
export const EnergySignalLogo = EnergyInnovationTerminalLogo;
export type EnergySignalLogoProps = EnergyInnovationTerminalLogoProps;

export const CleanGrantsLogo = EnergyInnovationTerminalLogo;
export type CleanGrantsLogoProps = EnergyInnovationTerminalLogoProps;

