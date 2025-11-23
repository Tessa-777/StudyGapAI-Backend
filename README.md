# 🧠 StudyGapAI - Backend API

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img alt="Flask" src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img alt="Supabase" src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white"/>
  <img alt="Google Gemini" src="https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
</p>

This is the official backend for **StudyGapAI**, an AI-powered learning diagnostics platform. It combines **Flask**, **Supabase**, and the **Google Gemini API** to provide personalized analysis and study plans for Nigerian students. This service is deployed on **Railway**.

**➡️ Frontend Repository:** [https://github.com/Tessa-777/Royal-Light-StudyGapAI](https://github.com/Tessa-777/Royal-Light-StudyGapAI)

---

## Development & Authorship

StudyGapAI was developed entirely by Theresia Saumu as the sole developer for the WUD AI Hackathon 2025 (1st Place Winner).

**Technical Development:** 100% developed by Theresia Saumu
- Full-stack architecture and implementation
- All backend code (Python Flask)
- All frontend code
- Database design and implementation
- AI integration and prompt engineering
- Deployment and DevOps

**Hackathon Collaboration:** During the 1 week hackathon sprint, team members contributed to ideation and strategic direction. All code and technical implementation was authored solely by Theresia Saumu.

**Current Status:** StudyGapAI is now being developed independently by Theresia Saumu.

## ✨ Core Features

- **AI-Powered Diagnostic Engine:** The core of the API. Analyzes quiz results and student explanations to identify root cause knowledge gaps.
- **Personalized Study Plan Generation:** Creates tailored 6-week study roadmaps based on diagnostic data.
- **Secure Authentication:** Manages user registration, login, and profiles using Supabase Auth.
- **Comprehensive Progress Tracking:** Endpoints to store and retrieve quiz history, performance metrics, and study plan progress.
- **RESTful API Design:** Clean, well-structured endpoints for seamless integration with any frontend client.

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | Flask (Python) | Core API & Business Logic |
| **Database** | Supabase (PostgreSQL) | Data Storage, Auth & Row-Level Security |
| **AI Engine** | Google Gemini 2.0 Flash | Diagnostic Analysis & Plan Generation |
| **Hosting** | Railway | Deployment |

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ and `pip`
- A Supabase project
- A Google AI API Key

### 2. Installation & Setup

1.  **Clone the `main` branch:**
    ```bash
    git clone --branch main https://github.com/Tessa-777/Royal-Light-StudyGapAI-Backend.git
    cd Royal-Light-StudyGapAI-Backend
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root and add your credentials:
    ```env
    SUPABASE_URL=your_supabase_url
    SUPABASE_ANON_KEY=your_supabase_anon_key
    SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
    GOOGLE_API_KEY=your_gemini_api_key
    ```

4.  **Run database migrations:**
    Apply the SQL migrations located in the `/supabase/migrations` directory to your Supabase project via the SQL Editor. This sets up the required tables and Row-Level Security policies.

5.  **Run the development server:**
    ```bash
    flask run
    ```
    The API will be available at `http://127.0.0.1:5000`.

## 🤖 The AI Engine (Google Gemini)

Our API's core intelligence comes from **Google Gemini 2.0 Flash**.

- **Why Gemini?** It offers the perfect balance of fast response times (3-5 seconds per analysis), low cost, and strong reasoning capabilities for the Nigerian educational context.
- **How it Works:** We use a carefully engineered 287-line system prompt that instructs the model to perform a deep analysis and return a validated, structured JSON response. This ensures reliability and consistency for the frontend.

## 🔑 API Endpoints

### Authentication
- `POST /api/users/register`: Register a new user.
- `POST /api/users/login`: Authenticate a user and receive a JWT.
- `GET /api/users/me`: Get the current authenticated user's profile.

### AI Diagnostics & Study Plans
- `POST /api/ai/analyze-diagnostic`: **(Core Endpoint)** Submits quiz data and student explanations. Returns a comprehensive AI-generated diagnostic report, including root cause analysis, a projected score, and a full 6-week study plan.
- `POST /api/ai/save-diagnostic`: Saves a guest user's diagnostic results to their account after they register.
- `POST /api/ai/explain-answer`: Get a detailed, AI-generated explanation for a specific quiz question.

### Quizzes & Progress
- `GET /api/quiz/questions`: Retrieve the list of diagnostic quiz questions.
- `GET /api/progress/progress`: Get a user's historical performance data.

## 📄 AI Acceleration Report

This project was built in a hackathon timeframe using extensive AI assistance. For a complete breakdown, see our **[AI Acceleration Report](AI_ACCELERATION_REPORT.md)**.
