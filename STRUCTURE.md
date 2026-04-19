Suggested repo structure!

Here is the cleanest way to structure your repository for a Next.js and FastAPI stack.

## The Monorepo Structure

Create a master folder for your project, and inside it, separate the stack into two distinct directories.
```
comparative-legal-engine/
├── frontend/                 # (Next.js + Tailwind)
│   ├── app/                  # Your pages and routing
│   ├── components/           # UI components (Tabs, Columns, Loaders)
│   ├── package.json          # Node dependencies
│   └── .env.local            # NEXT_PUBLIC_API_URL lives here
│
├── backend/                  # (FastAPI + Python)
│   ├── api/                  # Your route logic
│   ├── schemas.py            # Pydantic models (HanafiOutput, etc.)
│   ├── main.py               # The FastAPI server entry point
│   ├── manage_data.py        # The RAG setup/upload script you wrote
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # GEMINI_API_KEY lives here
│
├── .gitignore                # Combined ignore rules for the whole repo
├── README.md                 # Your polished project overview
└── plan.md                   # The architectural blueprint for the team
```

## 3 Rules for Making the Monorepo Work

1. **The "Two Terminal" Rule**

Because you have two different environments running simultaneously, you will always need two terminal windows open when developing locally:

- Terminal 1: cd frontend → npm run dev (Runs on localhost:3000)

- Terminal 2: cd backend → source .venv/bin/activate → fastapi dev main.py (Runs on localhost:8000)

2. **The Combined .gitignore**

Since the root of your project now houses both JavaScript and Python, your single .gitignore file needs to block the heavy folders for both environments. Ensure it includes:

```
# Node
frontend/node_modules/
frontend/.next/

# Python
backend/.venv/
backend/__pycache__/
*.pyc

# Security
.env
.env.local
```

3. **The Deployment "Root Directory" Trick**

This is the most common stumbling block for monorepos, but Vercel and Render make it incredibly easy. When you connect your GitHub repository to these services, you must tell them exactly which folder to look at.

- In Vercel: Go to Project Settings -> Build & Development Settings -> Root Directory, and type frontend. Vercel will now completely ignore the Python backend.

- In Render: When setting up your Web Service, look for the Root Directory field and type backend. Render will now completely ignore the Next.js frontend.