# 🧠 Laya AI 决策系统 - 使用指南 v2.0

## 🎯 系统简介

本系统是一套基于 **Laya AI** 决策引擎的通用智能决策平台，支持多种决策场景：

- ✅ **智能分类**：文本/评论/内容自动分类
- ✅ **情感分析**：正面/负面/中性情感识别
- ✅ **意图识别**：用户意图自动识别
- ✅ **推荐决策**：个性化推荐与营销策略
- ✅ **风险评估**：业务/信贷/安全风险评估
- ✅ **批量处理**：高效批量决策分析

---

## 🆕 v2.0 更新

| 改进 | 说明 |
|------|------|
| HTTP 重试 | `requests` + `Retry` 自动重试 429/5xx，指数退避 |
| 异步客户端 | `httpx` 高并发批量处理 |
| 结构化日志 | `structlog` JSON 日志 + trace_id |
| 输入校验 | `pydantic` 提前拦截非法输入 |
| 环境变量配置 | `LAYA_BASE_URL`/`LAYA_TIMEOUT` 等覆盖 |
| 外部数据源 | `--data file.json/.csv/-` |
| 统一输出 | `{"metadata": {...}, "results": [...]}` |
| 进度条 | 实时进度反馈 |
| 插件化场景 | 自动注册，新场景无需改 main.py |
| 完整测试 | pytest 覆盖率覆盖 |

---

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install pydantic pydantic-settings structlog requests httpx
```

### 2. 启动 Laya AI 服务

```bash
cd /Users/hotker/Workspace/laya
./start-laya.sh

# 验证服务
curl http://localhost:8000/health
```

### 3. 运行系统

```bash
cd /Users/hotker/Workspace/laya_decision_system

# 交互式菜单
python src/main.py

# 直接模式
python src/main.py --classification   # 智能分类
python src/main.py --sentiment        # 情感分析
python src/main.py --intention        # 意图识别
python src/main.py --recommend        # 推荐决策
python src/main.py --risk             # 风险评估（新增）
python src/main.py --batch            # 批量处理
```

### 4. 使用外部数据

```bash
python src/main.py --classification --data reviews.json
python src/main.py --sentiment --data comments.csv
python src/main.py --sentiment --data -        # stdin
```

### 5. Docker 运行

```bash
docker build -t laya-decision:v2 .
docker run -it --rm -e LAYA_BASE_URL=http://laya-server:8000 laya-decision:v2 --classification
```

---

## 📊 功能模块详解

### 1. 智能分类

**场景**：客户评论、工单、邮件等自动分类

```bash
python src/main.py --classification
python src/main.py --classification --data reviews.json
```

**分类维度**：质量 | 价格 | 服务 | 功能 | 设计

**功能特性**：
- 外部数据源支持（JSON/CSV/stdin）
- 输入校验
- 进度条显示
- 分类统计 + 结果导出

### 2. 情感分析

**场景**：产品评价、舆情监控、用户反馈

```bash
python src/main.py --sentiment
python src/main.py --sentiment --data comments.csv
```

**情感维度**：非常正面 | 正面 | 中性 | 负面 | 非常负面

### 3. 意图识别

**场景**：客服咨询、搜索意图、营销意图

```bash
python src/main.py --intention
python src/main.py --intention --data messages.json
```

**意图维度**：咨询 | 投诉 | 购买 | 售后 | 好评

### 4. 推荐决策

**场景**：产品推荐、营销策略、个性化推送

```bash
python src/main.py --recommend
```

包含两个子场景：
- **产品推荐**：用户画像 → 推荐策略
- **营销策略**：营销场景 → 推荐策略

### 5. 风险评估（新增）

**场景**：信贷风险评估、安全预警、合规审核

```bash
python src/main.py --risk
```

**风险维度**：高风险 | 中风险 | 低风险 | 安全

### 6. 批量处理

**场景**：大量数据批量决策

```bash
python src/main.py --batch
python src/main.py --batch --data bulk.csv --format csv
```

**功能**：
- 自动分块处理
- 进度条显示
- 性能统计（耗时/条）
- JSON/CSV 输出

---

## 📝 CLI 参考

```
python src/main.py [选项]

场景选项（互斥，选一个）：
  --classification    智能分类
  --sentiment         情感分析
  --intention         意图识别
  --recommend         推荐决策
  --risk              风险评估
  --batch             批量处理

通用选项：
  --health            检查 Laya 服务状态
  --list              列出所有可用场景
  --data FILE         外部数据文件 (.json/.csv/-)
  --format FORMAT     输出格式 (json|csv, 默认 json)

交互式菜单（无参数）：
  1 智能分类    2 情感分析    3 意图识别
  4 推荐决策    5 风险评估    6 批量处理    7 数据管理    0 退出
```

---

## 📁 系统结构

```
laya_decision_system/
├── src/main.py                     # CLI 主程序
├── scenarios/                      # 决策场景（自动注册）
│   ├── __init__.py                 # 场景注册
│   ├── classification.py           # 智能分类
│   ├── sentiment.py                # 情感分析
│   ├── intention.py                # 意图识别
│   ├── recommendation.py           # 推荐决策
│   └── risk.py                     # 风险评估
├── config/config.py                # pydantic-settings 配置
├── utils/                          # 工具模块
│   ├── http_client.py              # 同步 HTTP（requests + 重试）
│   ├── async_http_client.py        # 异步 HTTP（httpx）
│   ├── validation.py               # 输入校验
│   ├── output.py                   # 输出管理
│   ├── data_source.py              # 数据源加载
│   ├── logging_utils.py            # 结构化日志
│   ├── plugin.py                   # 场景插件系统
│   └── progress.py                 # 进度条
├── tests/                          # 测试
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_http_client.py
│   ├── test_validation.py
│   ├── test_output.py
│   ├── test_data_source.py
│   └── test_plugin.py
├── output/                         # 决策输出
├── Dockerfile
├── .env.example
├── requirements.txt
└── run.sh
```

---

## 📈 使用示例

### 示例 1：智能分类

```python
from utils.http_client import make_predict_request
from utils.output import save_results

questions = {
    "category": {
        "type": "choice",
        "instructions": "判断评论类别",
        "criteria": {
            "quality": "质量、做工、耐用",
            "price": "价格、贵、便宜",
            "service": "客服、物流、安装"
        }
    }
}

result = make_predict_request("产品质量很好，做工精细", questions)
print(f"分类：{result['answers']['category']['choice']}")
```

### 示例 2：批量处理

```python
from utils.http_client import make_batch_request

states = [
    {"body": "产品质量很好"},
    {"body": "价格太贵了"},
    {"body": "客服态度差"}
]

questions = {
    "sentiment": {
        "type": "choice",
        "instructions": "情感分析",
        "criteria": {
            "positive": "好评、推荐、质量好",
            "negative": "差评、问题、不好",
        }
    }
}

result = make_batch_request(states, questions)
print(f"处理了 {len(result['results'])} 条")
```

### 示例 3：异步并发批量

```python
import asyncio
from utils.async_http_client import async_batch_concurrent

async def main():
    states = [{"body": "好"}, {"body": "坏"}, {"body": "一般"}]
    questions = {
        "sentiment": {"type": "choice", "instructions": "情感", "criteria": {"positive": "好"}}
    }
    result = await async_batch_concurrent(states, questions)
    print(f"成功: {result['progress']['succeeded']}/{result['progress']['total']}")

asyncio.run(main())
```

### 示例 4：外部数据源

```python
from utils.data_source import load_data

# JSON
data = load_data("reviews.json", text_column="body")
# CSV
data = load_data("reviews.csv", text_column="body")
# stdin
data = load_data("-", text_column="body")

for item in data:
    body = item["body"]
    # 处理...
```

---

## ⚙️ 配置

### 环境变量

通过 `LAYA_` 前缀环境变量覆盖：

| 变量 | 默认 | 说明 |
|------|------|------|
| `LAYA_BASE_URL` | `http://localhost:8000` | 服务地址 |
| `LAYA_TIMEOUT` | `30` | 超时（秒） |
| `LAYA_MODEL` | `multilingual` | 默认模型 |
| `LAYA_MAX_BATCH_SIZE` | `100` | 批量分块 |
| `LAYA_MAX_CONCURRENT_REQUESTS` | `5` | 并发数 |
| `LAYA_RETRY_TIMES` | `3` | 重试次数 |
| `LAYA_RETRY_DELAY` | `1.0` | 重试延迟（秒） |
| `LAYA_OUTPUT_DIR` | `./output` | 输出目录 |
| `LAYA_LOG_LEVEL` | `INFO` | 日志级别 |
| `LAYA_LOG_FORMAT` | `json` | 日志格式 |

### .env 文件

```bash
cp .env.example .env
# 编辑 .env
```

---

## 📊 决策输出

### 批量输出格式

```json
{
  "metadata": {
    "system": "Laya AI 决策系统",
    "version": "2.0.0",
    "timestamp": "2026-10-02T12:00:00.000000",
    "decision_type": "classification",
    "count": 5,
    "trace_id": "a1b2c3d4"
  },
  "results": [
    {
      "review": "产品质量很好，做工精细",
      "category": "quality"
    }
  ]
}
```

### CSV 输出

```bash
python src/main.py --batch --format csv
```

---

## 🧪 测试

```bash
# 全部测试
pytest tests/ -v

# 覆盖率
pytest tests/ -v --cov=. --cov-report=term-missing

# 单个
pytest tests/test_http_client.py -v
```

---

## 📝 新增场景（插件化）

新建场景只需 3 步：

**1. 创建 `scenarios/my_scene.py`**：
```python
from utils.http_client import make_predict_request
from utils.output import save_results
from utils.plugin import register

def run_my_scene(data_source=None):
    print("🧠 自定义场景")
    # ... 实现

register("my_scene", "自定义场景", "custom", run_my_scene)
```

**2. 在 `scenarios/__init__.py` 中导入并注册**：
```python
from scenarios.my_scene import run_my_scene  # noqa: F401
register("my_scene", "自定义场景", "custom", run_my_scene)
```

**3. 运行**：
```bash
python src/main.py --list
python src/main.py --my_scene
```

---

## 🔧 故障排除

### Laya 服务未启动
```bash
cd /Users/hotker/Workspace/laya && ./start-laya.sh
curl http://localhost:8000/health
```

### HTTP 连接失败
```bash
python src/main.py --health
# 增加重试
export LAYA_RETRY_TIMES=5
export LAYA_RETRY_DELAY=2.0
```

### 批量处理慢
```bash
export LAYA_MAX_CONCURRENT_REQUESTS=10
```

---

## 📞 信息

- **版本**：v2.0.0
- **文档更新**：2026-10-02
- **运行环境**：Python 3.10+
- **许可证**：仅供学习和研究使用