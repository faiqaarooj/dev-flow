export interface RepositoryMeta {
  owner: string
  name: string
  ref?: string | null
}

export interface ScanStatusResponse {
  scan_id: string
  id?: string
  status: 'queued' | 'running' | 'completed' | 'completed_with_warnings' | 'failed' | string
  repository: RepositoryMeta
}

export interface ScanSummary {
  scan_id: string
  id?: string
  repository_url: string
  owner?: string | null
  repository_name?: string | null
  ref?: string | null
  status: 'queued' | 'running' | 'completed' | 'completed_with_warnings' | 'failed' | string
  created_at: string
  error_message?: string | null
  findings_count?: number
  high_count?: number
  medium_count?: number
  low_count?: number
  summary?: Record<string, any>
}

export interface Finding {
  finding_id: string
  id?: string
  scan_id?: string
  source_type?: 'bandit' | 'ai_review' | 'combined'
  rule_id?: string
  title?: string
  message?: string
  severity?: 'HIGH' | 'MEDIUM' | 'LOW' | string
  priority?: string
  confidence?: string
  file_path?: string
  line_start?: number
  line_end?: number
  line_number?: number
  evidence?: string
  code_snippet?: string
  rationale?: string
  explanation?: string
  remediation?: string
  cwe?: string
  manual_review_required?: boolean
}

export interface CoverageData {
  files_discovered: number
  files_analyzed: number
  files_skipped: number
  warnings: string[]
}

export interface ScanDetails {
  scan_id: string
  id?: string
  status: 'queued' | 'running' | 'completed' | 'completed_with_warnings' | 'failed' | string
  repository_url?: string
  repository_name?: string
  files_analyzed?: number
  coverage?: CoverageData
  stages?: Record<string, string>
  findings: Finding[]
  patch_proposals?: PatchProposal[]
  created_at?: string
  error_message?: string | null
  summary?: Record<string, any>
}

export interface PatchProposal {
  proposal_id: string
  id?: string
  finding_id: string
  scan_id?: string
  status?: string
  target_path?: string
  file_path?: string
  diff?: string
  patch?: string
  explanation?: string
  review_notes?: string[]
  created_at?: string
  verification?: string
  verificationEvidence?: string
}

export interface RescanPayload {
  proposal_id: string
  finding_id?: string
  patch?: string
  patch_diff?: string
}

export interface VerificationResult {
  verification_id: string
  proposal_id: string
  status: 'resolved' | 'still_detected' | 'unverified' | string
  checks_run: string[]
  evidence: string
  limitations: string[]
}

export interface ApiClient {
  baseUrl: string
  getHealth: () => Promise<{ status: string; version?: string }>
  listScans: () => Promise<ScanSummary[]>
  startScan: (repositoryUrl: string, ref?: string | null) => Promise<ScanStatusResponse>
  getScan: (scanId: string) => Promise<ScanDetails>
  suggestFix: (scanId: string, findingId: string) => Promise<PatchProposal>
  rescanPatch: (scanId: string, payload: RescanPayload) => Promise<VerificationResult>
  downloadBlob: (content: string, filename: string, mimeType?: string) => void
  downloadPrdUrl: string
  downloadSystemDesignUrl: string
  downloadAuditReportUrl: string
  getPrdUrl: (scanId?: string | null) => string
  getSystemDesignUrl: (scanId?: string | null) => string
  getAuditReportUrl: (scanId?: string | null) => string
  getDocDownloadUrl: (slug: string, scanId?: string | null) => string
  getScanReportUrl: (scanId: string) => string
  getPatchDownloadUrl: (scanId: string, proposalId: string) => string
  getDocsList: (scanId?: string | null) => Promise<{ documents: any[] }>
  getDocContent: (slug: string, scanId?: string | null) => Promise<any>
}

export const api: ApiClient
