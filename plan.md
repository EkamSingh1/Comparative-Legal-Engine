# Architecture Plan

## Runtime Shape

- `frontend/`: Next.js App Router UI deployed on Vercel.
- `backend/`: FastAPI JSON API deployed on Render.
- `sources/`: PDF corpus uploaded to Gemini File Search using `backend/manage_data.py`.

## Request Flow

1. A user submits one scenario in the Next.js UI.
2. The frontend sends `POST /api/analyze` to the FastAPI backend.
3. The backend runs four Gemini File Search calls, one for each school:
   - Hanafi: Quran, Sahih Bukhari, A Digest of Moohummudan Law.
   - Maliki: Quran, Al-Muwatta of Imam Malik.
   - Shafi'i: Quran, Sahih Bukhari.
   - Hanbali: Quran, Musnad Ahmad Bin Hanbal, Al-Muwatta of Imam Malik.
4. The backend runs one synthesis call with no File Search.
5. The frontend renders final rulings, evidence, reasoning, and the synthesis.

## Guardrails

- The backend enforces a 4,000 character scenario limit.
- Provider output is validated through Pydantic schemas before returning to the UI.
- The API includes an in-process rate limiter tuned for the documented free-tier limits.
- Every result is framed as educational only, not legal advice and not a fatwa.

## Deployment

- Vercel root directory: `frontend`.
- Render root directory: `backend`.
- Configure `NEXT_PUBLIC_API_URL` in Vercel with the Render API URL ending in `/api`.
- Configure `GEMINI_API_KEY`, `GEMINI_FILE_SEARCH_STORE`, and `ALLOWED_ORIGINS` in Render.
