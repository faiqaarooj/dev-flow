# DevFlow AI — System Design & Engineering Documentation Suite

**Release Version:** 2.2 — Production Operational Suite  
**Status:** 100% Implemented & Verified in Production  
**Lead Designer & Software Engineer:** Faiqa Arooj (Bugfolio, SE-Tech Society, Google Developer Groups)  
**Repository:** `https://github.com/faiqaarooj/dev-flow.git`  
**Live Application:** `https://dev-flow-iota-nine.vercel.app`  

---

## 1. Documentation Index

This directory contains the certified, production-grade system design and technical specifications for the DevFlow AI platform.

| Document | Name & Scope | Description |
|---|---|---|
| [**00-project-charter.md**](file:///Users/apple/Desktop/hackathon/docs/00-project-charter.md) | Project Charter & Mission | Product thesis, stakeholder matrix, core differentiators, and non-negotiables. |
| [**01-requirements.md**](file:///Users/apple/Desktop/hackathon/docs/01-requirements.md) | Functional & Non-Functional PRD | Detailed requirements matrix, performance SLAs, and security criteria. |
| [**02-system-architecture.md**](file:///Users/apple/Desktop/hackathon/docs/02-system-architecture.md) | System Architecture & Design | Monolith architecture, ingestion pipeline, sequence flows, ADRs, and deployment fixes. |
| [**03-agent-and-workflow-design.md**](file:///Users/apple/Desktop/hackathon/docs/03-agent-and-workflow-design.md) | Multi-Agent Coordination | 6 bounded agent roles, AST analysis, 3-tier AI patch hierarchy, and sandbox verification. |
| [**04-api-contracts.md**](file:///Users/apple/Desktop/hackathon/docs/04-api-contracts.md) | REST API & Protocol Specs | OpenAPI endpoints, request/response JSON schemas, and documentation streaming. |
| [**05-data-model.md**](file:///Users/apple/Desktop/hackathon/docs/05-data-model.md) | Data Model & SQLite DDL | Embedded SQLite 3 schema (`devflow.db`), indexes, ER diagrams, and WAL mode. |
| [**06-security-and-threat-model.md**](file:///Users/apple/Desktop/hackathon/docs/06-security-and-threat-model.md) | Security & STRIDE Threat Model | Zero-trust defenses, Zip-Slip path sanitization, quota bounds, and sandboxing. |
| [**07-implementation-roadmap.md**](file:///Users/apple/Desktop/hackathon/docs/07-implementation-roadmap.md) | Milestone Delivery Ledger | Complete verification ledger of all implemented platform milestones. |
| [**08-testing-and-quality-plan.md**](file:///Users/apple/Desktop/hackathon/docs/08-testing-and-quality-plan.md) | Quality Assurance & Test Ledger | 19 automated tests, test case matrix, and 529ms frontend production build metrics. |
| [**09-dnotifier-integration.md**](file:///Users/apple/Desktop/hackathon/docs/09-dnotifier-integration.md) | DNotifier Gateway Architecture | HMAC-SHA256 signature verification, event schemas, and fault tolerance. |
| [**10-demo-and-presentation-plan.md**](file:///Users/apple/Desktop/hackathon/docs/10-demo-and-presentation-plan.md) | Live Demo Runbook & Script | Step-by-step presentation sequence, tested repo targets, and defense answers. |
| [**SYSTEM_DESIGN.md**](file:///Users/apple/Desktop/hackathon/SYSTEM_DESIGN.md) | Comprehensive Root System Design | Master architectural specification available directly via `/api/docs/system-design`. |

---

## 2. Production Architecture Summary

DevFlow AI is an autonomous security auditing platform built for developers:
- **Frontend:** React 18 + Vite 8 SPA styled in minimalist dark aesthetic (`#1a1a1a` with `#f4c453` yellow accents) using Tailwind CSS and Framer Motion. Edge routing is protected by catch-all SPA rewrites.
- **Backend:** Python 3.9+ FastAPI ASGI application with dual-mode execution (local persistent uvicorn and synchronous serverless Vercel execution).
- **Static Analysis:** Bandit v1.7.9 AST visitor engine operating with zero dynamic code execution.
- **Remediation:** 3-tier patch engine (Gemini 2.0 Flash -> GPT-4o-mini -> deterministic offline rule heuristics).
- **Verification:** Ephemeral sandbox workspace re-scanning patches before human review.
- **Alerts:** Non-blocking asynchronous HMAC-signed event dispatch via DNotifier.
