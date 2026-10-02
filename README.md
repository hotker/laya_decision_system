# 🧠 Laya AI Decision System v2.0

> A Universal Intelligent Decision Platform Based on Laya AI Decision Engine

## 📋 Overview

This system is a universal intelligent decision platform based on the **Laya AI** decision engine, supporting multiple decision scenarios:

- ✅ **Intelligent Classification**: Automatic classification of text/comments/content
- ✅ **Sentiment Analysis**: Positive/negative/neutral sentiment recognition
- ✅ **Intent Recognition**: Automatic user intent identification
- ✅ **Risk Assessment**: Automatic risk level scoring
- ✅ **Recommendation Decision**: Personalized recommendations and strategy formulation
- ✅ **Batch Processing**: Efficient batch decision analysis

### Tech Stack

| Component | Description |
|------|------|
| **Python 3.10+** | Modern type annotations |
| **Laya AI** | AI decision engine (multi-language support) |
| **requests** | Synchronous HTTP with auto-retry + exponential backoff |
| **httpx** | Asynchronous HTTP for high-concurrency batch processing (optional) |
| **pydantic** | Data validation + environment variable configuration |
| **structlog** | Structured JSON logging |

---

## 🆕 v2.0 Updates

| # | Improvement | Description |
|---|------|------|
| 1 | HTTP Retry | `requests` + `Retry` auto-retry for 429/5xx |
| 2 | Async Client | `httpx` high-concurrency `async_batch_concurrent()` |
| 3 | Structured Logging | `structlog` JSON output + trace_id |
| 4 | Input Validation | `pydantic` request parameter validation |
| 5 | Environment Config | `LAYA_BASE_URL` overrides, `.env` support |
| 6 | External Data Source | `--data file.json/.csv/-` |
| 7 | Unified Output | `{"metadata": {...}, "results": [...]}` |
| 8 | Progress Bar | Real-time `Classification |████| 30% 1.2/s ETA 5.0s` |
| 9 | Risk Assessment | New scenario added |
| 10 | Plugin Architecture | Automatic scene registration, no need to modify main.py |
| 11 | CSV Output | `--format csv` |
| 12 | Complete Testing | pytest + coverage |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pydantic pydantic-settings structlog requests httpx
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

```bash
export LAYA_BASE_URL=http://localhost:8000
export LAYA_MODEL=multilingual
export LAYA_TIMEOUT=30
export LAYA_RETRY_TIMES=3
```

### 3. Start Laya Service

```bash
# Start Laya AI service
cd /Users/hotker/Workspace/laya
./start-laya.sh

# Verify service
curl http://localhost:8000/health
```

### 4. Run System

```bash
# Interactive menu
python src/main.py

# Direct mode
python src/main.py --classification   # Intelligent classification
python src/main.py --sentiment        # Sentiment analysis
python src/main.py --intention        # Intent recognition
python src/main.py --recommend        # Recommendation decision
python src/main.py --risk             # Risk assessment
python src/main.py --batch            # Batch processing
```

### 5. Docker

```bash
# Build
docker build -t laya-decision:v2 .

# Run
docker run -it --rm \
  -e LAYA_BASE_URL=http://laya-server:8000 \
  laya-decision:v2 --classification
```

---

## 📁 Project Structure

```
laya_decision_system/
├── src/                          # Core entry
│   └── main.py                   # CLI main program
├── scenarios/                    # Decision scenarios (auto-registration)
│   ├── __init__.py
│   ├── classification.py         # Intelligent classification
│   ├── sentiment.py              # Sentiment analysis
│   ├── intention.py              # Intent recognition
│   ├── recommendation.py         # Recommendation decision
│   └── risk.py                   # Risk assessment
├── config/                       # Configuration
│   └── config.py                 # pydantic-settings model
├── utils/                        # Utility modules
│   ├── http_client.py            # Sync HTTP (requests + retry)
│   ├── async_http_client.py      # Async HTTP (httpx)
│   ├── validation.py             # Input validation
│   ├── output.py                 # Output management
│   ├── data_source.py            # Data source loading
│   ├── logging_utils.py          # Structured logging
│   ├── plugin.py                 # Scene plugin system
│   └── progress.py               # Progress bar
├── tests/                        # Tests
├── output/                       # Decision output
├── docs/                         # Documentation
├── .github/                      # GitHub automation
├── Dockerfile                    # Docker
├── .dockerignore
├── .env.example
├── requirements.txt
└── run.sh
```

---

## 📊 Feature Modules

### 1. Intelligent Classification

**Scenario**: Customer reviews, work orders, emails auto-classification

```bash
python src/main.py --classification
python src/main.py --classification --data reviews.json
```

**Classification Dimensions**: Quality, Price, Service, Feature, Design

### 2. Sentiment Analysis

**Scenario**: Product reviews, public opinion monitoring, user feedback

```bash
python src/main.py --sentiment
python src/main.py --sentiment --data comments.csv
```

**Sentiment Dimensions**: Very Positive / Positive / Neutral / Negative / Very Negative

### 3. Intent Recognition

**Scenario**: Customer service inquiries, search intent, marketing intent

```bash
python src/main.py --intention
python src/main.py --intention --data messages.json
```

**Intent Dimensions**: Inquiry / Complaint / Purchase / After-sales / Positive Review

### 4. Recommendation Decision

**Scenario**: Product recommendations, marketing strategies

```bash
python src/main.py --recommend
```

**Recommendation Dimensions**: Premium Quality / Cost-effective / Trend / Personalized / Comprehensive

**Marketing Dimensions**: Discount / Content Marketing / Social裂变 / Membership / Precision Push

### 5. Risk Assessment (New)

**Scenario**: Credit, security, compliance risk

```bash
python src/main.py --risk
```

**Risk Dimensions**: High Risk / Medium Risk / Low Risk / Safe

### 6. Batch Processing

**Scenario**: Rapid analysis of large volumes of data

```bash
python src/main.py --batch
python src/main.py --batch --data bulk.csv --format csv
```

---

## 📝 Usage

### CLI Options

```
python src/main.py [options]

General Options:
  --classification    Intelligent classification
  --sentiment         Sentiment analysis
  --intention         Intent recognition
  --recommend         Recommendation decision
  --risk              Risk assessment
  --batch             Batch processing
  --health            Check service status
  --list              List all available scenarios
  --data FILE         External data file (.json/.csv/-)
  --format FORMAT     Output format (json|csv, default json)
```

### Data Source Format

**JSON Array**:
```json
[{"body": "Review 1"}, {"body": "Review 2"}]
```

**CSV**:
```csv
body
Review 1
Review 2
Review 3
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|--------|------|
| `LAYA_BASE_URL` | `http://localhost:8000` | Laya service address |
| `LAYA_TIMEOUT` | `30` | Request timeout (seconds) |
| `LAYA_MODEL` | `multilingual` | Default model |
| `LAYA_MAX_BATCH_SIZE` | `100` | Max batch chunk size |
| `LAYA_MAX_CONCURRENT_REQUESTS` | `5` | Async concurrency |
| `LAYA_RETRY_TIMES` | `3` | Retry times |
| `LAYA_RETRY_DELAY` | `1.0` | Initial retry delay (seconds) |
| `LAYA_OUTPUT_DIR` | `./output` | Output directory |
| `LAYA_LOG_LEVEL` | `INFO` | Log level |
| `LAYA_LOG_FORMAT` | `json` | Log format (`json`/`text`) |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 📄 License

This project is for learning and research purposes only.