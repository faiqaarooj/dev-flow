import { useEffect, useMemo, useState } from 'react'
import {
  Activity, AlertTriangle, ArrowRight, CheckCircle2, ChevronRight, CircleDot,
  Clock3, Code2, Download, FileDown, FileSearch, FileText, GitFork, History,
  Layers, LayoutDashboard, LoaderCircle, Menu, Search, Settings, Shield,
  ShieldAlert, ShieldCheck, X, XCircle,
} from 'lucide-react'
import { createBrowserRouter, Link, NavLink, Outlet, useNavigate, useParams } from 'react-router'
import { api } from '../services/api'
import { HeroPage } from '../pages/HeroPage'
import { DevFlowLogo } from '../components/DevFlowLogo'

const nav = [
  ['Landing Page', '/', ShieldCheck],
  ['Overview', '/dashboard', LayoutDashboard],
  ['New Scan', '/scans/new', FileSearch],
  ['Scan History', '/history', History],
  ['Security Findings', '/findings', ShieldAlert],
  ['Downloads & Docs', '/docs', FileDown],
  ['Settings', '/settings', Settings],
]

const cx = (...classes: Array<string | false | undefined>) => classes.filter(Boolean).join(' ')

function Button({ children, className = '', variant = 'primary', ...props }: any) {
  const styles = variant === 'secondary'
    ? 'border border-[var(--border)] bg-[var(--panel)] text-[var(--text)] hover:bg-[var(--panel-hover)]'
    : 'bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)]'
  return <button className={cx('inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]', styles, className)} {...props}>{children}</button>
}

function Shell() {
  const [mobile, setMobile] = useState(false)
  const [apiHealth, setApiHealth] = useState<string>('checking')

  useEffect(() => {
    let active = true
    api.getHealth()
      .then(() => { if (active) setApiHealth('connected') })
      .catch(() => { if (active) setApiHealth('disconnected') })
    return () => { active = false }
  }, [])

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      {mobile && <button aria-label="Close navigation" onClick={() => setMobile(false)} className="fixed inset-0 z-30 bg-black/60 lg:hidden" />}
      <aside className={cx('fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-[var(--border)] bg-[var(--sidebar)] transition-transform lg:translate-x-0', mobile ? 'translate-x-0' : '-translate-x-full')}>
        <div className="flex h-20 items-center gap-3 border-b border-[var(--border)] px-6">
          <Link to="/" className="flex items-center gap-3 hover:opacity-85 transition-opacity">
            <DevFlowLogo size="sm" withText={true} />
          </Link>
          <button aria-label="Close navigation" onClick={() => setMobile(false)} className="ml-auto text-[var(--muted)] lg:hidden"><X size={20} /></button>
        </div>
        <nav className="flex-1 space-y-1 p-3" aria-label="Primary navigation">
          {nav.map(([label, path, Icon]: any) => (
            <NavLink key={path} to={path} end={path === '/dashboard'} onClick={() => setMobile(false)}
              className={({ isActive }) => cx('flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition', isActive ? 'bg-[var(--accent-soft)] text-[var(--accent-light)]' : 'text-[var(--muted)] hover:bg-[var(--panel)] hover:text-[var(--text)]')}>
              <Icon size={18} />{label}
            </NavLink>
          ))}
        </nav>
        <div className="m-4 rounded-xl border border-[var(--border)] bg-[var(--panel)] p-3">
          <div className="flex items-center gap-2 text-xs font-medium">
            <CircleDot size={14} className={apiHealth === 'connected' ? 'text-[var(--success)]' : 'text-[var(--danger)]'} />
            {apiHealth === 'connected' ? 'Backend connected' : (apiHealth === 'checking' ? 'Connecting...' : 'Backend offline')}
          </div>
          <div className="mt-1 truncate text-[11px] text-[var(--muted)]">{api.baseUrl || 'Same-origin (/api)'}</div>
        </div>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center border-b border-[var(--border)] bg-[color:var(--bg-translucent)] px-4 backdrop-blur-xl sm:px-8">
          <button aria-label="Open navigation" onClick={() => setMobile(true)} className="mr-3 text-[var(--muted)] lg:hidden"><Menu size={22} /></button>
          <div className="text-sm text-[var(--muted)]">Workspace <span className="mx-2 text-[var(--border-strong)]">/</span> <span className="text-[var(--text)]">Security</span></div>
          <div className="ml-auto flex items-center gap-2 text-xs text-[var(--muted)]">
            <span className={cx('size-1.5 rounded-full', apiHealth === 'connected' ? 'bg-[var(--success)]' : 'bg-[var(--danger)]')} />
            {apiHealth === 'connected' ? 'API ready' : 'API offline'}
          </div>
        </header>
        <main className="mx-auto max-w-[1480px] p-4 sm:p-8"><Outlet /></main>
      </div>
    </div>
  )
}

function PageHeading({ eyebrow, title, description, action }: any) {
  return <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end"><div><div className="mb-2 text-xs font-medium text-[var(--muted)]">{eyebrow}</div><h1 className="text-2xl font-semibold tracking-[-.025em] sm:text-3xl">{title}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--muted)]">{description}</p></div>{action}</div>
}

function RepoForm({ compact = false }: { compact?: boolean }) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)
  const navigate = useNavigate()
  const validate = (value: string) => {
    try {
      const parsed = new URL(value)
      if (parsed.protocol !== 'https:' || parsed.hostname !== 'github.com' || parsed.pathname.split('/').filter(Boolean).length < 2) throw new Error()
      return ''
    } catch { return 'Enter a repository URL like https://github.com/owner/repository' }
  }
  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    const issue = validate(url.trim())
    if (issue) return setError(issue)
    setRunning(true); setError('')
    try {
      const result = await api.startScan(url.trim())
      const id = result?.scan_id || result?.id
      if (!id) throw new Error('The API accepted the request but did not return a scan ID.')
      navigate(`/scans/${id}`, { state: { initial: result } })
    } catch (err: any) { setError(err.message) } finally { setRunning(false) }
  }
  return <form onSubmit={submit} className={cx('rounded-2xl border border-[var(--border)] bg-[var(--panel)]', compact ? 'p-5' : 'p-5 sm:p-7')}>
    <label htmlFor="repo-url" className="mb-2 block text-sm font-medium">Public GitHub repository</label>
    <div className="flex flex-col gap-3 sm:flex-row">
      <div className="relative flex-1"><GitFork className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--muted)]" size={19} /><input id="repo-url" value={url} onChange={e => { setUrl(e.target.value); if (error) setError('') }} placeholder="https://github.com/owner/repository" aria-invalid={!!error} aria-describedby="repo-help" className="h-12 w-full rounded-xl border border-[var(--border-strong)] bg-[var(--input)] pl-12 pr-4 text-sm outline-none transition placeholder:text-[var(--muted-dim)] focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent-ring)]" /></div>
      <Button type="submit" disabled={running} className="h-12 sm:min-w-48">{running ? <><LoaderCircle className="animate-spin" size={18} /> Starting analysis</> : <>Analyze Repository <ArrowRight size={17} /></>}</Button>
    </div>
    <div id="repo-help" className={cx('mt-3 flex items-start gap-2 text-xs', error ? 'text-[var(--danger)]' : 'text-[var(--muted)]')}>{error ? <AlertTriangle size={15} className="shrink-0" /> : <Shield size={14} />}<span>{error || 'Evaluates Python repositories with Bandit static security tools and AI agent verification. No code is executed.'}</span></div>
  </form>
}

function SummaryCard({ label, value, icon: Icon, tone = 'neutral' }: any) {
  const colors: any = { neutral: 'text-[var(--accent-light)] bg-[var(--accent-soft)]', danger: 'text-[var(--danger)] bg-[var(--danger-soft)]', success: 'text-[var(--success)] bg-[var(--success-soft)]' }
  return <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-5"><div className="flex items-center justify-between"><div className={cx('grid size-9 place-items-center rounded-xl', colors[tone])}><Icon size={18} /></div><span className="text-2xl font-semibold tabular-nums">{value}</span></div><div className="mt-5 text-sm text-[var(--muted)]">{label}</div></div>
}

function EmptyState({ title = 'No scans yet', description = 'Analyze a public Python repository to create your first security report.', action = true }: any) {
  return <div className="grid min-h-64 place-items-center rounded-2xl border border-dashed border-[var(--border-strong)] bg-[var(--panel-subtle)] p-8 text-center"><div><div className="mx-auto grid size-12 place-items-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent-light)]"><FileSearch size={23} /></div><h2 className="mt-4 font-semibold">{title}</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--muted)]">{description}</p>{action && <Link to="/scans/new" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[var(--accent-light)] hover:text-white">Start a new scan <ChevronRight size={16} /></Link>}</div></div>
}

function Overview() {
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    api.listScans()
      .then((data) => { if (active && Array.isArray(data)) setHistory(data) })
      .catch(() => {})
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const totalFindings = history.reduce((acc, item) => acc + (item.findings_count || 0), 0)
  const completedScans = history.filter((item) => item.status === 'completed' || item.status === 'completed_with_warnings').length

  return (
    <>
      <PageHeading eyebrow="Overview" title="Repository Security" description="Find risk, inspect the evidence, and verify proposed fixes without changing your repository." action={<Link to="/history" className="text-sm font-medium text-[var(--muted)] hover:text-white">View history</Link>} />
      <RepoForm />
      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard label="Total findings detected" value={totalFindings} icon={ShieldAlert} />
        <SummaryCard label="Scans completed" value={completedScans} icon={CheckCircle2} tone="success" />
        <SummaryCard label="Total repositories analyzed" value={history.length} icon={Activity} />
        <SummaryCard label="Verified resolved" value="0" icon={ShieldCheck} tone="success" />
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-5">
        <div>
          <div className="flex items-center gap-2 font-semibold">
            <FileDown size={18} className="text-[var(--accent-light)]" />
            <span>Download Project Deliverables</span>
          </div>
          <p className="mt-1 text-xs text-[var(--muted)]">Download official PRD specifications, System Design documents, or scan patches.</p>
        </div>
        <div className="flex flex-wrap gap-2.5">
          <a
            href={api.downloadPrdUrl}
            download="DevFlow-AI-PRD.md"
            className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-3.5 py-2 text-xs font-semibold text-white transition hover:border-[var(--accent)] hover:bg-[var(--panel-hover)]"
          >
            <FileText size={15} className="text-yellow-400" /> Download PRD (.md)
          </a>
          <a
            href={api.downloadSystemDesignUrl}
            download="DevFlow-AI-System-Design.md"
            className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-3.5 py-2 text-xs font-semibold text-white transition hover:border-[var(--accent)] hover:bg-[var(--panel-hover)]"
          >
            <Layers size={15} className="text-purple-400" /> Download System Design (.md)
          </a>
        </div>
      </div>
      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-semibold">Recent activity</h2>
          <span className="text-xs text-[var(--muted)]">API results from backend database</span>
        </div>
        {loading ? (
          <div className="flex justify-center p-8 text-[var(--muted)]"><LoaderCircle className="animate-spin" size={20} /></div>
        ) : history.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--panel)]">
            <div className="divide-y divide-[var(--border)]">
              {history.slice(0, 5).map((scan) => (
                <Link key={scan.scan_id} to={`/scans/${scan.scan_id}`} className="flex items-center justify-between p-4 transition hover:bg-[var(--panel-hover)]">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-medium text-white">{scan.repository_name || scan.owner ? `${scan.owner}/${scan.repository_name}` : scan.repository_url}</span>
                      <span className={cx('inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize', scan.status === 'completed' ? 'bg-[var(--success-soft)] text-[var(--success)]' : (scan.status === 'failed' ? 'bg-[var(--danger-soft)] text-[var(--danger)]' : 'bg-[var(--warning-soft)] text-[var(--warning)]'))}>
                        {scan.status}
                      </span>
                    </div>
                    <div className="mt-1 text-xs text-[var(--muted)]">
                      {scan.findings_count} findings • {scan.created_at ? new Date(scan.created_at).toLocaleString() : 'Recently scanned'}
                    </div>
                  </div>
                  <ChevronRight size={18} className="text-[var(--muted)]" />
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>
    </>
  )
}

const stages = ['Validating repository URL', 'Cloning & inspecting files', 'Running Bandit static security scanner', 'AI triage & prioritization', 'Preparing results']

function NewScan() {
  return (
    <>
      <PageHeading eyebrow="New scan" title="Analyze a repository" description="Submit a public GitHub repository to check for security weaknesses." />
      <div className="grid gap-6 xl:grid-cols-[1.4fr_.6fr]">
        <RepoForm />
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
          <div className="mb-5 flex items-center gap-2 font-medium"><Shield size={17} className="text-[var(--muted)]" /> Scan process</div>
          <div className="space-y-4">
            {stages.map((stage, i) => (
              <div key={stage} className="flex items-center gap-3 text-sm text-[var(--muted)]">
                <span className="grid size-6 place-items-center rounded-full border border-[var(--border-strong)] text-[10px]">{i + 1}</span>
                {stage}
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

function SeverityBadge({ severity }: any) {
  const value = String(severity || 'informational').toLowerCase()
  const styles: any = {
    critical: 'bg-[var(--danger-soft)] text-[var(--danger)]',
    high: 'bg-[var(--danger-soft)] text-[var(--danger)]',
    medium: 'bg-[var(--warning-soft)] text-[var(--warning)]',
    low: 'bg-[var(--success-soft)] text-[var(--success)]',
    informational: 'bg-[var(--accent-soft)] text-[var(--accent-light)]',
  }
  return <span className={cx('inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold capitalize', styles[value] || styles.informational)}>{value}</span>
}

function ScanResults() {
  const { scanId = '' } = useParams()
  const navigate = useNavigate()
  const [scan, setScan] = useState<any>(null)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<any>(null)

  useEffect(() => {
    let active = true
    let timer: any = null

    const fetchScan = async () => {
      try {
        const data = await api.getScan(scanId)
        if (!active) return
        setScan(data)
        // If scan is still running or queued, poll every 1.5 seconds
        if (data.status === 'queued' || data.status === 'running') {
          timer = setTimeout(fetchScan, 1500)
        }
      } catch (e: any) {
        if (active) setError(e.message)
      }
    }

    fetchScan()
    return () => {
      active = false
      if (timer) clearTimeout(timer)
    }
  }, [scanId])

  if (error) return <ErrorState message={error} retry={() => window.location.reload()} />
  if (!scan || scan.status === 'queued' || scan.status === 'running') {
    return <LoadingScan scanId={scanId} status={scan?.status || 'queued'} stagesState={scan?.stages} />
  }

  if (scan.status === 'failed') {
    return (
      <>
        <PageHeading
          eyebrow={`Scan ${scanId}`}
          title={scan.repository_name ? `${scan.repository_name}` : 'Repository Security Scan'}
          description={scan.repository_url || 'Target repository analysis'}
          action={
            <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-xs font-semibold text-red-400">
              <XCircle size={14} /> Scan Incomplete
            </span>
          }
        />

        <div className="mt-6 rounded-2xl border border-red-500/30 bg-[var(--panel)] p-6">
          <div className="flex items-start gap-4">
            <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-red-500/15 text-red-400">
              <AlertTriangle size={20} />
            </div>
            <div className="flex-1">
              <h2 className="text-base font-semibold text-white">Repository Inspection Notice</h2>
              <p className="mt-1 text-sm text-[var(--muted)] leading-relaxed">
                {scan.error_message || 'The security scan encountered an issue accessing or inspecting the target repository.'}
              </p>
              <div className="mt-4 flex flex-wrap items-center gap-3">
                <Button onClick={() => navigate('/scans/new')} variant="primary">
                  Analyze Another Repository <ArrowRight size={15} />
                </Button>
                <Button onClick={() => window.location.reload()} variant="secondary">
                  Refresh Scan
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Try Another Repository</h3>
          <RepoForm compact={true} />
        </div>
      </>
    )
  }

  const findings = Array.isArray(scan?.findings) ? scan.findings : []
  const shown = findings.filter((f: any) => `${f.title} ${f.file_path || ''} ${f.rule_id || ''}`.toLowerCase().includes(query.toLowerCase()))
  const filesAnalyzed = scan.coverage?.files_analyzed ?? scan.files_analyzed ?? 0

  return (
    <>
      <PageHeading
        eyebrow={`Scan ${scanId}`}
        title={scan.repository_name ? `${scan.repository_name}` : 'Repository Security Scan'}
        description={scan.repository_url || 'Target repository analysis'}
        action={
          <span className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--panel)] px-3 py-2 text-xs capitalize">
            <CircleDot size={14} className={scan.status === 'completed' ? 'text-[var(--success)]' : 'text-[var(--warning)]'} />
            {scan.status.replace(/_/g, ' ')}
          </span>
        }
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <SummaryCard label="Security findings" value={findings.length} icon={ShieldAlert} tone={findings.length > 0 ? 'danger' : 'success'} />
        <SummaryCard label="Python files analyzed" value={filesAnalyzed} icon={Code2} />
        <SummaryCard label="Files discovered" value={scan.coverage?.files_discovered ?? filesAnalyzed} icon={Activity} />
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-4">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold">
            <FileDown size={17} className="text-[var(--accent-light)]" />
            <span>Audit Deliverables & Downloadable Files</span>
          </div>
          <p className="mt-0.5 text-xs text-[var(--muted)]">Export security report, project requirements (PRD), and system architecture.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <a
            href={api.getScanReportUrl(scanId)}
            download={`DevFlow-Security-Report-${scanId}.md`}
            className="inline-flex min-h-9 items-center gap-1.5 rounded-xl border border-yellow-500/40 bg-yellow-500/10 px-3 py-1.5 text-xs font-semibold text-yellow-300 transition hover:bg-yellow-500/20"
          >
            <Download size={14} /> Audit Report (.md)
          </a>
          <a
            href={api.downloadPrdUrl}
            download="DevFlow-AI-PRD.md"
            className="inline-flex min-h-9 items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-3 py-1.5 text-xs font-semibold text-white transition hover:border-[var(--accent)]"
          >
            <FileText size={14} className="text-yellow-400" /> PRD (.md)
          </a>
          <a
            href={api.downloadSystemDesignUrl}
            download="DevFlow-AI-System-Design.md"
            className="inline-flex min-h-9 items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-3 py-1.5 text-xs font-semibold text-white transition hover:border-[var(--accent)]"
          >
            <Layers size={14} className="text-purple-400" /> System Design (.md)
          </a>
        </div>
      </div>

      {scan.coverage?.warnings && scan.coverage.warnings.length > 0 && (
        <div className="mt-4 rounded-xl border border-[var(--warning-border,rgba(244,196,83,0.3))] bg-[var(--warning-soft)] p-4 text-xs text-[var(--warning)]">
          <div className="font-semibold mb-1">Coverage Notices:</div>
          <ul className="list-disc pl-4 space-y-0.5">
            {scan.coverage.warnings.map((w: string, i: number) => <li key={i}>{w}</li>)}
          </ul>
        </div>
      )}

      <div className="mt-6 rounded-2xl border border-[var(--border)] bg-[var(--panel)]">
        <div className="flex flex-col gap-3 border-b border-[var(--border)] p-4 sm:flex-row sm:items-center">
          <h2 className="font-semibold">Security findings ({findings.length})</h2>
          <div className="relative sm:ml-auto sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" size={16} />
            <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search title, file, or rule" className="h-10 w-full rounded-lg border border-[var(--border)] bg-[var(--input)] pl-10 pr-3 text-sm outline-none focus:border-[var(--accent)]" />
          </div>
        </div>
        {shown.length === 0 ? (
          <div className="p-5">
            <EmptyState action={false} title={findings.length ? 'No matching findings' : 'No vulnerabilities detected'} description={findings.length ? 'Adjust your search to see other results.' : 'The Bandit scanner did not detect any known security weaknesses in the analyzed files.'} />
          </div>
        ) : (
          <div className="divide-y divide-[var(--border)]">
            {shown.map((finding: any, index: number) => (
              <button key={finding.finding_id || index} onClick={() => setSelected(finding)} className="flex w-full items-center gap-4 p-4 text-left transition hover:bg-[var(--panel-hover)]">
                <SeverityBadge severity={finding.severity} />
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium">{finding.title || finding.message || 'Untitled finding'}</div>
                  <div className="mt-1 truncate font-mono text-xs text-[var(--muted)]">
                    {finding.file_path || 'No file location supplied'}{finding.line_start ? `:${finding.line_start}` : ''}
                  </div>
                </div>
                <span className="hidden text-xs text-[var(--muted)] sm:block font-mono bg-[var(--bg)] px-2 py-1 rounded border border-[var(--border)]">{finding.rule_id || 'Bandit'}</span>
                <ChevronRight size={17} className="text-[var(--muted)]" />
              </button>
            ))}
          </div>
        )}
      </div>
      {selected && <FindingDrawer finding={selected} scanId={scanId} close={() => setSelected(null)} />}
    </>
  )
}

function LoadingScan({ scanId, status, stagesState }: any) {
  return (
    <div>
      <PageHeading eyebrow={`Scan ${scanId}`} title="Analyzing Repository" description="Running multi-agent analysis: git retrieval, Bandit security scans, and AI risk triage." />
      <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="space-y-4">
          {stages.map((stage, i) => (
            <div key={stage} className="flex items-center gap-3 border-b border-[var(--border)] py-4 last:border-0">
              <LoaderCircle size={18} className="animate-spin text-[var(--accent-light)]" />
              <span className="text-sm font-medium">{stage}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function FindingDrawer({ finding, scanId, close }: any) {
  const [patch, setPatch] = useState<any>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const findingId = finding.finding_id || finding.id

  const suggest = async () => {
    setBusy(true); setError('')
    try {
      const res = await api.suggestFix(scanId, findingId)
      setPatch(res)
    } catch (e: any) { setError(e.message) }
    finally { setBusy(false) }
  }

  const rescan = async () => {
    setBusy(true); setError('')
    try {
      const result = await api.rescanPatch(scanId, {
        proposal_id: patch?.proposal_id || '',
        finding_id: findingId,
        patch: patch?.diff || patch?.patch,
      })
      setPatch({
        ...patch,
        verification: result?.status,
        verificationEvidence: result?.evidence,
      })
    } catch (e: any) { setError(e.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm" onMouseDown={close}>
      <section aria-label="Finding details" onMouseDown={e => e.stopPropagation()} className="h-full w-full max-w-2xl overflow-y-auto border-l border-[var(--border)] bg-[var(--bg)] p-5 shadow-2xl sm:p-8">
        <div className="flex items-start gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <SeverityBadge severity={finding.severity} />
              <span className="font-mono text-xs text-[var(--muted)]">{finding.rule_id}</span>
            </div>
            <h2 className="mt-3 text-xl font-semibold">{finding.title || finding.message}</h2>
            <div className="mt-2 font-mono text-xs text-[var(--muted)]">
              {finding.file_path}{finding.line_start ? `:${finding.line_start}` : ''}
            </div>
          </div>
          <button aria-label="Close details" onClick={close} className="rounded-lg p-2 text-[var(--muted)] hover:bg-[var(--panel)]"><X size={20} /></button>
        </div>

        <div className="mt-8 space-y-6">
          <div>
            <h3 className="mb-2 text-sm font-semibold">Message & Description</h3>
            <p className="text-sm leading-6 text-[var(--muted)]">{finding.message}</p>
          </div>
          {finding.evidence && (
            <div>
              <h3 className="mb-2 text-sm font-semibold">Evidence Code</h3>
              <pre className="rounded-xl border border-[var(--border)] bg-[var(--code)] p-4 text-xs leading-5 text-[var(--code-text)] font-mono overflow-auto">{finding.evidence}</pre>
            </div>
          )}
          {finding.rationale && (
            <div>
              <h3 className="mb-2 text-sm font-semibold">Triage Rationale</h3>
              <p className="text-sm leading-6 text-[var(--muted)]">{finding.rationale}</p>
            </div>
          )}
        </div>

        <div className="mt-8 border-t border-[var(--border)] pt-6">
          {error && (
            <div className="mb-4 flex gap-2 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] p-3 text-sm text-[var(--danger)]">
              <AlertTriangle size={17} />{error}
            </div>
          )}

          {!patch ? (
            <Button onClick={suggest} disabled={busy}>
              {busy ? <LoaderCircle className="animate-spin" size={17} /> : <ShieldCheck size={17} />} Suggest Fix
            </Button>
          ) : (
            <>
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold">Proposed Patch</h3>
                <span className={cx('rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase', patch.verification === 'resolved' ? 'bg-[var(--success-soft)] text-[var(--success)]' : (patch.verification === 'still_detected' ? 'bg-[var(--danger-soft)] text-[var(--danger)]' : 'bg-[var(--warning-soft)] text-[var(--warning)]'))}>
                  {patch.verification ? patch.verification.replace(/_/g, ' ') : 'Unverified'}
                </span>
              </div>
              <pre className="max-h-80 overflow-auto rounded-xl border border-[var(--border)] bg-[var(--code)] p-4 text-xs leading-6 text-[var(--code-text)] font-mono">{patch.diff || patch.patch}</pre>
              {patch.explanation && <p className="mt-3 text-sm leading-6 text-[var(--muted)]">{patch.explanation}</p>}
              {patch.verificationEvidence && (
                <div className="mt-3 rounded-lg border border-[var(--border)] bg-[var(--panel)] p-3 text-xs text-[var(--muted)]">
                  <span className="font-semibold text-white">Scanner Verification Result:</span> {patch.verificationEvidence}
                </div>
              )}
              <div className="mt-4 flex flex-wrap gap-2.5">
                <Button onClick={rescan} disabled={busy}>
                  {busy ? <LoaderCircle className="animate-spin" size={17} /> : <ShieldCheck size={17} />} Re-scan Patch
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    const text = patch.diff || patch.patch || ''
                    const filename = `fix_${finding.rule_id || 'issue'}_${findingId}.diff`
                    api.downloadBlob(text, filename, 'text/x-diff')
                  }}
                >
                  <Download size={16} /> Download Fix (.diff)
                </Button>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  )
}

function ErrorState({ message, retry }: any) {
  const navigate = useNavigate()
  return (
    <div className="grid min-h-[60vh] place-items-center text-center p-4">
      <div className="max-w-lg">
        <div className="mx-auto grid size-12 place-items-center rounded-2xl bg-[var(--danger-soft)] text-[var(--danger)]">
          <XCircle size={23} />
        </div>
        <h1 className="mt-4 text-xl font-semibold">Unable to complete scan</h1>
        <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{message}</p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <Button onClick={() => navigate('/scans/new')} variant="primary">
            Start a new scan
          </Button>
          <Button onClick={retry} variant="secondary">
            Try again
          </Button>
        </div>
      </div>
    </div>
  )
}

function HistoryView() {
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    api.listScans()
      .then((data) => { if (active && Array.isArray(data)) setHistory(data) })
      .catch(() => {})
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  return (
    <>
      <PageHeading eyebrow="Workspace" title="Scan History" description="All completed and active security scans persisted in the backend database." />
      {loading ? (
        <div className="flex justify-center p-12 text-[var(--muted)]"><LoaderCircle className="animate-spin" size={24} /></div>
      ) : history.length === 0 ? (
        <EmptyState title="No scan history yet" description="Start a scan using a public GitHub repository to view historical security audits." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--panel)]">
          <div className="divide-y divide-[var(--border)]">
            {history.map((scan) => (
              <Link key={scan.scan_id} to={`/scans/${scan.scan_id}`} className="flex items-center justify-between p-5 transition hover:bg-[var(--panel-hover)]">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm font-semibold text-white">{scan.repository_name || scan.owner ? `${scan.owner}/${scan.repository_name}` : scan.repository_url}</span>
                    <span className={cx('inline-flex rounded-full px-2.5 py-0.5 text-[10px] font-semibold capitalize', scan.status === 'completed' ? 'bg-[var(--success-soft)] text-[var(--success)]' : (scan.status === 'failed' ? 'bg-[var(--danger-soft)] text-[var(--danger)]' : 'bg-[var(--warning-soft)] text-[var(--warning)]'))}>
                      {scan.status}
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-[var(--muted)]">
                    Scan ID: <span className="font-mono">{scan.scan_id}</span> • {scan.findings_count} findings • {scan.created_at ? new Date(scan.created_at).toLocaleString() : 'Recent'}
                  </div>
                </div>
                <ChevronRight size={18} className="text-[var(--muted)]" />
              </Link>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

function SettingsView() {
  const [status, setStatus] = useState<string>('Testing...')
  const [ok, setOk] = useState<boolean | null>(null)

  const check = () => {
    setStatus('Testing connection to ' + api.baseUrl + '/health...')
    api.getHealth()
      .then((res: any) => {
        setStatus(`Connected successfully! Server response: ${JSON.stringify(res)}`)
        setOk(true)
      })
      .catch((err: any) => {
        setStatus(`Connection failed: ${err.message}`)
        setOk(false)
      })
  }

  useEffect(() => { check() }, [])

  return (
    <>
      <PageHeading eyebrow="Configuration" title="Settings & Connectivity" description="Verify API base URLs, environment parameters, and backend health." />
      <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6 max-w-xl space-y-4">
        <div>
          <div className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wider mb-1">Backend Base URL</div>
          <div className="font-mono text-sm bg-[var(--bg)] p-3 rounded-xl border border-[var(--border)] text-white">{api.baseUrl}</div>
        </div>
        <div>
          <div className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wider mb-1">Health Status</div>
          <div className={cx('p-3 rounded-xl border text-xs font-mono', ok ? 'border-green-800 bg-green-950/40 text-green-400' : 'border-amber-800 bg-amber-950/40 text-amber-300')}>
            {status}
          </div>
        </div>
        <Button onClick={check} variant="secondary" className="mt-2">Re-check Connection</Button>
      </div>
    </>
  )
}

function DocsView() {
  return (
    <>
      <PageHeading
        eyebrow="Deliverables"
        title="Documentation & Downloadable Files"
        description="Download PRD files, System Design specifications, and security audit reports."
      />
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6 flex flex-col justify-between">
          <div>
            <div className="size-11 rounded-xl bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-center text-yellow-400 mb-4">
              <FileText size={22} />
            </div>
            <h2 className="text-lg font-bold text-white">Product Requirements Document (PRD)</h2>
            <p className="mt-2 text-sm text-[var(--muted)] leading-relaxed">
              Complete product specifications including multi-agent architecture, functional requirements (FR-01 to FR-09), threat models, and user workflow criteria.
            </p>
          </div>
          <div className="mt-6">
            <a
              href={api.downloadPrdUrl}
              download="DevFlow-AI-PRD.md"
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-[var(--accent)] text-white px-4 py-2.5 text-sm font-semibold transition hover:bg-[var(--accent-hover)] w-full"
            >
              <Download size={16} /> Download PRD (.md)
            </a>
          </div>
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--panel)] p-6 flex flex-col justify-between">
          <div>
            <div className="size-11 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
              <Layers size={22} />
            </div>
            <h2 className="text-lg font-bold text-white">System Design & Architecture</h2>
            <p className="mt-2 text-sm text-[var(--muted)] leading-relaxed">
              Detailed system architecture diagrams, agent component models, database schemas, security boundaries, and API contract specifications.
            </p>
          </div>
          <div className="mt-6">
            <a
              href={api.downloadSystemDesignUrl}
              download="DevFlow-AI-System-Design.md"
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--panel-hover)] text-white px-4 py-2.5 text-sm font-semibold transition hover:border-[var(--accent)] w-full"
            >
              <Download size={16} /> Download System Design (.md)
            </a>
          </div>
        </div>
      </div>
    </>
  )
}

function NotFound() {
  return <ErrorState message="This page does not exist in the DevFlow workspace." retry={() => window.location.assign('/')} />
}

export const router = createBrowserRouter([
  { path: '/', Component: HeroPage },
  { path: '/', Component: Shell, children: [
    { path: 'dashboard', Component: Overview },
    { path: 'scans/new', Component: NewScan },
    { path: 'scans/:scanId', Component: ScanResults },
    { path: 'history', Component: HistoryView },
    { path: 'findings', Component: Overview },
    { path: 'docs', Component: DocsView },
    { path: 'settings', Component: SettingsView },
  ]},
  { path: '*', Component: NotFound },
])
