import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, GitFork, ArrowRight, ShieldCheck, AlertCircle, LoaderCircle } from 'lucide-react'
import { useNavigate } from 'react-router'
import { api } from '../services/api'

interface ScanModalProps {
  isOpen: boolean
  onClose: () => void
}

export const ScanModal: React.FC<ScanModalProps> = ({ isOpen, onClose }) => {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const validateUrl = (value: string) => {
    try {
      const parsed = new URL(value)
      if (
        parsed.protocol !== 'https:' ||
        parsed.hostname !== 'github.com' ||
        parsed.pathname.split('/').filter(Boolean).length < 2
      ) {
        throw new Error()
      }
      return ''
    } catch {
      return 'Please enter a valid GitHub repo URL (e.g., https://github.com/owner/repo)'
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = url.trim()
    const validationError = validateUrl(trimmed)
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)
    setError('')

    try {
      const result = await api.startScan(trimmed)
      const scanId = result?.scan_id || result?.id
      if (!scanId) {
        throw new Error('Scan initiated but no scan ID was returned by the backend.')
      }
      onClose()
      navigate(`/scans/${scanId}`, { state: { initial: result } })
    } catch (err: any) {
      setError(err.message || 'Failed to start scan.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/75 backdrop-blur-md"
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 15 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 15 }}
            className="relative w-full max-w-lg rounded-3xl border border-purple-500/30 bg-[#0d0d1a] p-6 sm:p-8 shadow-[0_0_60px_rgba(139,92,246,0.3)] z-10"
          >
            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X size={18} />
            </button>

            {/* Header */}
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400">
                <ShieldCheck size={22} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight">Scan Repository</h3>
                <p className="text-xs text-slate-400">Multi-agent static analysis and automated verification</p>
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Public GitHub Repository URL
                </label>
                <div className="relative">
                  <GitFork size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => {
                      setUrl(e.target.value)
                      if (error) setError('')
                    }}
                    placeholder="https://github.com/owner/repository"
                    className="w-full h-12 pl-10 pr-4 rounded-xl border border-slate-700 bg-slate-900/90 text-sm text-white placeholder-slate-500 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all font-mono"
                    autoFocus
                  />
                </div>
                {error ? (
                  <div className="mt-2 flex items-center gap-1.5 text-xs text-red-400 font-medium">
                    <AlertCircle size={13} />
                    <span>{error}</span>
                  </div>
                ) : (
                  <p className="mt-2 text-[11px] text-slate-500">
                    MVP evaluates Python files with Bandit static tools and AI agent verification.
                  </p>
                )}
              </div>

              {/* Sample Quick Links */}
              <div className="pt-1">
                <span className="text-[11px] text-slate-500 mr-2">Try sample:</span>
                <button
                  type="button"
                  onClick={() => {
                    setUrl('https://github.com/fastapi/fastapi')
                    setError('')
                  }}
                  className="text-[11px] text-purple-400 hover:text-purple-300 underline font-mono"
                >
                  fastapi/fastapi
                </button>
              </div>

              {/* Action Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full mt-4 h-12 rounded-xl bg-[#8b5cf6] hover:bg-[#7c3aed] text-white text-sm font-semibold tracking-wide flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(139,92,246,0.4)] transition-all cursor-pointer disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <LoaderCircle size={18} className="animate-spin" />
                    <span>Initiating Multi-Agent Pipeline...</span>
                  </>
                ) : (
                  <>
                    <span>Analyze Repository</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
