# 🧠 Laya AI 决策系统 v2.0

> 基于 Laya AI 决策引擎的通用智能决策平台

## 📋 系统概述

本系统是一套基于 **Laya AI** 决策引擎的通用智能决策平台，支持多种决策场景：

- ✅ **智能分类**：文本/评论/内容自动分类
- ✅ **情感分析**：正面/负面/中性情感识别
- ✅ **意图识别**：用户意图自动识别
- ✅ **风险评估**：风险等级自动评分
- ✅ **推荐决策**：个性化推荐与策略制定
- ✅ **批量处理**：高效批量决策分析

### 技术栈

| 组件 | 说明 |
|------|------|
| **Python 3.10+** | 使用现代类型注解 |
| **Laya AI** | 智能决策引擎（多语言支持） |
| **requests** | 同步 HTTP，自动重试 + 指数退避 |
| **httpx** | 异步 HTTP，高并发批量处理（可选） |
| **pydantic** | 数据校验 + 环境变量配置 |
| **structlog** | 结构化 JSON 日志 |

---

## 🆕 v2.0 更新

| # | 改进 | 说明 |
|---|------|------|
| 1 | HTTP 重试 | `requests` + `Retry` 自动重试 429/5xx |
| 2 | 异步客户端 | `httpx` 高并发 `async_batch_concurrent()` |
| 3 | 结构化日志 | `structlog` JSON 输出 + trace_id |
| 4 | 输入校验 | `pydantic` 校验请求参数 |
| 5 | 环境变量配置 | `LAYA_BASE_URL` 等覆盖，`.env` 支持 |
| 6 | 外部数据源 | `--data file.json/.csv/-` |
| 7 | 统一输出 | `{"metadata": {...}, "results": [...]}` |
| 8 | 进度条 | 实时 `分类 |████| 30% 1.2/s ETA 5.0s` |
| 9 | 风险评估 | 新增场景 |
| 10 | 插件化 | 场景自动注册，新场景无需改 main.py |
| 11 | CSV 输出 | `--format csv` |
| 12 | 完整测试 | pytest + 覆盖率 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pydantic pydantic-settings structlog requests httpx
```

### 2. 环境配置

```bash
cp .env.example .env
```

```bash
export LAYA_BASE_URL=http://localhost:8000
export LAYA_MODEL=multilingual
export LAYA_TIMEOUT=30
export LAYA_RETRY_TIMES=3
```

### 3. 启动 Laya 服务

```bash
# 启动 Laya AI 服务
cd /Users/hotker/Workspace/laya
./start-laya.sh

# 验证服务
curl http://localhost:8000/health
```

### 4. 运行系统

```bash
# 交互式菜单
python src/main.py

# 直接模式
python src/main.py --classification   # 智能分类
python src/main.py --sentiment        # 情感分析
python src/main.py --intention        # 意图识别
python src/main.py --recommend        # 推荐决策
python src/main.py --risk             # 风险评估
python src/main.py --batch            # 批量处理
```

### 5. Docker 运行

```bash
# 构建
docker build -t laya-decision:v2 .

# 运行
docker run -it --rm \
  -e LAYA_BASE_URL=http://laya-server:8000 \
  laya-decision:v2 --classification
```

---

## 📁 系统结构

```
laya_decision_system/
├── src/                          # 核心入口
│   └── main.py                   # CLI 主程序
├── scenarios/                    # 决策场景（自动注册）
│   ├── __init__.py
│   ├── classification.py         # 智能分类
│   ├── sentiment.py              # 情感分析
│   ├── intention.py              # 意图识别
│   ├── recommendation.py         # 推荐决策
│   └── risk.py                   # 风险评估
├── config/                       # 配置
│   └── config.py                 # pydantic-settings 模型
├── utils/                        # 工具模块
│   ├── http_client.py            # 同步 HTTP（requests + 重试）
│   ├── async_http_client.py      # 异步 HTTP（httpx）
│   ├── validation.py             # 输入校验
│   ├── output.py                 # 输出管理
│   ├── data_source.py            # 数据源加载
│   ├── logging_utils.py          # 结构化日志
│   ├── plugin.py                 # 场景插件系统
│   └── progress.py               # 进度条
├── tests/                        # 测试
├── output/                       # 决策输出
├── docs/                         # 文档
├── .github/                      # GitHub 自动化
├── Dockerfile                    # Docker
├── .dockerignore
├── .env.example
├── requirements.txt
└── run.sh
```

---

## 📊 功能模块

### 1. 智能分类

**场景**：客户评论、工单、邮件等自动分类

```bash
python src/main.py --classification
python src/main.py --classification --data reviews.json
```

**分类维度**：质量、价格、服务、功能、设计

### 2. 情感分析

**场景**：产品评价、舆情监控、用户反馈

```bash
python src/main.py --sentiment
python src/main.py --sentiment --data comments.csv
```

**情感维度**：非常正面 / 正面 / 中性 / 负面 / 非常负面

### 3. 意图识别

**场景**：客服咨询、搜索意图、营销意图

```bash
python src/main.py --intention
python src/main.py --intention --data messages.json
```

**意图维度**：咨询 / 投诉 / 购买 / 售后 / 好评

### 4. 推荐决策

**场景**：产品推荐、营销策略

```bash
python src/main.py --recommend
```

**推荐维度**：高端品质 / 性价比 / 流行趋势 / 个性化 / 综合

**营销维度**：折扣 / 内容营销 / 社交裂变 / 会员 / 精准推送

### 5. 风险评估（新增）

**场景**：信贷、安全、合规风险

```bash
python src/main.py --risk
```

**风险维度**：高风险 / 中风险 / 低风险 / 安全

### 6. 批量处理

**场景**：大量数据快速分析

```bash
python src/main.py --batch
python src/main.py --batch --data bulk.csv --format csv
```

---

## 📝 使用方式

### CLI 选项

```
python src/main.py [选项]

通用选项：
  --classification    智能分类
  --sentiment         情感分析
  --intention         意图识别
  --recommend         推荐决策
  --risk              风险评估
  --batch             批量处理
  --health            检查服务状态
  --list              列出所有可用场景
  --data FILE         外部数据文件 (.json/.csv/-)
  --format FORMAT     输出格式 (json|csv, 默认 json)
```

### 数据源格式

**JSON 数组**：
```json
[{"body": "评论 1"}, {"body": "评论 2"}]
```

**CSV**：
```csv
body
评论 1
评论 2
评论 3
```

---

## ⚙️ 配置

### 环境变量

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `LAYA_BASE_URL` | `http://localhost:8000` | Laya 服务地址 |
| `LAYA_TIMEOUT` | `30` | 请求超时（秒） |
| `LAYA_MODEL` | `multilingual` | 默认模型 |
| `LAYA_MAX_BATCH_SIZE` | `100` | 批量最大分块 |
| `LAYA_MAX_CONCURRENT_REQUESTS` | `5` | 异步并发数 |
| `LAYA_RETRY_TIMES` | `3` | 重试次数 |
| `LAYA_RETRY_DELAY` | `1.0` | 重试初始延迟（秒） |
| `LAYA_OUTPUT_DIR` | `./output` | 输出目录 |
| `LAYA_LOG_LEVEL` | `INFO` | 日志级别 |
| `LAYA_LOG_FORMAT` | `json` | 日志格式 (`json`/`text`) |

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 带覆盖率
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 📄 许可证

本项目仅供学习和研究使用。
