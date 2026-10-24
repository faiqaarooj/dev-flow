# DevFlow AI frontend

Repository security scanning dashboard built with React, Vite, Tailwind CSS, React Router, and Lucide.

## Start locally

1. Install dependencies: `pnpm install`
2. Copy `.env.example` to `.env` and update `VITE_API_BASE_URL` if needed.
3. Start the frontend: `pnpm dev`

The configured backend must expose the scan, fix suggestion, and patch re-scan endpoints described in the product API contract. API failures are shown in the interface; the frontend does not fabricate scan results.
