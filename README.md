# ContextQueryRewriteOptimize

**上下文改写优化** —— 马来西亚新车汽车销售多轮对话系统的用户 Query 改写质量分析与自动优化工具。

---

## 项目简介

本项目面向马来西亚新车直播/在线销售场景，对 LLM 在多轮对话中执行的用户 Query 改写任务进行**质量评测**和**自动 Prompt 优化**。

支持语言：中文（Zh）/ 英文（En）/ 马来语（My）/ 混合语（Mix）

核心工作流：

```
原始对话数据集 → 错误自动检测 → 生成 groundtruth 评测集 → DSPy 自动优化 Prompt → 线上推理改写
```

---

## 项目结构

```
.
├── analyze_rewrites.py      # 主分析脚本：错误检测 + 生成评测 Excel
├── dspy_optimizer.py        # DSPy MIPROv2 自动 Prompt 优化
├── run_inference.py         # 加载优化程序，执行单条/批量改写推理
├── optimized_rewriter.json  # 已优化的 DSPy 程序（可直接加载）
├── dataset/
│   ├── 马来西亚新车数据集.xlsx   # 原始数据（854 条，15 列）
│   ├── groundtruth_eval.xlsx    # 生成的评测集（运行 analyze_rewrites.py 后产生）
│   └── 重写规范记录.md           # Live QA 重写评估规范
├── docs/
│   └── query_rewrite_spec.md    # 改写规范文档（错误分类、Prompt 优化建议、缩写词表）
└── llm_infer/
    ├── model_config.py          # Azure 模型端点与 API Key 配置
    ├── litellm_client.py        # LiteLLM 统一模型客户端
    └── model.py                 # 模型调用封装
```

---

## 数据集说明

原始数据集（`dataset/马来西亚新车数据集.xlsx`）共 854 条，关键列：

| 列名 | 列号 | 说明 |
|------|------|------|
| `Language Type` | col 6 | 语言类型：`Zh` / `En` / `My` / `Mix` |
| `original_query` | col 10 | 用户原始 query |
| `rewrite_prompt` | col 13 | 完整 prompt（含对话历史、缩写词表、补充知识）|
| `rewrite_res` | col 14 | LLM 改写结果 |

---

## 改写规则概览

| 规则 | 说明 |
|------|------|
| 指代消解 | 将"那辆"/"the one"/"yang ni"等代词替换为历史中明确出现的车型名 |
| 缩写展开 | 按缩写词表还原（`dp` → `Down Payment`，`mthly` → `Monthly`，`rm` → `Ringgit Malaysia`）|
| 语种保持 | 中文 query 中**禁止**注入英文业务词；英/马来语 query 中**禁止**注入中文 |
| 禁止过度改写 | 禁止添加历史中未明确出现的信息（车型年份、颜色、配置等）|
| 无需改写时原样输出 | 若当前 query 已完整或无历史可参考，输出原文 |

详见 [docs/query_rewrite_spec.md](docs/query_rewrite_spec.md)。

---

## 错误分类体系

| 错误码 | 说明 | 典型示例 |
|--------|------|---------|
| `LANG_ERROR` | 中文 query 中注入了英文业务词汇 | "放 10% 的 Down Payment" |
| `OVER_REWRITE` | 改写包含对话历史中未出现的细节（幻觉）| 凭空添加年份、颜色、地点 |
| `UNDER_REWRITE` | 含强指代词但未消解（上下文可获取时）| "那辆车多少钱？"未替换车型名 |
| `MEANING_CHANGE` | 改写改变了原始语义 | 月供↔首付、询问↔陈述 混用 |
| `NO_CHANGE` | 改写前后完全相同（无实质动作）| — |
| `CORRECT` | 改写正确 | — |

---

## 质量基准（2026-04-17）

| 标签 | 数量 | 占比 |
|------|------|------|
| CORRECT | 447 | 52.3% |
| NO_CHANGE | 357 | 41.8% |
| OVER_REWRITE | 28 | 3.3% |
| LANG_ERROR | 11 | 1.3% |
| UNDER_REWRITE | 11 | 1.3% |
| **错误合计** | **50** | **5.9%** |

---

## 快速开始

### 1. 安装依赖

```bash
pip install openpyxl dspy-ai litellm openai
```

### 2. 配置模型

编辑 `llm_infer/model_config.py`，填写 Azure OpenAI 端点与 API Key：

```python
azure_model_config = {
    "gpt-5.4-nano": {
        "base_url": "https://<your-resource>.cognitiveservices.azure.com/openai/v1/",
        "api_key": "<your-api-key>",
    },
    # 支持：DeepSeek-R1-0528 / DeepSeek-V3-0324 / gpt-4.1 / gpt-4o / o3 等
}
```

### 3. 分析数据集，生成评测集

```bash
python3 analyze_rewrites.py
# 输出：dataset/groundtruth_eval.xlsx
```

### 4. DSPy 自动 Prompt 优化

```bash
# 完整 MIPROv2 优化（推荐）
python3 dspy_optimizer.py

# 快速模式（BootstrapFewShot，速度快但效果略低）
python3 dspy_optimizer.py --quick

# 仅评估，不优化
python3 dspy_optimizer.py --eval

# 加载已有程序并评估
python3 dspy_optimizer.py --load optimized_rewriter.json --eval
# 优化结果保存为 optimized_rewriter.json
```

### 5. 线上推理改写

```bash
# 单条改写
python3 run_inference.py \
    --query "那辆车月供多少？" \
    --history "User: Seal 落地价多少？\nAgent: 大约 12 万。" \
    --car-series "Seal" \
    --lang Zh

# 批量推理（输入为 JSON 文件）
python3 run_inference.py --batch input.json --output output.json
```

批量输入格式（`input.json`）：

```json
[
  {
    "query": "那辆车月供多少？",
    "history": "User: Seal 落地价多少？\nAgent: 大约 12 万。",
    "car_series": "Seal",
    "lang": "Zh"
  }
]
```

---

## 支持的模型

通过 `llm_infer/litellm_client.py` 统一管理，当前支持的 Azure 部署模型：

| 模型名 | 类型 |
|--------|------|
| `gpt-5.4-nano` | Azure OpenAI（默认推理模型）|
| `gpt-4.1` / `gpt-4.1-mini` | Azure OpenAI |
| `gpt-4o` / `gpt-4o-mini` | Azure OpenAI |
| `o3` | Azure OpenAI |
| `DeepSeek-R1-0528` | Azure AI Foundry |
| `DeepSeek-V3-0324` / `DeepSeek-V3.2` | Azure AI Foundry |
