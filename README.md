# 🍯 Agentic Honeypot for Scam Detection & Intelligence Extraction

An AI-powered honeypot system that engages with scammers in real-time, detects fraud attempts, and extracts actionable intelligence. Built with FastAPI and LangChain, using local LLMs for privacy-preserving conversations.

## 🎯 Overview

This system acts as a **digital honeypot** that:
- **Detects scam messages** using ML-based classification and keyword analysis
- **Engages scammers** with realistic human-like responses (mimics a tech-naive elderly person)
- **Extracts intelligence** including UPI IDs, phone numbers, bank accounts, and phishing links
- **Reports findings** via callback API for further analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Server                           │
│                         (app.py)                                │
├─────────────┬─────────────┬─────────────────┬──────────────────┤
│  Detector   │   Agent     │   Extractor     │ Session Manager  │
│(detector.py)│ (agent.py)  │  (extract.py)   │(session_manager) │
├─────────────┼─────────────┼─────────────────┼──────────────────┤
│ DistilBERT  │  Ollama     │  Regex-based    │  In-memory       │
│ Phishing    │  Llama 3.2  │  Pattern        │  Session Store   │
│ Classifier  │  (Local)    │  Matching       │                  │
└─────────────┴─────────────┴─────────────────┴──────────────────┘
```

## 📁 Project Structure

```
├── app.py              # FastAPI server & main endpoint
├── agent.py            # LLM-powered conversational agent
├── detector.py         # Scam detection with ML + keywords
├── extract.py          # Intelligence extraction (regex)
├── session_manager.py  # Session state management
├── requirements.txt    # Python dependencies
└── .env                # Environment variables (API_KEY)
```

## ⚙️ Components

### 1. Scam Detector (`detector.py`)
- Uses **DistilBERT** model fine-tuned for phishing detection
- Keyword-based reinforcement for India-specific scam patterns
- Strong indicators: OTP, UPI PIN, gift cards

### 2. Conversational Agent (`agent.py`)
- Powered by **Llama 3.2** (3B) via Ollama (runs locally)
- Persona: Elderly, tech-naive individual
- Per-session conversation memory for context retention

### 3. Intelligence Extractor (`extract.py`)
- Extracts: Bank accounts, UPI IDs, phone numbers, phishing URLs
- India-focused regex patterns
- Deduplication and normalization

### 4. Session Manager (`session_manager.py`)
- In-memory session tracking
- Confidence scoring and agent activation
- Automatic stale session cleanup (24h)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) installed with `llama3.2:3b-instruct-q4_K_M` model

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd Agentic-Honey-Pot-for-Scam-Detection-Intelligence-Extraction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Pull the Ollama model
ollama pull llama3.2:3b-instruct-q4_K_M
```

### Configuration

Create a `.env` file:
```env
API_KEY=your_secret_api_key
GUVI_CALLBACK_URL=https://your-callback-endpoint.com/api/result
```

### Run the Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns: `{"status": "ok"}`

### Process Scammer Message
```http
POST /honeypot/message
Content-Type: application/json
X-API-Key: your_secret_api_key

{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked! Share OTP to verify.",
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {}
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh dear, I'm worried. What OTP are you talking about? I don't understand these technical things very well."
}
```

## 🔍 How It Works

1. **Message Received** → API validates sender and API key
2. **Scam Detection** → ML model + keywords analyze the message
3. **Confidence Update** → Session confidence score adjusts based on detection
4. **Agent Activation** → When confidence ≥ 0.6, the AI agent engages
5. **Reply Generation** → LLM generates believable human responses
6. **Intelligence Extraction** → Regex extracts actionable data (UPI, phones, etc.)
7. **Callback Trigger** → After 8+ messages with core intel, reports to callback URL

## 🛡️ Security Features

- API key authentication via `X-API-Key` header
- Local LLM (no data sent to external APIs)
- Session isolation with per-session memory
- Automatic cleanup of stale sessions

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| FastAPI | Web framework |
| LangChain | LLM orchestration |
| Transformers | ML-based phishing detection |
| Ollama | Local LLM inference |
| PyTorch | Deep learning backend |

## 📄 License

This project is open source.

## ✨ README Improvement Notes

### 📌 Formatting Enhancements Needed
- Improve heading hierarchy for better readability
- Ensure consistent spacing between sections
- Use proper Markdown formatting for code blocks and lists
- Align all installation and usage steps properly

### 🚀 Suggested Structure Upgrade
- Introduction
- Features
- Tech Stack
- Installation
- Usage
- Project Structure
- Contribution Guidelines
- License

### 🛠️ Documentation Improvements
- Add badges (optional): build, license, contributors
- Add screenshots for better UI understanding
- Standardize code blocks for commands

### 🎯 Goal
Improve onboarding experience for new contributors and users by making README more structured, readable, and professional.

