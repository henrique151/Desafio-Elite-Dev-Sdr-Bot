set -e

# ================= FRONTEND (Next.js) =================
echo "Starting frontend..."
cd frontend
npm install
npm run build
npm run start -p $PORT &  # Porta do Railway
FRONTEND_PID=$!

# ================= BACKEND (FastAPI) =================
echo "Starting backend..."
cd ../backend
pip install --upgrade pip
pip install -r requirements.txt

# Rode FastAPI usando Uvicorn na porta fixa 8000
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# ================= AGUARDAR AMBOS PROCESSOS =================
wait $FRONTEND_PID $BACKEND_PID
