# Comparative Legal Engine

An educational website that demonstrates how the four primary Sunni schools of law can produce distinct legal outcomes when they apply different hierarchies of authority to the same scenario.

The tool is not legal advice, not a fatwa, and not a substitute for a qualified lawyer, scholar, or jurisdiction-specific authority. It is designed for a small number of users to explore methodological differences in a source-grounded way.

## What It Does

- Accepts a free-form case scenario from the user.
- Runs four school-specific agents against a Gemini File Search RAG store.
- Restricts each school to the source scope described below.
- Returns structured JSON for final rulings, cited evidence, and reasoning.
- Runs a synthesis pass that explains the core methodological divergence without introducing new evidence.
- Shows the result in a Next.js interface with tabs, source profiles, citations, and an educational disclaimer.

## Stack

- Frontend: Next.js App Router, TypeScript, Tailwind CSS.
- Backend: FastAPI, Pydantic, Google GenAI SDK.
- RAG: Gemini File Search over the PDFs in `sources/`.
- Deployment: Vercel for `frontend/`, Render for `backend/`.

## Source Hierarchies

The engine uses different sources of authority in Sunni Islamic law:

- The Quran: the foundational source of Islamic law.
- The Sunnah and Hadith: recorded sayings and actions of the Prophet.
- Ijma: scholarly or early-community consensus, depending on the school.
- Qiyas: analogical reasoning.
- Ijtihad and Istihsan: independent reasoning and juristic preference where permitted.

The four schools are configured as follows:

- Hanafi: Quran; mutawatir or highly reliable Hadith with emphasis on Sahih Bukhari; Qiyas and Istihsan; Ijma through the Hanafi legal tradition and A Digest of Moohummudan Law.
- Maliki: Quran; early Medinan practice and consensus with emphasis on Al-Muwatta of Imam Malik; Qiyas where aligned with Medinan practice.
- Shafi'i: Quran; Sahih Hadith with emphasis on Sahih Bukhari; narrow Qiyas only where text is absent; no Istihsan.
- Hanbali: Quran; Hadith with emphasis on Musnad Ahmad Bin Hanbal; Ijma of companions and earliest generations; minimal to no Qiyas.

## Included Sources

- The Quran: <https://www.clearquran.com/downloads/quran-english-translation-clearquran-edition-allah.pdf>
- Sahih Bukhari: <https://d1.islamhouse.com/data/en/ih_books/single/en_Sahih_Al-Bukhari.pdf>
- Fatawa 'Alamgiri through "A Digest of Moohummudan Law" by Baillie, Neil B.E.: <https://archive.org/details/dli.ministry.11968/mode/2up>
- Al-Muwatta of Imam Malik: <https://ia903201.us.archive.org/22/items/al-muwatta-of-imam-malik/Al-Muwatta%20of%20Imam%20Malik.pdf>
- Musnad Ahmad Bin Hanbal, volume 1: <https://archive.org/details/musnad-ahmad-bin-hanbal-english-translation/mode/2up>

## Repository Structure

```text
.
├── backend/                  # FastAPI API and Gemini integration
│   ├── api/                  # Routes
│   ├── core/                 # Config, prompts, limiter
│   ├── services/             # Provider service
│   ├── tests/                # Backend tests
│   ├── main.py               # FastAPI app
│   ├── manage_data.py        # Gemini File Search upload/list/test CLI
│   └── requirements.txt
├── frontend/                 # Next.js UI
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── sources/                  # PDF corpus
├── PROMPT.md                 # Original agent prompt spec
├── RATELIMITS.md             # Provider rate-limit notes
├── STRUCTURE.md              # Original structure recommendation
└── render.yaml               # Render backend blueprint
```

## Local Setup

### Backend

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set:

```bash
GEMINI_API_KEY=your-key
GEMINI_FILE_SEARCH_STORE=Islamic-Law-Sources
GEMINI_FILE_SEARCH_MODEL=gemini-3.1-flash-lite-preview
GEMINI_FILE_SEARCH_FALLBACK_MODELS=
GEMINI_SYNTHESIS_MODEL=gemini-3.1-flash-lite-preview
GEMINI_SYNTHESIS_FALLBACK_MODELS=
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Upload the source PDFs to Gemini File Search:

```bash
python backend/manage_data.py upload-all
python backend/manage_data.py list
```

Run the API:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open <http://localhost:3000>.

## API

### `GET /api/health`

Returns backend status, configured store, model names, and whether the API key is configured.

### `GET /api/schools`

Returns the school metadata and configured source scopes.

### `POST /api/analyze`

Request:

```json
{
  "scenario": "A buyer and seller complete an online sale, but the product description was ambiguous..."
}
```

Response:

```json
{
  "scenario": "...",
  "disclaimer": "...",
  "generated_at": "...",
  "synthesis": {
    "core_divergence": "...",
    "consensus_point": "..."
  },
  "schools": [
    {
      "school": "hanafi",
      "school_name": "Hanafi",
      "final_ruling": "...",
      "primary_evidence": [],
      "legal_reasoning": [],
      "methodology": {}
    }
  ]
}
```

## Rate Limits

One analysis uses five model calls:

- 4 File Search calls, one per school.
- 1 non-File Search synthesis call.

The backend defaults to `gemini-3.1-flash-lite-preview` and spaces provider calls by `4.2` seconds with a `12` calls-per-minute cap. Adjust these values in `backend/.env` if your model tier differs.

If a model returns temporary high-demand errors such as `503 UNAVAILABLE`, set comma-separated fallback models in `GEMINI_FILE_SEARCH_FALLBACK_MODELS` and `GEMINI_SYNTHESIS_FALLBACK_MODELS`. The backend retries the primary model first, then tries the configured fallbacks only for transient provider errors.

## Deployment

### Backend on Render

1. Create a Render web service from this repository.
2. Set root directory to `backend`.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
5. Set environment variables:
   - `GEMINI_API_KEY`
   - `GEMINI_FILE_SEARCH_STORE`
   - `GEMINI_FILE_SEARCH_MODEL`
   - `GEMINI_FILE_SEARCH_FALLBACK_MODELS` (optional)
   - `GEMINI_SYNTHESIS_MODEL`
   - `GEMINI_SYNTHESIS_FALLBACK_MODELS` (optional)
   - `ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app`

The root `render.yaml` contains the same baseline service definition.

### Frontend on Vercel

1. Create a Vercel project from this repository.
2. Set root directory to `frontend`.
3. Set `NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/api`.
4. Deploy.

## Development Checks

```bash
cd backend
python -m compileall main.py api core services schemas.py manage_data.py tests

cd ../frontend
npm run lint
npm run typecheck
npm run build
```
