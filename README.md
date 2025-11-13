# Zé Continha

Zé Continha is a proof-of-concept project for **PairTrading (Long & Short)** based on **Cointegration**.

⚠️ **Disclaimer**:  
* No buy/sell recommendations are given.  
* Data accuracy is **not guaranteed**.  
* Use the information at your own risk.  

[http://zecontinha.com.br/b3/pairs_ranking](http://zecontinha.com.br/b3/pairs_ranking)

---

## ✅ Quick Start

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd zecontinha
```

### 2. Set up environment variables
Copy the examples and edit credentials:
```bash
cp postgres.env.example postgres.env
cp zecontinha.env.example zecontinha.env
```

**Edit the files** to match your database, API keys, and Telegram credentials.

- `postgres.env`: Postgres database settings  
- `zecontinha.env`: Django SECRET_KEY, Binance API keys, Telegram API key  

---

### 3. Run the project with Docker 🐋 (recommended)
Bring up all services (images will be built automatically if needed, and migrations will run):
```bash
docker compose up --build -d
```

The Django project and all services will start automatically.

---

### 4. Running the cron task
Open a shell in the app container:
```bash
docker compose run --rm app bash
```

Run the cron calculation script:
```bash
python cron_calc.py
```

---

### 5. Run the project normally (without Docker)
If you want to run the Django project directly on your machine (requires **Python 3.9+**):
1. Create a virtual environment:
```bash
python3.9 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
2. Install dependencies with Poetry:
```bash
poetry install
```
3. Apply migrations:
```bash
python manage.py migrate
```
4. Run the development server:
```bash
python manage.py runserver 0.0.0.0:8000
```
Visit: [http://localhost:8000](http://localhost:8000)

