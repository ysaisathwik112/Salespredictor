# 🎯 SalesCast AI — Intelligent Sales Prediction System

<div align="center">

**Enterprise-grade, full-stack ML-powered sales prediction platform**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## 📋 Overview

SalesCast AI is a **production-ready** sales prediction system that serves machine learning predictions via a Flask REST API with an enterprise-grade frontend dashboard. Built with clean architecture, modular design, and industry best practices.

### Key Features

- 🧠 **GradientBoosting ML Model** — Trained on retail sales data with 95%+ R² accuracy
- 🔌 **REST API** — Flask-based API with Swagger docs, validation, and structured responses
- 🎨 **Premium UI** — Glassmorphism design, video background, Chart.js analytics, responsive
- 📊 **Real-time Dashboard** — Prediction history, analytics, and trend charts
- 🐳 **Docker Ready** — One-command deployment with Docker Compose
- 🔒 **Security** — Input validation, CORS, rate limiting, secure headers
- 📝 **Full Logging** — Rotating file logs for app, errors, and predictions
- 🧪 **Tested** — Comprehensive unit tests with pytest
- 🔄 **CI/CD** — GitHub Actions pipeline for test, build, and deploy

---

## 🏗️ Architecture

```
ml-sales-prediction-system/
│
├── app/                        # Flask Application
│   ├── __init__.py             # App factory
│   ├── routes/
│   │   └── api.py              # REST API endpoints
│   ├── services/
│   │   ├── prediction_service.py  # ML prediction logic
│   │   └── training_service.py    # Model retraining
│   ├── models/
│   │   ├── __init__.py         # SQLAlchemy models
│   │   └── schemas.py          # Marshmallow validation
│   └── utils/
│       ├── logger.py           # Logging configuration
│       └── error_handlers.py   # Global error handlers
│
├── ml/                         # Machine Learning
│   ├── training/
│   │   └── train.py            # Training pipeline
│   ├── preprocessing/
│   │   └── preprocessor.py     # Data preprocessing
│   └── artifacts/              # Model artifacts (generated)
│       ├── model.pkl
│       ├── scaler.pkl
│       └── encoder.pkl
│
├── frontend/                   # Frontend UI
│   ├── index.html              # Main HTML
│   ├── css/style.css           # Design system
│   └── js/app.js               # Frontend logic
│
├── tests/                      # Test suite
│   ├── test_api.py             # API tests
│   └── test_model.py           # ML tests
│
├── nginx/                      # Nginx config
│   └── nginx.conf
│
├── logs/                       # Application logs
├── .github/workflows/          # CI/CD pipeline
├── Dockerfile                  # Container build
├── docker-compose.yml          # Multi-service orchestration
├── requirements.txt            # Python dependencies
├── config.py                   # Environment configuration
├── run.py                      # Application entry point
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### 1. Clone & Setup

```bash
cd ml-sales-prediction-system

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Train the Model

```bash
python ml/training/train.py
```

This generates model artifacts (`model.pkl`, `scaler.pkl`, `encoder.pkl`) in `ml/artifacts/`.

### 3. Run the Application

```bash
python run.py
```

Open **http://localhost:5000** in your browser.

### 4. Run Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment

### Single Container

```bash
docker build -t salescast-ai .
docker run -p 5000:5000 salescast-ai
```

### Full Stack (API + Redis + Nginx)

```bash
docker-compose up -d
```

Access at **http://localhost** (port 80 via Nginx).

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve frontend UI |
| `GET` | `/health` | API health check |
| `POST` | `/predict` | Sales prediction |
| `POST` | `/api/predict/batch` | Batch predictions |
| `POST` | `/train` | Retrain model |
| `GET` | `/api/predictions/history` | Prediction history |
| `GET` | `/api/analytics/summary` | Analytics summary |
| `GET` | `/docs` | Swagger API documentation |

### Example Prediction Request

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "item_weight": 12.5,
    "item_visibility": 0.05,
    "item_mrp": 150.00,
    "item_type": "Dairy",
    "outlet_size": "Medium",
    "outlet_location_type": "Tier 1",
    "outlet_type": "Supermarket Type1",
    "outlet_establishment_year": 2005
  }'
```

### Example Response

```json
{
  "success": true,
  "request_id": "a3f2b1c4d5e6",
  "data": {
    "predicted_sales": 2547.83,
    "confidence_score": 0.9312,
    "prediction_time_ms": 12.45,
    "model_version": "1.0.0",
    "currency": "USD"
  }
}
```

---

## 🧠 Machine Learning

### Model Details

| Property | Value |
|----------|-------|
| Algorithm | GradientBoostingRegressor |
| Features | 8 input → 30+ encoded |
| Training Data | 5,000 synthetic samples |
| Cross-validation | 5-fold |
| Preprocessing | StandardScaler + OneHotEncoder |

### Input Features

| Feature | Type | Range |
|---------|------|-------|
| Item Weight | Float | 0.1 – 50.0 |
| Item Visibility | Float | 0.0 – 0.35 |
| Item MRP | Float | 10 – 300 |
| Item Type | Categorical | 16 categories |
| Outlet Size | Categorical | Small/Medium/High |
| Outlet Location | Categorical | Tier 1/2/3 |
| Outlet Type | Categorical | 4 types |
| Establishment Year | Integer | 1980 – 2025 |

---

## 🔒 Security Features

- **Input Validation** — Marshmallow schemas with strict type/range validation
- **CORS** — Configurable cross-origin resource sharing
- **Rate Limiting** — Flask-Limiter with configurable thresholds
- **Secure Headers** — X-Frame-Options, X-Content-Type-Options, XSS protection (via Nginx)
- **Error Handling** — Global error handlers with no stack trace leakage

---

## 📊 Monitoring

- **Application Logs** → `logs/app.log` (10MB rotating, 5 backups)
- **Error Logs** → `logs/error.log`
- **Prediction Logs** → `logs/predictions.log`
- **Swagger Docs** → `http://localhost:5000/docs`

---

## 🛠️ Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `development` | Environment (dev/prod) |
| `SECRET_KEY` | auto-generated | Flask secret key |
| `DATABASE_URL` | SQLite | Database connection |
| `REDIS_URL` | `redis://localhost:6379` | Redis URL |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PORT` | `5000` | Server port |

---

## 📄 License

This project is for educational and demonstration purposes.

---

<div align="center">
<strong>Built with ❤️ for enterprise ML applications</strong>
</div>
