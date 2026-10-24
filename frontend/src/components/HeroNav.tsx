import React from 'react'
import { ShieldCheck, ArrowUpRight, LayoutDashboard } from 'lucide-react'
import { Link } from 'react-router'

interface HeroNavProps {
  onOpenScan: () => void
}

export const HeroNav: React.FC<HeroNavProps> = ({ onOpenScan }) => {
  return (
    <header className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between z-30 relative">
      {/* Brand Logo */}
      <Link to="/" className="flex items-center gap-2.5 group">
        <div className="size-9 rounded-xl bg-gradient-to-br from-[#8b5cf6] to-[#6d28d9] flex items-center justify-center text-white shadow-lg shadow-purple-900/30 group-hover:scale-105 transition-transform">
          <ShieldCheck size={20} />
        </div>
        <div className="flex flex-col">
          <span className="font-bold tracking-tight text-white text-lg">DevFlow <span className="text-[#a78bfa]">AI</span></span>
        </div>
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
