# Universal Language Translator & AI Chatbot

A modern, web-based translation tool featuring a sophisticated glassmorphic interface, 3D space particle background, local translation fallback, a Python FastAPI backend, and an integrated AI assistant (Darcy) powered by Google Gemini.

## Features

- **Real-Time Translation:** Translates text between multiple languages using Google Translate (with local API fallbacks).
- **Interactive AI Assistant (Darcy):** Conversational AI powered by the Gemini API (`gemini-2.5-flash` with rate-limit fallbacks).
- **Text-to-Speech (TTS):** Integrated voice synthesis for listening to source and translation texts.
- **Glassmorphic UI:** A visual design featuring smooth CSS animations, neon borders, and a responsive layout.
- **3D Starfield Background:** Immersive interactive background powered by Three.js.

---

## Directory Structure

```text
translation_tool/
│
├── index.html          # Frontend interface (HTML, CSS, Three.js, Vanilla JS)
├── main.py            # Python backend subsystem (FastAPI & API Integrations)
├── requirements.txt   # Python dependency list
├── .env.example       # Template for API credentials and configuration
├── .gitignore         # Files and directories ignored by Git (e.g. .env)
└── README.md          # Project documentation
```

---

## Running Locally

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- An internet connection for API services.
- A **Gemini API Key** (optional, required if using the AI Chatbot feature). Get one from [Google AI Studio](https://aistudio.google.com/).

### 2. Set Up the Backend
1. **Clone or download** this repository.
2. Open a terminal inside the project directory and create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows (CMD):** `venv\Scripts\activate`
   - **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   - **macOS/Linux:** `source venv/bin/activate`
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configure Environment Variables
1. Copy the `.env.example` file to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and replace `your_gemini_api_key_here` with your actual Google Gemini API key:
   ```text
   GEMINI_API_KEY=AIzaSy...
   ```
   *(Note: The `.env` file is listed in `.gitignore` so your private API key will not be committed to GitHub.)*

### 4. Run the Server
1. Start the backend server with:
   ```bash
   python main.py
   ```
2. The FastAPI backend will run on `http://127.0.0.1:8000`.

### 5. Launch the Frontend
1. Open the [index.html](index.html) file directly in any modern web browser, or serve it using a local development server (like VS Code's Live Server or `python -m http.server`).
2. Type your source text, choose target languages, and hit **Translate**.

---

## GitHub Deployment & Hosting Guide

### Can I host this directly on GitHub Pages?
**Not completely.**
- **GitHub Pages** is a static hosting platform. It can serve the `index.html` file (including its styling, CSS, and Three.js effects), but it **cannot run Python scripts** or host the FastAPI server (`main.py`).
- If you host the project only on GitHub Pages, the frontend will load, but clicking "Translate" will show a connection error because it tries to call `http://127.0.0.1:8000`, which runs on your local machine.

### Recommended Hosting Solutions

To host the live version of this app for free or at a low cost:

1. **Deploy Frontend & Backend Separately (Recommended):**
   - **Frontend:** Host the `index.html` on **GitHub Pages**, **Vercel**, or **Netlify** (which are free and optimized for static files).
   - **Backend:** Host the FastAPI backend (`main.py`) on a service like **Render**, **Railway**, **Fly.io**, or **Hugging Face Spaces**.
   - **Integration:** After deploying the backend, update `API_URL` in [index.html](index.html#L945) (line 945) from `http://127.0.0.1:8000/api/translate` to your deployed backend URL (e.g., `https://your-backend.onrender.com/api/translate`).

2. **Deploy the Complete Stack Together:**
   - You can deploy the entire repository to **Render** or **Railway** as a Python Web Service. 
   - You can modify `main.py` slightly to mount and serve the static `index.html` file directly from FastAPI. (e.g., using `fastapi.staticfiles.StaticFiles`). This way, visiting the backend URL in a browser will load the app automatically.
