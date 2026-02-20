# 评分系统设计

## 评分架构

```
单轮对话结束
    │
    ├──→ [内容评分] Gemini Structured Output → 各维度分数
    │
    ├──→ [表达评分] 语音特征分析(语速/停顿/填充词)
    │
    └──→ [非语言评分] 微表情+目光数据(前端采集)
            │
            ▼
      加权汇总 → 单轮得分 → 累计 → 面试总报告
```

## 1. 内容评分（AI打分）

使用 Gemini 的 Structured Output 功能，强制输出 JSON 格式评分：

```python
from pydantic import BaseModel, Field

class TurnScore(BaseModel):
    content_accuracy: float = Field(ge=0, le=10, description="内容准确性")
    logic_clarity: float = Field(ge=0, le=10, description="逻辑清晰度")
    technical_depth: float = Field(ge=0, le=10, description="技术深度")
    communication: float = Field(ge=0, le=10, description="表达能力")
    brief_comment: str = Field(description="简短点评，50字以内")

# LangChain with_structured_output
scorer = llm.with_structured_output(TurnScore)
```

评分 Prompt：

```
请根据以下面试对话，对候选人的本轮回答进行评分。

[岗位要求] {jd_context}
[面试官问题] {question}
[候选人回答] {answer}
[参考答案要点] {reference_points}

评分标准：
- content_accuracy: 回答是否正确，关键知识点是否覆盖
- logic_clarity: 回答是否有条理，逻辑是否自洽
- technical_depth: 是否有深入理解，而非表面背诵
- communication: 表达是否清晰简洁
```

## 2. 表达评分（语音特征）

从音频中提取的特征：

| 特征 | 计算方式 | 评分逻辑 |
|------|---------|---------|
| 语速 | 字数/时长 | 过快或过慢扣分，120-180字/分钟为佳 |
| 停顿比 | 静音时长/总时长 | >40% 扣分（犹豫过多） |
| 回答时长 | 总时长 | 过短(<10s)扣分，过长(>120s)扣分 |

## 3. 非语言评分（微表情+目光）

前端 MediaPipe 采集，通过 WebSocket 发送到后端：

```json
{
  "type": "expression",
  "data": {
    "emotion": "confident",
    "eye_contact": true,
    "face_detected": true,
    "confidence": 0.85
  }
}
```

| 指标 | 评分逻辑 |
|------|---------|
| 目光接触率 | 看向摄像头的时间占比，>70% 为佳 |
| 面部可见率 | 面部在画面中的时间占比 |
| 情绪稳定性 | 情绪波动幅度，过于紧张扣分 |

## 4. 综合评分公式

```
单轮得分 = 0.6 × 内容评分均值 + 0.25 × 表达评分 + 0.15 × 非语言评分

面试总分 = Σ(单轮得分 × 题目权重) / Σ(题目权重)
```

## 5. 面试报告

面试结束后生成结构化报告：

```json
{
  "overall_score": 7.8,
  "dimensions": {
    "content_accuracy": { "score": 8.0, "comment": "..." },
    "logic_clarity": { "score": 7.5, "comment": "..." },
    "technical_depth": { "score": 7.0, "comment": "..." },
    "communication": { "score": 8.5, "comment": "..." },
    "nonverbal": { "score": 7.2, "comment": "..." }
  },
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "question_details": [ ... ]
}
```
