import React from 'react'
import { motion } from 'framer-motion'

const metrics = [
  {
    value: '45%',
    label: 'AI code has security flaws'
  },
  {
    value: '1 in 5',
    label: 'apps have serious vulnerabilities'
  },
  {
    value: '2.74x',
    label: 'more XSS than human code'
  }
]

const incidents = [
  { name: 'Replit DB Deleted', tag: '2025' },
  { name: 'Tea App 72K IDs', tag: '2025' },
  { name: 'Lovable CVE-2025', tag: '2025' },
  { name: 'Moltbook 1.5M Keys', tag: '2026' },
  { name: 'Vinext 52 Vulns', tag: '2026' }
]

export const SecurityMetrics: React.FC = () => {
  return (
    <section className="w-full max-w-5xl mx-auto px-4 py-10 relative z-20 space-y-12">
      
      {/* 3 Yellow Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {metrics.map((item) => (
          <div
            key={item.label}
            className="rounded-2xl border border-[#f4c453]/60 bg-slate-950/60 backdrop-blur-md p-6 text-center hover:border-[#f4c453] transition-all hover:shadow-[0_0_30px_rgba(244,196,83,0.18)]"
          >
            <div className="text-4xl sm:text-5xl font-black font-mono tracking-tight text-[#f4c453] drop-shadow-[0_0_12px_rgba(244,196,83,0.3)]">
              {item.value}
            </div>
            <div className="mt-3 text-sm text-slate-300 font-medium">
              {item.label}
            </div>
          </div>
        ))}
      </div>

      {/* Real Incidents 2025-2026 Timeline */}
      <div className="rounded-2xl border border-slate-800/80 bg-slate-950/50 p-6 sm:p-8 backdrop-blur-md space-y-6">
        <div className="text-center sm:text-left">
          <span className="text-xs sm:text-sm font-bold tracking-[0.2em] uppercase text-[#f4c453]">
            REAL INCIDENTS 2025-2026
          </span>
        </div>

        {/* Horizontal Timeline */}
        <div className="relative pt-4 pb-2">
          {/* Timeline Connector Line */}
          <div className="hidden sm:block absolute top-[27px] left-8 right-8 h-[2px] bg-gradient-to-r from-amber-500/40 via-[#f4c453] to-amber-500/40" />

          {/* Incident Nodes */}
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-6 sm:gap-2 relative z-10">
            {incidents.map((incident, i) => (
              <div key={incident.name} className="flex flex-col items-center text-center group">
                {/* Node Dot */}
                <div className="size-4 rounded-full bg-[#f4c453] border-2 border-slate-950 shadow-[0_0_10px_#f4c453] group-hover:scale-125 transition-transform" />
                
                {/* Node Label */}
                <span className="mt-3 text-xs sm:text-sm font-semibold text-slate-200 group-hover:text-[#f4c453] transition-colors">
                  {incident.name}
                </span>
                <span className="text-[10px] text-slate-500 font-mono mt-0.5">
                  {incident.tag}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

    </section>
  )
}
