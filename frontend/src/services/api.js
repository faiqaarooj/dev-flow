const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL !== undefined
    ? import.meta.env.VITE_API_BASE_URL
    : import.meta.env.PROD
      ? ''
      : 'http://localhost:8000'
).replace(/\/$/, '')

async function request(path, options = {}) {
  const controller = new AbortController()
  const timeoutMs = options.timeout || 60000
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
    })

    const text = await response.text()
    let data = null
    if (text) {
      try {
        data = JSON.parse(text)
      } catch {
        throw new Error('The API returned an unreadable response.')
      }
    }

    if (!response.ok) {
      let message = `Request failed with status ${response.status}.`
      if (typeof data?.detail === 'string') {
        message = data.detail
      } else if (data?.detail?.error?.message) {
        message = data.detail.error.message
      } else if (data?.error?.message) {
        message = data.error.message
      } else if (data?.message) {
        message = data.message
      }
      throw new Error(message)
    }

    return data
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('The request timed out. Check the API server and try again.')
    }
    if (error instanceof TypeError) {
      throw new Error(
        `Unable to reach the DevFlow API at ${API_BASE_URL}. Confirm the backend server is running and CORS is enabled.`
      )
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
  }
}

export const api = {
  baseUrl: API_BASE_URL,
  getHealth: () => request('/health'),
  listScans: () => request('/api/scans'),
  startScan: (repositoryUrl, ref = null) =>
    request('/api/scans', {
      method: 'POST',
      body: JSON.stringify({ repository_url: repositoryUrl, ref }),
      timeout: 60000,
    }),
  getScan: (scanId) => request(`/api/scans/${encodeURIComponent(scanId)}`),
  suggestFix: (scanId, findingId) =>
    request(`/api/scans/${encodeURIComponent(scanId)}/fixes`, {
      method: 'POST',
      body: JSON.stringify({ finding_id: findingId }),
      timeout: 60000,
    }),
  rescanPatch: (scanId, payload) =>
    request(`/api/scans/${encodeURIComponent(scanId)}/rescan`, {
      method: 'POST',
      body: JSON.stringify(payload),
      timeout: 60000,
    }),
  downloadBlob: (content, filename, mimeType = 'text/plain;charset=utf-8') => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  },
  downloadPrdUrl: `${API_BASE_URL}/api/docs/prd`,
  downloadSystemDesignUrl: `${API_BASE_URL}/api/docs/system-design`,
  downloadAuditReportUrl: `${API_BASE_URL}/api/docs/audit-report`,
  getScanReportUrl: (scanId) => `${API_BASE_URL}/api/scans/${encodeURIComponent(scanId)}/export/report`,
  getPatchDownloadUrl: (scanId, proposalId) => `${API_BASE_URL}/api/scans/${encodeURIComponent(scanId)}/fixes/${encodeURIComponent(proposalId)}/download`,
}
