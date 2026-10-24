import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, Copy, Terminal } from 'lucide-react'

export const FailurePatternsTerminal: React.FC = () => {
  const [copied, setCopied] = useState(false)

  const codeString = `// Top 3 failure patterns
1. Row Level Security: MISSING
2. Auth: CLIENT_SIDE_ONLY
3. API Keys: HARDCODED_IN_FRONTEND`

  const handleCopy = () => {
    navigator.clipboard.writeText(codeString)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="w-full max-w-4xl mx-auto px-4 pb-16 md:pb-24 relative z-20">
      <div className="rounded-2xl border border-slate-800 bg-[#090910] shadow-2xl overflow-hidden">
        {/* Terminal Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-slate-900/80 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="size-3 rounded-full bg-[#ef4444]" />
            <span className="size-3 rounded-full bg-[#f59e0b]" />
            <span className="size-3 rounded-full bg-[#10b981]" />
            <span className="ml-3 text-xs font-mono text-slate-400 flex items-center gap-1.5">
              <Terminal size={13} />
              <span>vulnerabilities.log</span>
            </span>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            {copied ? (
              <>
                <Check size={13} className="text-emerald-400" />
                <span className="text-emerald-400 font-medium">Copied</span>
              </>
            ) : (
              <>
                <Copy size={13} />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {/* Terminal Body */}
        <div className="p-5 sm:p-6 font-mono text-xs sm:text-sm leading-relaxed space-y-2 hero-grid-bg">
          <div className="text-slate-500 italic">
            // Top 3 failure patterns
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-purple-400 font-bold">1.</span>
            <span className="text-slate-200">Row Level Security:</span>
            <span className="text-red-400 font-semibold bg-red-950/40 px-2 py-0.5 rounded border border-red-900/50">
              MISSING
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-purple-400 font-bold">2.</span>
            <span className="text-slate-200">Auth:</span>
            <span className="text-amber-400 font-semibold bg-amber-950/40 px-2 py-0.5 rounded border border-amber-900/50">
              CLIENT_SIDE_ONLY
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-purple-400 font-bold">3.</span>
            <span className="text-slate-200">API Keys:</span>
            <span className="text-red-400 font-semibold bg-red-950/40 px-2 py-0.5 rounded border border-red-900/50">
              HARDCODED_IN_FRONTEND
            </span>
          </div>
        </div>

      </div>
    </section>
  )
}
