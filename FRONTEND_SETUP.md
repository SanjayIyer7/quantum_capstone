# Q-Detect frontend setup

## Run locally

Open a terminal in the `frontend` directory and run:

```bash
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`). Keep the terminal running.

## Build for Vercel

Import the repository into Vercel and set **Root Directory** to `frontend`.

- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Optional environment variable: `VITE_API_URL` = the public URL of the deployed FastAPI backend (no trailing slash)

The frontend has a local preview mode so it can render without the API. Preview values are illustrative and labelled as preview data. To run real experiments online, deploy the Python/FastAPI backend separately and set `VITE_API_URL` to that public API URL. Ensure the backend allows requests from the Vercel domain via CORS.
