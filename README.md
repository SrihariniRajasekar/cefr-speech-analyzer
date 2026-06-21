# 🎙️ CEFR Speech Analyzer

A multi-LLM communication evaluation system that scores spoken English proficiency using the CEFR (Common European Framework of Reference) standard. Records or accepts audio, transcribes it, and scores the speaker across 12 communication parameters using multiple AI models simultaneously — then compares which model judges most consistently.

---

## ✨ Features

- 🎤 Record audio directly in-browser or upload a file
- 📝 Automatic transcription via Groq Whisper Large V3 (cloud-based, no local GPU needed)
- 🤖 Scores evaluated in parallel by **3 different LLMs**: Groq (Llama 3.3 70B), Gemini 2.5 Flash Lite, Ollama (Gemma4 31B)
- 📊 12 CEFR communication parameters scored 0–5 each (Vowel Sounds, Consonant Sounds, Word Stress, Intonation, Sentence Construction, Comprehensibility, Clarity, Voice Projection, Filler Avoidance, Confidence, Rate of Speech, Thought Flow)
- 🏅 CEFR level classification (A1–C2) based on consensus score
- 📈 Visual dashboard — radar charts, gauges, grouped bar charts comparing LLM scores
- 💡 AI-generated personalized improvement tips for weak areas
- 📋 Curated speaking scenarios (professional / academic / general) to prompt the user
- 📥 Auto-logging of every session to an Excel sheet, downloadable from the app
- 🔒 API keys stored server-side only — never exposed to the frontend

---

## 🏗️ Architecture

```
┌────────────┐        ┌─────────---─┐        ┌───────────┐
│  Streamlit │  HTTP  │    Flask    │  HTTPS │ External  │
│  Frontend  │ ──────►│   Backend   │ ──────►│ APIs      │
│  (UI only) │ ◄──────│ (all logic) │ ◄──────│(Groq/Gemini│
└────────────┘        -────────----─┘        │  Ollama)  │
                                             └───────────┘
```

- **Frontend (`frontend/app.py`)** — Streamlit UI. Handles audio input (record/upload), displays results, charts, and improvement tips. Contains no business logic or API keys.
- **Backend (`backend/app.py`)** — Flask API. Handles transcription, prompt building, parallel LLM scoring (via threading), Excel logging, and serves the results file for download.

### Data Flow

**Audio Input** → **Groq Whisper (Transcription)** → **Feature Extraction** → **CEFR Prompt** → **3 LLMs Scored in Parallel** → **Averaged Scores** → **Excel Storage + Dashboard Display**

---

## 🚀 Setup

### 1. Clone the repository
```bash
git clone https://github.com/SrihariniRajasekar/cefr-speech-analyzer.git
cd cefr-speech-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** If you hit PyTorch/Whisper-related errors, this project uses **Groq's cloud Whisper API** for transcription, so no local PyTorch/GPU setup is required.

### 4. Set up API keys

Copy the example env file and fill in your own free API keys:
```bash
cd backend
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
```

Edit `backend/.env`:
```
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
MISTRAL_API_KEY=your_mistral_key_here
OLLAMA_API_KEY=your_ollama_key_here
```

**Free API key sources:**
| Service | Link                                 |
|---------|--------------------------------------|
| Groq    | https://console.groq.com             |
| Gemini  | https://aistudio.google.com          |
| Mistral | https://console.mistral.ai           |
| Ollama  | https://ollama.com/settings/keys     |

You don't need all 4 — the app works with however many you provide (minimum 1).

### 5. Run the backend
```bash
cd backend
python app.py
```
Runs on `http://127.0.0.1:5000`

### 6. Run the frontend (in a new terminal)
```bash
cd frontend
streamlit run app.py
```
Opens automatically at `http://localhost:8501`

---

## 📂 Project Structure

```
cefr-speech-analyzer/
├── backend/
│   ├── app.py              # Flask API — transcription, scoring, Excel logging
│   ├── .env.example        # Template for required API keys
│   └── .env                # Your actual keys (gitignored)
├── frontend/
│   └── app.py               # Streamlit UI
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📊 CEFR Score Ranges

| Level | Score (out of 60) | Description        |
|-------|-------------------|--------------------|
| A1    | 0–10              | Beginner           |
| A2    | 11–20             | Elementary         |
| B1    | 21–30             | Intermediate       |
| B2    | 31–40             | Upper Intermediate |
| C1    | 41–50             | Advanced           |
| C2    | 51–60             | Proficient         |

---

## 🛠️ Tech Stack

| Component      | Technology                  |
|----------------|-----------------------------|
| Frontend       | Streamlit                   |
| Backend        | Flask                       |
| Transcription  | Groq Whisper Large V3 Turbo |
| LLMs           | Groq (Llama 3.3 70B),       |
|                | Gemini 2.5 Flash Lite,      |   
|                | Ollama (Gemma4 31B)         |
| Charts         | Plotly                      |
| Data Storage   | openpyxl (Excel)            |

---

## 🧭 Roadmap

- [ ] Admin dashboard to filter/export historical results
- [ ] Phoneme-level acoustic analysis for more accurate pronunciation scoring
- [ ] Cloud deployment for remote access
- [ ] Support for additional LLM providers as free tiers become available

---

## 👤 Author

Built by Sriharini R 