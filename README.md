<div align="center">

# Deadline / 截止日 🕒  

</div>

> **Automatically track things you said you would do, but never did.**  
> 自动捕捉你在聊天 / 邮件 / 评论里“说过要做、后来忘掉了”的承诺，生成一份可追责的 **Promise Backlog（承诺清单）**。

---

### 🌟 项目简介 / Project Overview

- **产品定位**：  
  - 不是待办清单工具  
  - 不是日程提醒工具  
  - 而是一个 **“承诺检测 + 责任追踪” 系统**  
- **核心哲学**：
  - ❌ 不帮你“生成任务”
  - ✅ 只从你已经说过的话里，挖出那些有 **“我会 / 我们会 / 之后搞定 / TODO / later / follow up”** 的句子
  - 然后把它们结构化成：
    - **谁** 在 **什么时候** 承诺了 **要做什么**
    - 是否有 **明确或模糊的 deadline**
    - 当前状态是 **pending / overdue / unclear**

你可以把 **Deadline** 想象成：  
> 一双在你聊天记录 / issue 评论 / 邮件线程里到处“抓你现行”的监控眼睛 👀  
> 帮你把“嘴上说过”的事情，变成“承诺资产”。

---

### ✅ 核心特性 / Key Features

- **跨场景文本输入**：
  - 💬 IM 聊天记录（Slack / Discord / 微信 / 飞书 等）
  - 🐙 GitHub / GitLab / Jira issue & PR 评论
  - 📧 邮件正文（转发、导出、聚合文本）
  - 🧾 任意时间顺序的纯文本日志

- **严格的“非幻觉”承诺检测**：
  - 先用轻量 **关键词预筛**（`I'll`, `TODO`, `later`, `follow up` 等）
  - 通过 LLM **句子级** 判断：  
    > “这一句是不是一个承诺 / 义务 / 要做的事情？”
  - 只接受 **YES / NO**，拒绝模糊回答，尽量避免幻觉

- **多维度承诺分类**：
  - `personal_promise`：个人承诺（“我会修”、“I'll fix it”）
  - `team_promise`：团队/组织承诺（“我们会处理”、“We’ll take care of it”）
  - `soft_intention`：软意向（“我们应该……”、“We should maybe…”）
  - `hard_commitment`：硬承诺（“周五前我一定搞定”、“I will do X by Friday”）

- **责任人 & 截止时间抽取（不瞎编）**：
  - `who`：
    - 句子主体是 “I” → 直接记录 `"I"`
    - 句子主体是 “we” → 记录 `"we"`
    - 不清楚是谁 → `"Unassigned"`
  - `deadline_text`：
    - 只记录 **原始表达**：`"next week"`, `"by Friday"`, `"before launch"`
    - ❌ 不推断具体日期（2026-02-10 这种不会凭空生成）

- **结构化 Promise Backlog 输出**：
  - 📄 Markdown 列表（适合贴在 GitHub / Notion / Slack）
  - 🧾 JSON（适合落库 / API / 分析）
  - 🧮 文本表格（适合 CLI 浏览）

---

### 🧠 产品设计原则 / Design Principles

- **不生成任务，只发现承诺**：
  - 不帮你“规划今天做什么”
  - 专注回答：“你之前答应过别人 / 团队什么？”

- **拒绝幻觉 / No Hallucinations**：
  - 不凭空创造人物、日期、任务
  - 没有明确责任人 → 统一标记为 **`Unassigned`**
  - 没有明确截止时间 → 统一标记为 **`No explicit deadline`**

- **句子级（sentence-level）推理**：
  - 所有 LLM 调用都在 **“单句” 粒度**完成
  - 不让模型“看整段然后总结”
  - 流程是：
    1. 这是一条承诺吗？（Yes / No）
    2. 如果是，属于哪种类型？
    3. 能抽取出谁负责 & 有无 deadline 表达吗？

- **分类优先（Classification-first）而非总结**：
  - 所有 Prompt 都是 **分类 / 抽取** 指令
  - 明确禁止使用“summarize”这类请求

---

### 🗂 项目结构 / Project Structure

```text
deadline/
  core/
    ingest.py          # 统一规范化聊天 / 邮件 / issue 文本
    detector.py        # 承诺句子检测（关键词 + LLM YES/NO）
    classifier.py      # 承诺类型分类 + 置信度
    resolver.py        # 责任人 & 截止时间解析 + 状态计算
  llm/
    client.py          # LLM HTTP 通用客户端（OpenAI 兼容）
    prompts.py         # Prompt 模板（句子级、带约束）
  schemas/
    commitment.py      # 数据模型 & 枚举定义
  outputs/
    formatter.py       # Markdown / JSON / 表格输出
  main.py              # CLI 入口（可作为未来插件 / Agent 的主线调用）
  README.md
requirements.txt
```

---

### 🧱 模块详解 / Module Deep Dive

#### 1. 数据模型层 `schemas/commitment.py` 🧬

- **核心枚举**：
  - `CommitmentKind`：承诺类型
  - `CommitmentStatus`：状态（`pending` / `overdue` / `unclear`）
- **核心实体**：
  - `SourceMessage`：一条原始消息（聊天 / 邮件 / 评论）
  - `SentenceSpan`：从消息里切分出的某一句
  - `Commitment`：最终结构化的“承诺”记录

示例（简化版）：

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class CommitmentKind(str, Enum):
    PERSONAL_PROMISE = "personal_promise"
    TEAM_PROMISE = "team_promise"
    SOFT_INTENTION = "soft_intention"
    HARD_COMMITMENT = "hard_commitment"


class CommitmentStatus(str, Enum):
    PENDING = "pending"
    OVERDUE = "overdue"
    UNCLEAR = "unclear"


@dataclass
class SourceMessage:
    text: str
    sender: Optional[str] = None
    timestamp: Optional[datetime] = None
    channel: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Commitment:
    id: str
    sentence: str
    full_message: str
    who: Optional[str]
    kind: Optional[CommitmentKind]
    kind_confidence: float
    created_at: datetime
    explicit_deadline_text: Optional[str]
    explicit_deadline_date: Optional[datetime]
    status: CommitmentStatus
    source: SourceMessage
```

> ✅ 模型特点：  
> - 所有可推断字段都保持“可空”（避免乱填）  
> - 日期统一使用 `datetime`，输出前再转成 ISO 字符串  

---

#### 2. 文本归一化 `core/ingest.py` 🧹

**目标**：把“混乱的原始内容”变成“可被模型消费的标准对话结构”。

- 输入可以是：
  - 一段长文本（例如导出的邮件线程）
  - 一组有 time / sender 的消息数组
- 输出是：
  - `NormalizedConversation`：
    - `messages: List[SourceMessage]`
    - `sentences: List[SentenceSpan]`

核心逻辑（简化）：

```python
def _split_into_sentences(text: str) -> List[str]:
    import re
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def normalize_from_text(text: str, *, sender=None, timestamp=None, channel=None):
    item = {
        "text": text,
        "sender": sender,
        "timestamp": timestamp,
        "channel": channel,
    }
    return normalize_from_messages([item], channel=channel)
```

> 💡 这里的句子切分用的是简单正则，方便后续替换成 spaCy、Stanza 等更强的 NLP 工具。

---

#### 3. 承诺句子检测 `core/detector.py` 🔍

**两级过滤**：

1. **关键词预筛**（本地规则，零成本）  
   如果一句话里完全没有类似：
   - `"I'll"`, `"I will"`, `"TODO"`, `"later"`, `"follow up"`, `"we should"`  
   → 直接跳过，不浪费 LLM 调用

2. **LLM 严格 YES/NO 判断**  
   - Prompt 明确约束：只回答 `YES` 或 `NO`
   - 严格限制模型的“话痨”与幻想空间

伪代码：

```python
def detect_commitment_sentences(llm: LLMClient, sentences: List[SentenceSpan]) -> List[SentenceSpan]:
    results = []
    for span in sentences:
        if not _keyword_prefilter(span.text):
            continue

        user_prompt = COMMITMENT_DETECTION_USER_TEMPLATE.format(sentence=span.text)
        answer = llm.chat(
            system_prompt=COMMITMENT_DETECTION_SYSTEM,
            user_prompt=user_prompt,
        ).strip().upper()

        if answer == "YES":
            results.append(span)
    return results
```

> 🎯 设计意图：  
> - 关键词减少调用次数  
> - 句子级 YES/NO 决策保证“只抓真正的承诺句”，不把“我觉得/我想/这个功能不错”误判为承诺。

---

#### 4. 承诺类型与置信度 `core/classifier.py` 🧪

当一句话已经被判定为 **承诺** 后，再进行更细粒度的分类：

- 输出：
  - `kind`: `personal_promise | team_promise | soft_intention | hard_commitment`
  - `confidence`: `0 ~ 1` 浮点数
  - `raw_label_dict`: 原始 JSON 输出，方便调试和后处理

代码片段：

```python
def classify_commitments(llm: LLMClient, spans: List[SentenceSpan]):
    results = []
    for span in spans:
        user_prompt = COMMITMENT_CLASSIFICATION_USER_TEMPLATE.format(sentence=span.text)
        raw = llm.chat(
            system_prompt=COMMITMENT_CLASSIFICATION_SYSTEM,
            user_prompt=user_prompt,
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"kind": "soft_intention", "confidence": 0.3}

        kind_str = str(data.get("kind", "soft_intention"))
        kind = CommitmentKind(kind_str) if kind_str in CommitmentKind._value2member_map_ else CommitmentKind.SOFT_INTENTION

        confidence = float(data.get("confidence", 0.5)) if isinstance(data.get("confidence"), (int, float, str)) else 0.5

        results.append((span, kind, confidence, data))
    return results
```

> 💡 这样一来，你可以在 UI 里用不同颜色区分“软意向”和“硬承诺”，也可以按置信度过滤掉模型不太确定的结果。

---

#### 5. 责任与 Deadline 解析 `core/resolver.py` 🧩

目标：在 **不瞎编** 的前提下，从承诺句子中挖出：

- `who`: 责任人（可以是 `"I"`, `"we"`, 也可以是 `"Unassigned"`）
- `deadline_text`: 原始 deadline 表达（可能为空）
- `status`: `pending / overdue / unclear`

这里有一个重要约束：

- **不在 LLM 里做日期推断**
- `explicit_deadline_date` 暂时保持 `None`
- 未来可以挂接一个 **确定性的日期解析器**（如只解析明确格式：`2026-02-10`，而不是 `"next week"`）

简化逻辑：

```python
def _extract_attributes(llm: LLMClient, sentence: str) -> dict:
    user_prompt = ATTRIBUTE_EXTRACTION_USER_TEMPLATE.format(sentence=sentence)
    raw = llm.chat(
        system_prompt=ATTRIBUTE_EXTRACTION_SYSTEM,
        user_prompt=user_prompt,
    )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"who": "Unassigned", "deadline_text": None}
    return {
        "who": data.get("who") or "Unassigned",
        "deadline_text": data.get("deadline_text"),
    }
```

> 🔒 这层是“安全闸门”：即使 LLM 出现格式问题，也会退回到安全默认值，避免产出垃圾数据。

---

#### 6. 输出格式 `outputs/formatter.py` 🖨

支持三种 Promise Backlog 视图：

- **Markdown**（适合贴在 GitHub issue / PR / 文档里）

```python
def to_markdown(commitments):
    lines = []
    for c in commitments:
        who = c.who or "Unassigned"
        deadline = c.explicit_deadline_text or "No explicit deadline"
        lines.append(f"- **Promise**: {c.sentence}")
        lines.append(f"  - **Who**: {who}")
        lines.append(f"  - **When**: {c.created_at.isoformat()}")
        lines.append(f"  - **Deadline**: {deadline}")
        lines.append(f"  - **Status**: {c.status.value}")
        lines.append("")
    return "\n".join(lines).strip()
```

- **JSON**（方便落库 / 给前端 / 统计分析）
- **文本表格**（在 CLI 中一眼看清谁欠了什么）

---

### 🚀 端到端使用方式 / End-to-End Usage

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置 LLM 环境变量（以 OpenAI 兼容接口为例）

Windows PowerShell 示例：

```bash
set DEADLINE_LLM_BASE_URL=https://api.openai.com/v1
set DEADLINE_LLM_API_KEY=sk-xxxx
set DEADLINE_LLM_MODEL=gpt-4.1-mini
```

#### 3. 从文件运行

```bash
python -m deadline.main --input sample.txt --format markdown
```

#### 4. 从 stdin 运行（管道）

```bash
type sample.txt | python -m deadline.main --format table
```

示例输入（`sample.txt`）：

```text
I'll fix this bug next week.
We should revisit the onboarding flow later.
I'll get back to you on this.
This looks good to me.
TODO: handle edge cases in the billing logic in the next release.
```

示例输出（Markdown）：

```markdown
- **Promise**: I'll fix this bug next week.
  - **Who**: I
  - **When**: 2026-02-02T10:00:00
  - **Deadline**: next week
  - **Status**: unclear

- **Promise**: TODO: handle edge cases in the billing logic in the next release.
  - **Who**: Unassigned
  - **When**: 2026-02-02T10:00:00
  - **Deadline**: in the next release
  - **Status**: unclear
```

> ✅ 可以很方便地复制这段 Markdown，粘贴到 GitHub issue / 飞书 / Notion 作为“承诺索引”。

---

### 🧩 可扩展性设计 / Extension & Integration

- **VS Code / Cursor 插件**：
  - 使用现有 `core.*` 和 `outputs.*` 模块
  - 在编辑器侧获取当前文件 / 选中文本 → 调用 `normalize_from_text` → 整个 pipeline → 在侧边栏渲染 Promise Backlog

- **CI / GitHub Bot 集成**：
  - 针对 PR 描述和评论跑一遍 Deadline
  - 给出一个“本 PR 的承诺清单”，方便 Reviewer 和 Owner 对齐

- **后台 Agent / 定时任务**：
  - 订阅 Slack / Teams / 邮件 Webhook
  - 周期性抓取最新对话、跑一遍 pipeline
  - 把所有承诺写入一个统一的“承诺数据库”，再由别的系统去做提醒 / 分析

---

### 🧭 Roadmap Ideas（未来可以考虑的方向）

- ⏱ 更智能的 deadline 解析（在“绝对不瞎编”的前提下，只匹配明确日期格式）
- 🧑‍⚖️ 承诺完成状态对接（手动勾选 / GitHub issue 关联 / 任务系统联动）
- 📊 承诺指标仪表盘（按人 / 团队 / 项目分析“承诺兑现率”）
- 🔄 多语言支持（目前 Prompt 设计已适合中英混合场景）

---

### 🙌 总结

**Deadline / 截止日** 把“你说过的话”变成“可审计的承诺资产”：  

- 不打扰你的工作流  
- 不要求你刻意记录待办  
- 只是在你已经写下的文字里，悄悄帮你记住那些 **“我会做的事”**。  

欢迎你继续在这个基础上扩展 UI、插件、Agent 或团队内部版本，如果你有具体产品方向（B 端 / 个人效率 / 团队透明度），我也可以帮你一起设计更细的交互与功能。 🎯  

---

## 👤 作者 (Author)

**Haoze Zheng**

*   🎓 **School**: Xinjiang University (XJU)
*   📧 **Email**: zhenghaoze@stu.xju.edu.cn
*   🐱 **GitHub**: [mire403](https://github.com/mire403)

---

<div align="center">




<sub>Made by Haoze Zheng. 2026 Deadline.</sub>

</div>





