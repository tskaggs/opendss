# OpenDSS Field Dashboard

Monorepo for an agronomic field dashboard: a **FastAPI** backend that aggregates NASA POWER weather, SoilGrids soil properties, and a mocked SMAP soil moisture signal, plus a **Nuxt 4** desktop-style UI with a map, metrics, agronomic alerts, and 7-day charts.

## Repository layout

| Path | Description |
|------|-------------|
| [`backend/`](backend/) | FastAPI app (`app/`), Python dependencies in [`backend/requirements.txt`](backend/requirements.txt) |
| [`frontend/`](frontend/) | Nuxt 4 app using the `app/` directory structure, Nuxt UI, Leaflet, vue-chartjs |

## Prerequisites

- **Backend (local):** Python 3.11 or newer (3.12 recommended)
- **Frontend:** [Node.js](https://nodejs.org/) and [pnpm](https://pnpm.io/)
- **Optional:** Docker and Docker Compose, for running the API in a container

## Configuration

### Frontend

Copy [`.env.example`](.env.example) to `frontend/.env` and adjust if needed:

- `NUXT_PUBLIC_API_BASE` — Base URL of the FastAPI service (default `http://127.0.0.1:8000`). The browser calls this URL; keep it aligned with wherever the API is listening.

### Backend

Copy [`backend/.env.example`](backend/.env.example) to `backend/.env` when running `uvicorn` from `backend/` (optional; defaults match local dev).

| Variable | Purpose |
|----------|---------|
| `ENVIRONMENT` | `development` (default) or `production`. In production, interactive API docs (`/docs`) and the OpenAPI JSON are disabled. |
| `CORS_ORIGINS` | Comma-separated browser origins allowed to call the API (no spaces). Set this to your deployed frontend origin in production. |
| `TRUSTED_HOSTS` | Optional comma-separated `Host` values when the API is behind a reverse proxy. Leave empty to disable host checking. |
| `RATE_LIMIT_ANALYZE` | Limit for `POST /analyze` (slowapi format, default `60/minute`). |

Never commit real secrets. `.env` files are listed in [`.gitignore`](.gitignore).

## Backend (FastAPI)

### Local development

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Health check: `GET http://127.0.0.1:8000/health`
- Analysis: `POST http://127.0.0.1:8000/analyze` with JSON body `{ "lat": <number>, "lng": <number> }`

The API applies baseline security headers, configurable CORS, optional trusted hosts, and rate limiting on `/analyze`. See [`backend/app/main.py`](backend/app/main.py) and [`backend/app/core/config.py`](backend/app/core/config.py).

### Docker

Build and run the API in a consistent environment (see [`backend/Dockerfile`](backend/Dockerfile); the image runs as a non-root user):

```bash
docker build -t opendss-backend ./backend
docker run --rm -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e CORS_ORIGINS=https://your-frontend.example \
  opendss-backend
```

Or from the repo root with Compose (see [`docker-compose.yml`](docker-compose.yml) for optional `environment` overrides):

```bash
docker compose up --build
```

Use the same `NUXT_PUBLIC_API_BASE=http://127.0.0.1:8000` when the frontend runs on your machine and the API is published on port 8000.

**Docker image looks stale?** Compose may reuse cached layers. After changing `backend/` code or `requirements.txt`, run:

```bash
docker compose build --no-cache backend && docker compose up -d backend
```

Confirm the running container has the almanac-enabled schema: `GET /health` should return `"analyze_includes_almanac": true`. Then `POST /analyze` JSON should include an `almanac` object.

**`/health` missing `health_schema` / `analyze_includes_almanac`?** You are not reaching the Docker container.

On macOS it is common to run **`uvicorn` on the host** and **Docker** at the same time. `lsof` may show **two** listeners, for example:

- **`Python`** on **`127.0.0.1:8000`** — local FastAPI (IPv4 only).
- **`com.docker`** on **`*:8000`** — published container port.

**`curl http://127.0.0.1:8000`** uses **IPv4** to the loopback address, so traffic goes to **Python**, not Docker. That is why you still see an old `/health` body even after rebuilding the image.

**Fix (pick one):**

1. **Stop the host API** so Docker owns `:8000` for IPv4: find the PID with `lsof -nP -iTCP:8000 -sTCP:LISTEN`, then stop that terminal or `kill <PID>` (only the `Python` / `uvicorn` process, not Docker). Then `curl -s http://127.0.0.1:8000/health` should show `health_schema` and `analyze_includes_almanac`.

2. **Keep host uvicorn and use another port for Docker:** copy [`docker-compose.override.example.yml`](docker-compose.override.example.yml) to `docker-compose.override.yml` (gitignored), run `docker compose up -d backend`, then call **`http://127.0.0.1:8001`** for the container API and set `NUXT_PUBLIC_API_BASE=http://127.0.0.1:8001` in `frontend/.env`.

3. Recreate after code changes:  
   `docker compose down && docker compose build --no-cache backend && docker compose up -d backend`

4. Confirm the container: `docker ps --filter name=opendss-backend-api`

## Frontend (Nuxt)

```bash
cd frontend
pnpm install
pnpm dev
```

The dev server defaults to port 3000. Open the app in the browser; the field dashboard lives at `/field-dashboard` (the home route redirects there).

**Units:** On the field dashboard, use **Measurements** (Metric vs Standard US) for wind and precipitation, and **Temperature** (Celsius vs Fahrenheit) for soil temperature. Choices are stored in the browser (`localStorage`); the API still returns metric data and the UI converts for display.

Production build:

```bash
pnpm build
pnpm preview   # optional local preview of the production build
```

## API overview

The `POST /analyze` response includes location, weather (including wind, humidity, short-range precipitation context), mocked soil moisture with a 7-day series, soil temperature series, SoilGrids-derived properties when the upstream service is available, and agronomic fields (plant readiness and spray window classification).

External data services may be unavailable or rate-limited; the backend is written to degrade gracefully (for example, fallback weather data or null soil properties).

## Security and production

- **CORS:** Restrict `CORS_ORIGINS` to known frontend origins. Do not use `*` with credentials.
- **Docs:** With `ENVIRONMENT=production`, `/docs`, `/redoc`, and `/openapi.json` are disabled to reduce attack surface.
- **Secrets:** Do not commit `.env` files; use your host or orchestrator’s secret store in production.
- **Third-party APIs:** The backend calls external HTTP APIs only (NASA POWER, SoilGrids). It does not proxy arbitrary URLs from clients.
- **Reporting issues:** See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Troubleshooting

### Frontend cannot reach the API (“Failed to fetch”, network errors, or Analyze never succeeds)

- Confirm the backend is running (`curl http://127.0.0.1:8000/health` should return `{"status":"ok"}`).
- Set `NUXT_PUBLIC_API_BASE` in `frontend/.env` to the exact origin the browser must use (including scheme and port), e.g. `http://127.0.0.1:8000`. Restart `pnpm dev` after changing env vars.
- If the UI is opened as `http://localhost:3000` but `NUXT_PUBLIC_API_BASE` uses `127.0.0.1`, that is usually still fine for same-machine dev; if you see CORS errors, align origins or add your dev origin to `CORS_ORIGINS` in [`backend/.env.example`](backend/.env.example) (copied to `backend/.env`).

### CORS errors in the browser console

- Ensure your frontend origin is included in `CORS_ORIGINS` (comma-separated, no spaces). Restart the API after changes.

### HTTP 429 on `/analyze`

- The API rate-limits `POST /analyze` (default `60/minute` per client IP). Increase `RATE_LIMIT_ANALYZE` in `backend/.env` for local testing if needed, or wait before retrying.

### Soil texture / SoilGrids fields are empty

- The ISRIC SoilGrids API can return errors or maintenance responses (for example HTTP 503). The backend catches failures and leaves soil property fields null. Retry later or verify the service status; coordinates far offshore may also return sparse data.

### Weather metrics look odd or use fallback data

- NASA POWER may be slow or temporarily unavailable; the backend falls back to synthetic weather so the API still responds. Check backend logs for HTTP errors from the POWER endpoints.

### Docker: “port is already allocated” or API not reachable on 8000

- Another process may be using port 8000. Stop the conflicting service, or map a different host port: `docker run --rm -p 9000:8000 opendss-backend` and set `NUXT_PUBLIC_API_BASE=http://127.0.0.1:9000`.
- For Compose, adjust the `ports` mapping in [`docker-compose.yml`](docker-compose.yml) similarly.

### Docker daemon not running (CLI errors connecting to the socket)

- Start Docker Desktop (or your container runtime) and retry `docker build` / `docker compose up`.

## License

This project is licensed under the [MIT License](LICENSE).
