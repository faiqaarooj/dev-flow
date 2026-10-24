import React, { useState } from 'react'
import { HeroNav } from '../components/HeroNav'
import { HeroHeader } from '../components/HeroHeader'
import { HowWeCanHelp } from '../components/HowWeCanHelp'
import { VulnerabilityAlert } from '../components/VulnerabilityAlert'
import { SecurityMetrics } from '../components/SecurityMetrics'
import { FailurePatternsTerminal } from '../components/FailurePatternsTerminal'
import { ScanModal } from '../components/ScanModal'
import { DevFlowLogo } from '../components/DevFlowLogo'
import { Heart } from 'lucide-react'

export const HeroPage: React.FC = () => {
  const [scanModalOpen, setScanModalOpen] = useState(false)

  const handleOpenScan = () => {
    setScanModalOpen(true)
  }

  const handleExplore = () => {
    const el = document.getElementById('features')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <div className="min-h-screen bg-[#07070d] text-slate-100 selection:bg-purple-600 selection:text-white relative overflow-hidden">
      
      {/* Background Radial Glow Effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[550px] bg-gradient-to-b from-purple-700/15 via-indigo-900/10 to-transparent blur-[140px] pointer-events-none rounded-full" />
      <div className="absolute top-[800px] left-0 w-[450px] h-[450px] bg-purple-900/10 blur-[130px] pointer-events-none rounded-full" />
      <div className="absolute top-[1400px] right-0 w-[550px] h-[550px] bg-red-900/10 blur-[140px] pointer-events-none rounded-full" />

      {/* Subtle Grid Overlay */}
      <div className="absolute inset-0 hero-grid-bg opacity-30 pointer-events-none" />

      {/* Main Container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        
        {/* Navigation Bar */}
        <HeroNav onOpenScan={handleOpenScan} />

        {/* Hero Section */}
        <main className="flex-1">
          {/* Main Title & Dual CTA */}
          <HeroHeader 
            onOpenScan={handleOpenScan} 
            onExplore={handleExplore} 
          />

          {/* How We Can Help & 3D Character */}
          <HowWeCanHelp onSelectFeature={() => handleOpenScan()} />

          {/* Red Vulnerability Warning Box */}
          <VulnerabilityAlert onOpenScan={handleOpenScan} />

          {/* 3 Metric Cards & Incidents Timeline */}
          <SecurityMetrics />

          {/* Top 3 Failure Patterns Terminal */}
          <FailurePatternsTerminal />
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-800/80 bg-slate-950/80 py-8 px-6 text-center text-xs text-slate-500 relative z-20">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <DevFlowLogo size="sm" />
              <span className="font-semibold text-slate-300">DevFlow AI</span>
              <span>— Find the risk. Fix the code. Verify the result.</span>
            </div>

            <div className="flex items-center gap-1.5 text-slate-400">
              <span>Crafted with</span>
              <Heart size={13} className="text-red-500 fill-red-500" />
              <span>by <strong className="text-slate-200">Awesome Team</strong></span>
            </div>
          </div>
        </footer>

      </div>

      {/* Interactive Scan Modal */}
      <ScanModal 
        isOpen={scanModalOpen} 
        onClose={() => setScanModalOpen(false)} 
      />

    </div>
  )
}
