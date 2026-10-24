# DevFlow

We don't just detect vulnerabilities; we show developers how to fix them and verify that the problem is solved.

DevFlow AI is planned as a read-only security review workflow for public Python GitHub repositories. The project documents the intended architecture and currently includes an initial FastAPI backend scaffold.

## Backend setup

Requirements: Python 3.12 or newer.

From the `backend` directory, create and activate a virtual environment, then install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GEMINI_API_KEY` for Gemini-powered features. Keep `.env` local; it is ignored by Git. The key is not required to start the API.

Start the backend from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `/docs`. `GET /health` checks that the API process is running.

## Current implementation status

The backend is an early scaffold. Scan creation currently validates the repository URL and queues a scan record; it does not yet retrieve repository files or run the full Bandit/Gemini remediation workflow. The planning documents describe the target behavior and staged implementation roadmap.

## Security notes

- Never commit `.env` files, API keys, the local virtual environment, or generated databases.
- The intended workflow is read-only and must not execute submitted repository code.
- Scanner/AI failures and partial coverage must not be reported as a clean scan.
