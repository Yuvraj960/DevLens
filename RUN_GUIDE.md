# 🚀 DevLens Local Execution & Inspection Guide

This guide provides step-by-step instructions for running, testing, and inspecting **DevLens** locally on Windows / Linux / macOS.

> 💡 **For a complete guide detailing all environment variables, API key sources (OpenAI, Anthropic, Ollama), and troubleshooting, see [EXECUTION_AND_SETUP_GUIDE.md](EXECUTION_AND_SETUP_GUIDE.md).**

---

## 📋 Prerequisites & Services

Ensure you have the following installed on your machine:
- **Docker Desktop** (with Docker Compose v2+)
- **Node.js** 18+ and `npm`
- **Python** 3.11+ (if running backend directly outside Docker)

---

## 🛠️ Step-by-Step Instructions to Run DevLens

### Option A: Running Local Hybrid Server (Recommended for Inspection)

1. **Environment Configuration**:
   - Create `.env` in the root directory (`c:\Users\lenovo\Desktop\DevLens\.env`):
     ```env
     POSTGRES_USER=devlens
     POSTGRES_PASSWORD=devlens_pass
     POSTGRES_DB=devlens_db
     DATABASE_URL=postgresql+asyncpg://devlens:devlens_pass@localhost:5432/devlens_db
     REDIS_URL=redis://localhost:6379/0
     QDRANT_URL=http://localhost:6333
     QDRANT_COLLECTION=devlens_code_chunks
     NEXT_PUBLIC_API_URL=http://localhost:8000
     ```

2. **Start Infrastructure Containers**:
   Run the following command in terminal:
   ```bash
   docker compose up -d postgres redis qdrant
   ```

3. **Run Backend Service (FastAPI)**:
   In a separate terminal window:
   ```bash
   cd backend
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # Linux/macOS: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Run Frontend Application (Next.js 14)**:
   In a separate terminal window:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access Application Dashboards**:
   - **Frontend UI**: Open [http://localhost:3000](http://localhost:3000)
   - **FastAPI OpenAPI Interactive Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Qdrant Vector Dashboard**: Open [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

### Option B: Running Full Production Stack in Docker

```bash
docker compose -f docker-compose.prod.yml up -d --build
```
Access at [http://localhost](http://localhost).

---

## 🧪 Running Automated Test Suites

To verify everything is functioning correctly behind the scenes:

```bash
cd backend
pytest -v
```
