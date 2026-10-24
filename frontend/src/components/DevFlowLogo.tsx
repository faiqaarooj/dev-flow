import React from 'react'

interface DevFlowLogoProps {
  size?: 'sm' | 'md' | 'lg'
  withText?: boolean
  className?: string
}

export const DevFlowLogo: React.FC<DevFlowLogoProps> = ({
  size = 'md',
  withText = false,
  className = '',
}) => {
  const dimensions = {
    sm: { box: 'size-7', icon: 16, text: 'text-base' },
    md: { box: 'size-9', icon: 20, text: 'text-lg' },
    lg: { box: 'size-11', icon: 24, text: 'text-xl' },
  }[size]

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      {/* Dynamic Cyber Shield Logo */}
      <div
        className={`${dimensions.box} relative flex items-center justify-center rounded-xl bg-[#0d0e17] border border-white/10 shadow-lg shadow-purple-950/40 overflow-hidden group-hover:border-[#f4c453]/40 transition-all`}
      >
        {/* Glow ambient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#f4c453]/20 via-[#8b5cf6]/20 to-transparent pointer-events-none" />

        <svg
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-5/6 h-5/6 z-10"
        >
          {/* Shield Outline */}
          <path
            d="M16 4L26 8.5V16C26 21.5 21.8 26.2 16 28.5C10.2 26.2 6 21.5 6 16V8.5L16 4Z"
            fill="rgba(139, 92, 246, 0.15)"
            stroke="url(#devflow-grad)"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
          {/* Left code flow bracket < */}
          <path
            d="M13 12.5L9.5 16L13 19.5"
            stroke="#f4c453"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Right code flow bracket > */}
          <path
            d="M19 12.5L22.5 16L19 19.5"
            stroke="#a855f7"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Center core neon pulse */}
          <circle cx="16" cy="16" r="1.75" fill="#f4c453" />

          <defs>
            <linearGradient id="devflow-grad" x1="6" y1="4" x2="26" y2="28" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#f4c453" />
              <stop offset="60%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {withText && (
        <div className="flex flex-col leading-none">
          <span className={`font-bold tracking-tight text-white ${dimensions.text}`}>
            DevFlow <span className="text-[#f4c453]">AI</span>
          </span>
          <span className="text-[10px] uppercase tracking-wider text-[var(--muted)] font-medium mt-0.5">
            Security Intelligence
          </span>
        </div>
      )}
    </div>
  )
}
