# 🚀 MIMIC – Quick Launch Checklist

## 📋 Pre‑flight Checks
- [ ] **FFmpeg** installed and on `PATH` (`ffmpeg -version`).
- [ ] **Python 3.10+** installed (`python --version`).
- [ ] **Node.js 18+** installed (`node --version`).
- [ ] **Gemini API key** ready.

## 🛠️ Backend Setup (Terminal 1)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
# .env (create if missing)
#   GEMINI_API_KEY=your_key_here
#   FRONTEND_URL=http://localhost:3000
python main.py   # runs on http://localhost:8000
```
- Verify health endpoint: `curl http://localhost:8000/health` → `{ "status": "healthy" }`.
- Ensure CORS allows `http://localhost:3000`.

## 🎨 Frontend Setup (Terminal 2)
```powershell
cd frontend
npm install
# .env.local (create if missing)
#   NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev   # runs on http://localhost:3000
```
- Open the URL and confirm the landing page loads.

## 🔗 End‑to‑End Integration Test
1. Open **http://localhost:3000**.
2. Navigate to **Upload**.
3. Choose a reference video from `data/samples/reference/`.
4. Choose 2‑5 clips from `data/samples/clips/`.
5. Click **Generate** and watch the progress bar. (FFmpeg scene detection → Gemini analysis → Render).
6. When finished, verify the side‑by‑side comparison and download the result.

*(Updated Jan 19, 2026 - 22:20 PM)*

## � Common Issues & Fixes
- **Gemini model not found** – double‑check the API key and that your Gemini 3 access is enabled.
- **FFmpeg not found** – ensure the binary is on `PATH` or reinstall.
- **WebSocket connection fails** – confirm `FRONTEND_URL` matches the backend CORS setting and both servers are running.
- **Port already in use** – kill the existing process (`lsof -ti:8000 | xargs kill -9` for backend, similar for frontend).

## ✅ Ready to Demo
When all checkboxes are green, the system is ready for a live demo or further development.
