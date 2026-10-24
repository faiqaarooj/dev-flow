import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, ShieldAlert } from 'lucide-react'

interface HeroHeaderProps {
  onOpenScan: () => void
  onExplore: () => void
}

export const HeroHeader: React.FC<HeroHeaderProps> = ({ onOpenScan, onExplore }) => {
  return (
    <section className="relative pt-12 pb-16 md:pt-20 md:pb-24 text-center px-4 max-w-4xl mx-auto z-20">
      {/* Subtle Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-purple-600/15 blur-[120px] pointer-events-none rounded-full" />

      {/* Main Headline */}
      <motion.h1 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-white leading-[1.15]"
      >
        Build Fearlessly. Ship Securely.
      </motion.h1>

      {/* Subheadline */}
      <motion.p 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15, ease: 'easeOut' }}
        className="mt-5 text-base sm:text-lg md:text-xl text-slate-300 font-normal max-w-2xl mx-auto"
      >
        Your Vibe Coded Application Will Be Protected
      </motion.p>

      {/* Dual CTA Buttons */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3, ease: 'easeOut' }}
        className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
      >
        {/* Primary Filled Purple Button */}
        <button
          onClick={onOpenScan}
          className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-[#8b5cf6] hover:bg-[#7c3aed] text-white text-sm font-semibold tracking-wide transition-all shadow-[0_0_25px_rgba(139,92,246,0.4)] hover:shadow-[0_0_35px_rgba(139,92,246,0.6)] hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
        >
          Scan Your Repository
        </button>

        {/* Secondary Outlined Button */}
        <button
          onClick={onExplore}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl border border-slate-700/80 bg-slate-900/50 hover:bg-slate-800 text-slate-200 hover:text-white text-sm font-medium transition-all hover:border-slate-500 cursor-pointer"
        >
          <span>Explore How It Works</span>
          <ArrowRight size={16} />
        </button>
      </motion.div>
    </section>
  )
}
