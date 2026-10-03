# 🧠 Laya AI Decision System v2.1

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
| **httpx** | Asynchronous HTTP with connection pooling + retry |
| **pydantic** | Data validation + environment variable configuration |
| **structlog** | Structured JSON logging |

---

## 🆕 v2.1 Updates

| # | Improvement | Description |
|---|------|------|
| 1 | **Plugin Auto-Discovery** | True automatic scenario registration via `scenarios/` directory scanning, no manual `main.py` mapping needed |
| 2 | **Async Connection Pooling** | Persistent `httpx.AsyncClient` with connection pooling (was creating/closing per request) |
| 3 | **Async Retry** | Exponential backoff retry for 429/5xx errors (was missing) |
| 4 | **Batch Iterative Chunking** | Replaced recursive batch splitting with safe iterative loop (no stack overflow risk) |
| 5 | **ProgressBar Fix** | Fixed infinite loop bug in terminal rendering |
| 6 | **Unified `--data` Support** | All scenarios (incl. risk) now support external data files |
| 7 | **Dynamic Batch Output** | Batch mode now displays all answer dimensions from response |
| 8 | **CSV Format Support** | `save_results(fmt="csv")` safely flattens nested structures |
| 9 | **Clean Config API** | Removed legacy dicts, unified access via `get_config()` |
| 10 | **Plugin Reset API** | `plugin.reset()` for clean test isolation |
| 11 | **Empty Results Safety** | All `_print_stats()` helpers guard against empty result lists |
| 12 | **Decoupled Validation** | `validate_state()` independent of `DecisionRequest` model |

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
docker build -t laya-decision:v2.1 .

# Run
docker run -it --rm \
  -e LAYA_BASE_URL=http://laya-server:8000 \
  laya-decision:v2.1 --classification
```

---

## 📁 Project Structure

```
laya_decision_system/
├── src/                          # Core entry
│   └── main.py                   # CLI main program (plugin-driven routing)
├── scenarios/                    # Decision scenarios (auto-registered)
│   ├── __init__.py               # Auto-discovery + CLI alias registration
│   ├── classification.py         # Intelligent classification
│   ├── sentiment.py              # Sentiment analysis
│   ├── intention.py              # Intent recognition
│   ├── recommendation.py         # Product recommendation + marketing strategy
│   └── risk.py                   # Risk assessment
├── config/                       # Configuration
│   └── config.py                 # pydantic-settings model (unified API)
├── utils/                        # Utility modules
│   ├── http_client.py            # Sync HTTP (requests + retry + session pool)
│   ├── async_http_client.py      # Async HTTP (httpx + pooling + retry)
│   ├── validation.py             # Input validation (independent state checks)
│   ├── output.py                 # Output management (JSON/CSV with safe flatten)
│   ├── data_source.py            # Data source loading (JSON/CSV/stdin)
│   ├── logging_utils.py          # Structured logging
│   ├── plugin.py                 # Plugin system (auto-discovery + reset API)
│   └── progress.py               # Progress bar (fixed rendering)
├── tests/                        # Tests (70+ cases, 85% coverage)
│   ├── test_plugin.py            # Plugin + auto-discovery tests
│   ├── test_http_client.py       # HTTP client tests
│   ├── test_data_source.py       # Data loading tests
│   └── test_output.py            # Output management tests
├── output/                       # Decision output
├── docs/                         # Documentation
├── .github/                      # GitHub Actions (CI + ruff lint)
├── Dockerfile                    # Docker
├── .env.example
├── pyproject.toml
└── run.sh
```

---

## 📊 Feature Modules

### 1. Intelligent Classification

**Scenario**: Customer reviews, work orders, emails auto-classification

```bash
python src/main.py --classification
python src/main.py --classification --data reviews.json
python src/main.py --classification --data reviews.csv
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

Runs both product recommendation AND marketing strategy decision sequentially.

**Recommendation Dimensions**: Premium Quality / Cost-effective / Trend / Personalized / Comprehensive

**Marketing Dimensions**: Discount / Content Marketing / Social / Loyalty / Personalized

### 5. Risk Assessment

**Scenario**: Credit, security, compliance risk

```bash
python src/main.py --risk
python src/main.py --risk --data risk_cases.json
```

**Risk Dimensions**: High Risk / Medium Risk / Low Risk / Safe

### 6. Batch Processing

**Scenario**: Rapid analysis of large volumes of data

```bash
python src/main.py --batch
python src/main.py --batch --data bulk.csv --format csv
```

- Auto-chunks large batches (no recursion, safe for any size)
- Real-time progress bar with ETA
- Supports JSON and CSV output

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

**Stdin**:
```bash
cat data.json | python src/main.py --batch --data -
```

---

## ⚙️ Configuration

### Environment Variables

All variables use `LAYA_` prefix. Supports `.env` files via `pydantic-settings`.

| Variable | Default | Description |
|----------|--------|------|
| `LAYA_BASE_URL` | `http://localhost:8000` | Laya service address |
| `LAYA_TIMEOUT` | `30` | Request timeout (seconds) |
| `LAYA_MODEL` | `multilingual` | Default model |
| `LAYA_MAX_BATCH_SIZE` | `100` | Max batch chunk size |
| `LAYA_MAX_CONCURRENT_REQUESTS` | `5` | Async concurrency |
| `LAYA_RETRY_TIMES` | `3` | Retry times (sync + async) |
| `LAYA_RETRY_DELAY` | `1.0` | Initial retry delay (seconds) |
| `LAYA_OUTPUT_DIR` | `./output` | Output directory |
| `LAYA_LOG_LEVEL` | `INFO` | Log level |
| `LAYA_LOG_FORMAT` | `json` | Log format (`json`/`text`) |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage (fails under 80%)
pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=80
```

### CI

GitHub Actions runs tests on Python 3.10–3.12 and ruff lint checks on every push/PR.

---

## 🔧 Architecture Highlights

### Plugin Auto-Discovery

Add a new scenario by creating a module in `scenarios/` with a `run_*` function. The system auto-discovers and registers it — no manual mapping in `main.py` needed.

```python
# scenarios/anomaly_detection.py
def run_anomaly_detection(data_source=None):
    # Your logic here
    pass
```

### Plugin Reset (Testing)

```python
from utils.plugin import reset
reset()  # Clear all registered scenarios for clean test isolation
```

### Async Client (Connection Pooling + Retry)

```python
from utils.async_http_client import async_make_predict_request, async_close_client

result = await async_make_predict_request(
    "text input",
    {"sentiment": {...}},
    max_retries=3  # Override default retry count
)
await async_close_client()  # Cleanup on shutdown
```

---

## 📄 License

This project is for learning and research purposes only.