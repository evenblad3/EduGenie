# EduGenie

**EduGenie: AI-Powered Learning Workspace**

Driven by Google Gemini, EduGenie helps students, self-learners, and educators master complex concepts, evaluate knowledge, and build structured learning paths.

## Features

-   **Ask (Q&A)** — Clear, accurate answers to complex educational questions.
-   **Explain** — Simple, structured breakdowns of difficult concepts.
-   **Quiz** — Dynamic, topic-specific multiple-choice assessments.
-   **Summarize** — Concise overviews and key takeaways from long passages.
-   **Learning Path** — Step-by-step roadmaps to master any subject.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic
- **AI:** Google Gemini 3.8 Flash via `google-generativeai`
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Server:** Gunicorn + Uvicorn Workers

## Prerequisites

- Python 3.11 or higher
- A Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

## Installation

1. **Clone the repo:**
   ```bash
   git clone https://github.com/sathya723/EduGenie
   cd EduGenie
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv 
   .\venv\Scripts\activate # windows
   # or
   source venv/bin/activate # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

## Local Development

```bash
uvicorn main:app --reload --port 8000
```

And then visit [http://localhost:8000](http://localhost:8000)

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home |
| `GET` | `/health` | Health check |
| `POST` | `/qa` | Answer an educational question |
| `POST` | `/explain` | Explain a concept |
| `POST` | `/quiz` | Generate a quiz |
| `POST` | `/summarize` | Summarize text |
| `POST` | `/learn/recommendations` | Create a learning path |

### Request/Response Examples

#### Q&A
```json
// POST /qa
{ "question": "What is the purpose of virtual environments in Python?" }
// Response
{ "answer": "Virtual environments create isolated directory trees..." }
```

#### Quiz
```json
// POST /quiz
{ "topic": "Python Programming" }
// Response
{
  "questions": [
    {
      "question": "Which built-in function returns the length of an object in Python?",
      "options": ["count()", "len()", "size()", "length()"],
      "correct_answer": "len()"
    }
  ]
}
```
