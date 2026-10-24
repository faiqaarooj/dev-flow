import React from 'react'
import { ArrowUpRight, LayoutDashboard } from 'lucide-react'
import { Link } from 'react-router'
import { DevFlowLogo } from './DevFlowLogo'

interface HeroNavProps {
  onOpenScan: () => void
}

export const HeroNav: React.FC<HeroNavProps> = ({ onOpenScan }) => {
  return (
    <header className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between z-30 relative">
      {/* Brand Logo */}
      <Link to="/" className="flex items-center group">
        <DevFlowLogo size="md" withText={true} />
      </Link>

      {/* Nav Links */}
      <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
        <a href="#about" className="hover:text-white transition-colors">About</a>
        <a href="#features" className="hover:text-white transition-colors">Features</a>
        <Link 
          to="/dashboard" 
          className="flex items-center gap-1.5 text-purple-400 hover:text-purple-300 font-semibold transition-colors"
        >
          <LayoutDashboard size={15} />
          <span>Security Dashboard</span>
        </Link>
        <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
        <a href="#contact" className="hover:text-white transition-colors">Contact</a>
      </nav>

      {/* CTA Button */}
      <div className="flex items-center gap-3">
        <Link
          to="/dashboard"
          className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-purple-300 bg-purple-950/60 border border-purple-500/30 hover:bg-purple-900/60 transition-all"
        >
          <LayoutDashboard size={13} />
          <span>Dashboard</span>
        </Link>
        <button
          onClick={onOpenScan}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-slate-200 border border-slate-700/80 bg-slate-900/60 hover:bg-slate-800 hover:text-white hover:border-purple-500/50 transition-all shadow-sm cursor-pointer"
        >
          <span>Scan Now</span>
          <ArrowUpRight size={14} className="text-[#a78bfa]" />
        </button>
      </div>
    </header>
  )
}
