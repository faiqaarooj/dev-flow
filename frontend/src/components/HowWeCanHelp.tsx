import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'

interface HowWeCanHelpProps {
  onSelectFeature?: (step: number) => void
}

const steps = [
  {
    number: '1',
    title: 'Find Hidden Vulnerabilities',
    description: 'Bandit static scanning coupled with deep multi-agent intelligence locates vulnerabilities in your code.'
  },
  {
    number: '2',
    title: 'Understand The Risks',
    description: 'Turn obscure scanner logs into crystal clear impact assessments with verifiable code evidence.'
  },
  {
    number: '3',
    title: 'Get AI-Assisted Fixes',
    description: 'Remediation agents construct surgical code patches without hallucinating or modifying your remote repo.'
  },
  {
    number: '4',
    title: 'Verify The Results Before They Reach Production',
    description: 'Automatically re-scan patches to guarantee they resolve issues without introducing new regressions.'
  }
]

export const HowWeCanHelp: React.FC<HowWeCanHelpProps> = ({ onSelectFeature }) => {
  return (
    <section id="features" className="w-full max-w-6xl mx-auto px-6 py-12 md:py-20 relative z-20">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
        
        {/* Left Column: Numbered List */}
        <div className="lg:col-span-7 space-y-6">
          {/* Badge Title */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-950/60 border border-purple-500/30 text-purple-300 text-xs font-semibold tracking-wide shadow-sm">
            <Sparkles size={13} className="text-[#a78bfa]" />
            <span>How We Can Help You ?</span>
          </div>

          <div className="space-y-4 pt-2">
            {steps.map((step, idx) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                onClick={() => onSelectFeature?.(idx + 1)}
                className="group p-4 sm:p-5 rounded-2xl border border-slate-800/80 bg-slate-900/40 hover:bg-slate-800/60 hover:border-purple-500/40 transition-all cursor-pointer flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-4 sm:gap-5 min-w-0">
                  <span className="text-xl sm:text-2xl font-bold font-mono text-[#a78bfa] group-hover:text-white transition-colors">
                    {step.number}
                  </span>
                  <div className="min-w-0">
                    <h3 className="text-base sm:text-lg font-semibold text-white group-hover:text-purple-200 transition-colors truncate sm:whitespace-normal">
                      {step.title}
                    </h3>
                  </div>
                </div>

                <div className="size-8 rounded-full bg-slate-800/80 group-hover:bg-purple-600/30 border border-slate-700/60 group-hover:border-purple-500/50 flex items-center justify-center shrink-0 transition-all">
                  <ArrowRight size={15} className="text-slate-400 group-hover:text-white group-hover:translate-x-0.5 transition-transform" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Right Column: Isolated 3D Character Canvas */}
        <div className="lg:col-span-5 flex justify-center lg:justify-end">
          <div className="relative w-full max-w-[420px] aspect-square flex items-center justify-center">
            {/* Ambient Background Aura */}
            <div className="absolute inset-0 bg-gradient-to-tr from-purple-600/25 via-indigo-600/20 to-transparent blur-3xl rounded-full pointer-events-none" />

            {/* Anti-Gravity Floating Container for 3D Developer Graphic */}
            <motion.div
              animate={{ 
                y: [0, -12, 0],
                rotateZ: [0, 1, 0, -1, 0]
              }}
              transition={{ 
                repeat: Infinity, 
                duration: 6, 
                ease: 'easeInOut' 
              }}
              className="relative z-10 w-full h-full rounded-3xl overflow-hidden border border-purple-500/30 bg-slate-950/80 shadow-[0_0_50px_rgba(139,92,246,0.3)] group"
            >
              <img 
                src="/hero-developer.jpg" 
                alt="3D Developer with glowing laptop"
                className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-700"
              />

              {/* Glassmorphism Badge Overlay */}
              <div className="absolute bottom-4 left-4 right-4 p-3 rounded-xl bg-slate-950/70 backdrop-blur-md border border-slate-700/50 flex items-center justify-between text-xs text-slate-300">
                <span className="flex items-center gap-2">
                  <span className="size-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Real-time Multi-Agent Sentinel</span>
                </span>
                <span className="text-purple-300 font-mono font-medium">GDG Verified</span>
              </div>
            </motion.div>
          </div>
        </div>

      </div>
    </section>
  )
}
