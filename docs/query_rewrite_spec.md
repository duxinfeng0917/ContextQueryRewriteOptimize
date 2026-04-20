# 上下文查询改写规范文档

> 适用场景：马来西亚新车汽车销售多轮对话系统的用户 query 改写模块

---

## 1. 任务定义

**目标**：结合多轮对话历史，将用户当前 query 中的**指代不明信息**补全，并将**常见缩写**还原为完整写法，输出一条"更完整、更清晰"的 query。

**不是翻译、不是改写语种、不是润色**。

### 输入
| 字段 | 说明 |
|------|------|
| `original_query` | 用户当前消息 |
| `history` | 对话历史（User/Agent 轮次） |
| `car_series` | 补充知识：本对话可能涉及的车系 |

### 输出
- 一条改写后的 query（单行纯文本）
- 若无需改写，**原样输出**

---

## 2. 改写类型

### 2.1 指代消解（Coreference Resolution）

将指代词替换为历史中对应的**明确对象**（车型/版本/价格类型等）。

| 语言 | 指代词示例 | 改写前 | 改写后 |
|------|-----------|--------|--------|
| 中文 | 那款、那辆、后者、前者、这辆车 | 那款多少钱？ | Honda City 多少钱？ |
| 英文 | the one, that car, it | What about the one? | What about the Seal Performance? |
| 马来语 | yang ni, kereta tu, yang ... tu | Yang ni berapa? | Honda City ni berapa? |
| 混合语 | yg ... tu, yang Performance tu | Klu yg Performance tu plak? | Klu yg Seal Performance tu plak? |

**规则**：
- 只用历史中**明确出现过**的原始写法（大小写/别名/符号保持一致）
- 若历史中无法确定指代对象 → **原样输出，不猜测**
- 若当前句中已包含车型名 → 无需补全，原样输出

### 2.2 缩写展开（Abbreviation Expansion）

将已知缩写还原为完整写法，保持与原句相同语种。

**分级机制**：
1. **词表优先**：查阅附录缩写词表，命中则直接替换
2. **语言兜底**：词表未覆盖时，仅在含义唯一、无歧义、展开后语种不变的条件下展开

---

## 3. 核心禁止规则

### 3.1 禁止语种切换（最高优先级）

- **中文 query** 中禁止注入英文业务词汇（如 Monthly Payment、Down Payment、Ringgit Malaysia）
- **英/马来语 query** 中禁止注入中文
- **混合语 query** 只能在原有语种范围内活动，不得新增书写系统
- 缩写展开必须保持原句语种：英文缩写 → 英文完整写法，马来语缩写 → 马来语完整写法

**典型错误示例**（来自数据集）：

| 原句（中文）| 错误改写 | 正确改写 |
|------------|---------|---------|
| 都要放 10% 的定金吗？ | 都要放 10% 的 **Down Payment** 吗？ | 都要放 10% 的定金吗？（原样） |
| 那个 BYD 的月供是多少？ | 那个 BYD Atto 3 的 **Monthly** 是多少？ | 那个 BYD Atto 3 的月供是多少？ |
| 欠银行大概 2万。 | 欠银行贷款大约 20,000 **Ringgit Malaysia**。 | 欠银行大概 2万。（原样） |
| Civic RS 月供多少？ | Civic RS **Monthly Payment (mthly) how much?** | Civic RS 月供多少？（原样） |

### 3.2 禁止过度改写（Hallucination）

- 禁止添加对话历史中**未明确出现**的信息（车型年份、颜色、地点、配置级别等）
- 禁止用模糊描述填充（如"for the car models available"、"dengan spesifikasi penuh"）

**典型错误示例**：

| 原句 | 错误改写 | 正确改写 |
|------|---------|---------|
| Nak book test drive Atto 3. | Nak book test drive Atto 3 untuk model tahun **2024** yang berada di lokasi **Kuala Lumpur**, dengan pilihan warna **hitam** dan kelengkapan **full spec**. | Nak book test drive Atto 3.（原样） |
| Berapa harga Mazda CX-30? | Berapa harga Mazda CX-30 untuk model terkini dengan **spesifikasi penuh dan penawaran yang tersedia**? | Berapa harga Mazda CX-30?（原样） |
| Any promotion this month? | Any promotion this month **for the car models available**? | Any promotion this month?（原样） |

### 3.3 禁止语义改变

- 车型专有名称（如 X50、Atto 3、OMODA E5）中的字母不是缩写，**禁止展开**
- 首付（Down Payment）≠ 月供（Monthly Installment），禁止混用
- 不得对原句做润色、改写句式或纠正语法

---

## 4. 错误分类体系

用于评测集标注，共 5 类：

| 标签 | 定义 | 严重度 |
|------|------|-------|
| `CORRECT` | 改写正确：正确补全指代/展开缩写，未过度改写 | — |
| `NO_CHANGE` | 无需改写：原句独立完整，原样输出 ✓ | — |
| `LANG_ERROR` | 语种错误：改写引入了与原句语种不一致的词汇 | 严重 |
| `MEANING_CHANGE` | 语义错误：改写改变了原句的语义意图（如月供↔首付混淆） | 严重 |
| `OVER_REWRITE` | 过度改写：添加了对话历史中不存在的细节（幻觉） | 中 |
| `UNDER_REWRITE` | 漏改写：含明确指代词但未消解，历史中有可推断的对象 | 中 |
| `STYLE_REWRITE` | 样式改写：仅措辞润色，未增加实质信息（可接受） | 轻微 |

---

## 5. 评测数据集统计（2026-04-17，n=854）

| 标签 | 数量 | 占比 |
|------|------|------|
| CORRECT | 447 | 52.3% |
| NO_CHANGE | 357 | 41.8% |
| OVER_REWRITE | 28 | 3.3% |
| LANG_ERROR | 11 | 1.3% |
| UNDER_REWRITE | 11 | 1.3% |
| **错误合计** | **50** | **5.9%** |

### 主要问题分析

**OVER_REWRITE（28例，占错误的56%）**  
模型在历史中无对应信息时仍添加了具体配置（年份、颜色、地点、完整规格）。集中出现于首轮问答（无历史背景）和开放性问题（如"有促销吗"）。

**LANG_ERROR（11例）**  
全部为中文 query 中注入英文业务词汇（Monthly、Down Payment、Ringgit Malaysia 等）。根因：prompt 的缩写词表包含这些英文词，模型在改写中文 query 时也触发了展开规则。

**UNDER_REWRITE（11例）**  
全部为中文强指代词（后者、前者、那辆、那款）在多车型对比场景中未做消解。这类场景的历史通常包含两个候选车型，需要模型从上下文语义判断指代对象。

---

## 6. Prompt 优化建议

基于错误分析，针对当前改写 prompt 的改进方向：

### 6.1 强化语种保护规则

在"核心硬性规则"中补充明确示例：

```
禁止示例（中文query禁止注入英文业务词汇）：
- 错误：都要放 10% 的 Down Payment 吗？→ 正确：都要放 10% 的定金吗？
- 错误：月供改写为 Monthly → 正确：保持"月供"
- 错误：2万改写为 20,000 Ringgit Malaysia → 正确：保持"2万"
```

### 6.2 明确区分首付与月供

在缩写词表说明中加注：

```
⚠️ 注意：dp → Down Payment（首付/定金），不同于月供（Monthly Installment）
  - 首付：购车时一次性支付的款项
  - 月供：贷款后每月还款金额
  禁止互相替换。
```

### 6.3 限制 OVER_REWRITE

在"只做补全与缩写展开"规则中加强约束：

```
禁止添加的信息类型（即使合理推断也不允许）：
- 车型年份（如 2024款）
- 颜色（如黑色、白色）
- 具体地点（如 Kuala Lumpur）
- 配置描述（如 full spec、spesifikasi penuh）
- 模糊的范围词（如"for the car models available"）
```

### 6.4 明确无对象时的处理

在"信息来源约束"规则中补充：

```
若当前 query 本身已包含完整主体（如已提到具体车型名），
则无需从历史中补全任何信息，直接原样输出。
```

---

## 7. 语种判断规则

| 语种标签 | 判断标准 | 改写语种 |
|---------|---------|---------|
| `Zh` | 主要由中文字符组成，可混入少量英文专有名词 | 中文，英文专有名词保留 |
| `En` | 主要由英文组成 | 英文 |
| `My` | 主要为标准马来语 | 马来语 |
| `Mix` | 英马混合（Manglish）或含中文混合 | 在原有语种范围内 |

---

## 8. 缩写词表（完整版）

### 英文/汽车业务词汇
| 缩写 | 完整写法 | 备注 |
|------|----------|------|
| mthly | Monthly | 月付的 |
| dp | Down Payment | 首付 |
| fl | Full Loan | 全额贷款 |
| rm | Ringgit Malaysia | 马来西亚令吉 |
| k | Thousand | 如 50k = 50,000 |
| nego | Negotiable | 可议价 |
| cond | Condition | 车况 |
| yr | Year | 年 |
| mil | Mileage | 里程 |
| acc free | Accident Free | 无事故 |
| ori | Original | 原装 |
| mod | Modified | 改装 |
| fs | Full Spec | 全配 |
| ss | Standard Spec | 标配 |
| recon | Reconditioned | 二手翻新 |
| mfg | Manufacturing Year | 出厂年份 |
| reg | Registered Year | 注册年份 |
| SA | Sales Advisor | 销售顾问 |
| doc | Document | 文件 |
| ic | Identity Card | 身份证 |
| lesen | Lesen Memandu | 驾照 |
| stmt | Bank Statement | 银行流水 |
| epf | Employees Provident Fund | 公积金 |
| bl | Blacklist | 黑名单 |
| guar | Guarantor | 担保人 |
| int | Interest Rate | 利率 |
| HP | Hire Purchase | 分期购买 |
| depo | Deposit | 押金 |
| bal | Balance | 余额 |
| ins | Insurance | 保险 |
| jpj | Jabatan Pengangkutan Jalan | 道路交通局 |
| loc | Location | 地点 |
| tq | Thank You | 谢谢 |
| ws / wasap | WhatsApp | WhatsApp |

### 马来语口语缩写
| 缩写 | 完整写法 |
|------|----------|
| brp | berapa |
| hrga | harga |
| kete | kereta |
| thn | tahun |
| bln | bulan |
| sy | saya |
| nk | nak |
| x | tak |
| bleh | boleh |
| skrg | sekarang |
| dh / dah | sudah |
| blm | belum |
| utk | untuk |
| jg | juga |
| tu | itu |
| ni | ini |
| kt | dekat |
| tau | tahu |
| cntk | cantik |
| msh | masih |
| tgu | tunggu |
| pki | pakai |
| kwsp | Kumpulan Wang Simpanan Pekerja |

---

## 附录：评测集文件说明

`dataset/groundtruth_eval.xlsx` 包含三个 sheet：

| Sheet | 内容 |
|-------|------|
| 改写质量评测 | 全量854条，含自动标注标签、错误说明、建议GT，供人工二次审核 |
| 统计总览 | 各标签数量和占比 |
| 错误案例 | 仅含错误案例（50条），适合优先人工修正 |

**人工审核流程**：
1. 打开"错误案例" sheet，重点审核 `LANG_ERROR` 和 `OVER_REWRITE` 类
2. 在"人工审核结论"列填写：`确认` / `误报` / `调整`
3. 若建议GT有误，在"人工修正groundtruth"列填写正确版本
4. 完成后将"人工修正groundtruth"作为最终 groundtruth 用于模型评测
