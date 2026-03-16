# ReadmeAI — Frontend

The React frontend for **ReadmeAI**, a Google Hackathon project that analyses any GitHub repository and generates a clear, structured README using Gemini AI.

---

## 🗂️ Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── FeedbackForm.jsx      # Accuracy rating + comments form
│   │   ├── Header.jsx            # Sticky top nav — logo links back to home
│   │   ├── ReadmePreview.jsx     # Preview / Raw toggle with react-markdown
│   │   ├── ReadmeSidebar.jsx     # Sticky ToC built from README headings
│   │   ├── RepoInput.jsx         # GitHub URL input with validation
│   │   └── SummaryCard.jsx       # Generic info card
│   ├── pages/
│   │   ├── HomePage.jsx          # Landing page — hero, input, feature cards
│   │   └── ResultPage.jsx        # Results — sidebar + README preview + feedback
│   ├── services/
│   │   └── api.js                # REST calls + mock response (VITE_USE_MOCK)
│   ├── utils/
│   │   └── headings.js           # Markdown heading extractor + slugify
│   ├── App.jsx                   # BrowserRouter routes
│   ├── main.jsx
│   └── index.css                 # Tailwind directives
├── .env.example
├── tailwind.config.js
├── vite.config.js
└── package.json
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- npm 9+

### Install & run

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL of the backend REST API |
| `VITE_USE_MOCK` | `false` | Set to `true` to use mock data — no backend required |

> **Quick demo (no backend needed):**
> ```bash
> VITE_USE_MOCK=true npm run dev
> ```

---

## 🧭 Pages & Features

### `/` — Home
- GitHub repository URL input with client-side validation
- Feature cards describing what the tool analyses
- Navigates to `/result` on submit, passing the URL via router state

### `/result` — Results
- **Sticky sidebar** — table of contents auto-generated from README headings; clicking a heading switches to Preview mode and smooth-scrolls to the section
- **README preview** — VSCode-style **Preview / Raw** toggle
  - *Preview*: fully rendered markdown (headings, tables, code blocks, lists, badges)
  - *Raw*: dark terminal view of the raw markdown source
- **Copy to clipboard** — one click to copy the full markdown
- **↺ Regenerate** — re-runs the analysis; shows spinner while loading
- **Accuracy Feedback** — 👍 / 👎 rating + free-text comment form; collapses to a thank-you on submit (wired to `POST /api/feedback` when backend is ready)

---

## 🛠️ Tech Stack

| | |
|---|---|
| Framework | React 19 + Vite 8 |
| Styling | Tailwind CSS v3 |
| Routing | React Router DOM v7 |
| Markdown | react-markdown + remark-gfm |
| Build | Vite |

---

## 📡 API Integration

All backend calls live in [`src/services/api.js`](src/services/api.js).

**`summarizeRepo(repoUrl)`** — `POST /api/summarize`

```js
const result = await summarizeRepo('https://github.com/owner/repo');
// result: { repoName, summary, techStack, setupSteps, usageExamples, readme }
```

Set `VITE_API_BASE_URL` to point at your backend. When the backend is not yet available, set `VITE_USE_MOCK=true` to use the built-in mock that returns a fully populated response after a simulated 2-second delay.

---

## 📦 Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
