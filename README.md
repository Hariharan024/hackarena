# சகி · Sakhi — The Invisible Woman (v6)

A voice-first guide that takes a first-time woman user, with **no English, no tech skills and no one to ask**, from
"I don't know what I can get" to a **personal document checklist for one government service**:
the Tamil Nadu monthly pensions for women without a husband's support (₹1,200/month).

| Her situation | Scheme |
|---|---|
| Husband died | Destitute Widow Pension (18+) |
| Husband left / divorced / court-separated | Destitute / Deserted Wives Pension (30+; deserted ≥ 5 years, or divorced / court separation certificate) |
| Never married | Pension to Poor Unmarried Women (50+) |

Plus, for all: property worth no more than ₹1,00,000 (a free government house doesn't count).

## How it works
1. **Sakhi speaks first** (one big button), in Tamil. English is one tap away.
2. One question at a time. Every question can be answered **by voice, by touching a picture/big button, or by typing**.
3. Answers become small "what I understood" chips she can touch to change.
4. A **deterministic rules engine** (`eligibility.py`) decides — never the AI. Result says "you *may* get…", never "you are eligible".
5. She gets a tick-off **document checklist**, 3 next steps (go to e-Sevai), and can **print** the page or **send it on WhatsApp**
   to show the officer / a relative.

**Gemini's job (optional):** (a) turn messy spoken Tamil/Tanglish/English into a few validated fields when the built-in parser
can't, (b) a Tamil voice for devices without one. Gemini never writes scheme facts; its output is whitelisted and range-checked
(`gemini_service.sanitize_extraction`). With no API key everything still works offline.

**Privacy:** the server is stateless. The profile lives only in the browser tab; nothing is stored or logged.

## Run
Windows: `.\run.ps1` · macOS/Linux: `./run.sh` → open **http://localhost:8000**
(builds the React app, then FastAPI serves UI + API from one URL). Put `GEMINI_API_KEY` in `backend/.env` for the Gemini features.

Dev mode with hot reload: `cd backend && uvicorn main:app --reload` and, in another terminal, `cd frontend && npm run dev` → http://localhost:5173.

## Test
```
cd backend  && pytest -q                                   # 70 tests: parser, rules + age/year boundaries, API journeys, Gemini safety
cd frontend && npm test                                    # UI tests (mocked server)
cd frontend && SAKHI_E2E_URL=http://127.0.0.1:8000 npm test   # + real UI against the real running backend
```

## Before you demo / deploy — please read
- **Use Chrome or Edge (Android Chrome is best).** Voice *input* needs Chrome's speech recognition; Safari/Firefox fall back to buttons + typing, which fully work.
- **Microphone needs HTTPS** on any host except `localhost`.
- **Tamil voice output:** Android Chrome has a Tamil voice. Many Windows PCs do not. If the browser has none, Sakhi automatically uses Gemini's
  voice when a key is set (`/api/tts`), otherwise shows the text on screen. Test on the actual demo device.
- **Re-verify the facts** in `backend/scheme_data.py` against the two official pages listed at its top (last checked 2026-10-01).
  Amounts change by government order.
- **Have a native Tamil speaker read `backend/messages.py`** and the document names in `scheme_data.py` once.
- The Gemini calls are checked against the SDK and fail safe, but could not be exercised against Google's live API in the build environment — try one real message with your key.

## Extend
- New scheme: add an entry to `SCHEMES` + its documents (data only). New language: add a column to `messages.py`, `scheme_data.py`, `ui.js`.
- Next ideas: Kalaignar Magalir Urimai Thogai, ration-card help, Anganwadi/maternity benefits, a helpline hand-off, SMS/IVR for feature phones.

## Layout
```
backend/  scheme_data.py (verified facts) · eligibility.py (rules) · nlu.py (Tamil/Tanglish/English parser)
          dialogue.py (question flow) · gemini_service.py · messages.py (all words) · main.py (API)
frontend/ src/App.jsx (flow) · components.jsx (screens) · speech.js (voice in/out) · ui.js (labels)
```
