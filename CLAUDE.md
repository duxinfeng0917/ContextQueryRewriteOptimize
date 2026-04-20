# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ContextQueryRewriteOptimize**（上下文改写优化）— 马来西亚新车汽车销售多轮对话系统的用户 query 改写质量分析与评测工具。

核心任务：评估 LLM 对多语言（中文/英文/马来语/混合语）用户 query 的改写质量，生成标准 groundtruth 评测集，并识别改写错误。

## Commands

```bash
# 分析数据集、生成评测集
python3 analyze_rewrites.py
# 输出：dataset/groundtruth_eval.xlsx

# 依赖安装
pip install openpyxl
```

## Architecture

### Key Files

| 文件 | 作用 |
|------|------|
| `analyze_rewrites.py` | 主分析脚本：读取数据集 → 错误检测 → 分类 → 生成评测 Excel |
| `dataset/马来西亚新车数据集.xlsx` | 原始数据，854条，15列 |
| `dataset/groundtruth_eval.xlsx` | 生成的评测集（运行脚本后产生） |
| `docs/query_rewrite_spec.md` | 改写规范文档，含错误分类体系、prompt 优化建议、缩写词表 |

### Dataset Columns

原始数据集的关键列：
- `original_query`（col 10）：用户原始 query
- `rewrite_res`（col 14）：LLM 改写结果
- `rewrite_prompt`（col 13）：完整 prompt（含对话历史、缩写词表、补充知识）
- `Language Type`（col 6）：`Zh` / `En` / `My` / `Mix`

### Error Detection Logic（`analyze_rewrites.py`）

五类错误的检测逻辑：
- **LANG_ERROR**：检测中文 query 中是否注入了英文业务词汇（Monthly、Down Payment 等）
- **OVER_REWRITE**：检测改写是否包含 hallucination 模式（年份/颜色/地点/配置等未出现在历史中的细节）
- **UNDER_REWRITE**：检测含强指代词（那辆、后者、前者、kereta ni 等）但未消解的案例
- **MEANING_CHANGE**：检测语义错误（如月供↔首付混用）
- **NO_CHANGE / CORRECT**：改写前后相同 / 改写正确

### Quality Results（2026-04-17 基准）

| 标签 | 数量 | 占比 |
|------|------|------|
| CORRECT | 447 | 52.3% |
| NO_CHANGE | 357 | 41.8% |
| OVER_REWRITE | 28 | 3.3% |
| LANG_ERROR | 11 | 1.3% |
| UNDER_REWRITE | 11 | 1.3% |
| 错误合计 | 50 | 5.9% |
