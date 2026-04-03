# air-quality-health-predictor
Air Quality Health Predictor

A full-stack application that predicts health risks based on air quality data using machine learning and real-time analytics.

🚀 Features
🌫️ Air Quality Index (AQI) prediction
🧠 Machine Learning-based health risk analysis
📊 Interactive dashboard (React)
🔌 REST API integration (FastAPI)
📈 Data visualization for pollution trends
🛠️ Tech Stack
Backend
Python
FastAPI
Scikit-learn
Pandas, NumPy
Frontend
React (Vite)
Axios
Chart libraries
Database
SQLite / PostgreSQL
⚙️ Installation Guide
1️⃣ Clone Repository
git clone https://github.com/MAHANTESHSKANDE/air-quality-health-predictor.git
cd air-quality-health-predictor
2️⃣ Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate   # Windows

pip install fastapi uvicorn pandas numpy scikit-learn sqlalchemy
3️⃣ Run Backend Server
uvicorn main:app --reload

👉 Runs at: http://127.0.0.1:8000

4️⃣ Frontend Setup
cd ../frontend
npm install
5️⃣ Run Frontend
npm run dev

👉 Runs at: http://localhost:5173

🧠 Machine Learning
Data preprocessing using Pandas
Model training using Scikit-learn
Predicts health impact based on AQI levels
