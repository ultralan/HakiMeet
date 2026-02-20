# 数据模型设计

## ER 关系

```
User 1──N Resume
User 1──N Interview
Interview 1──N InterviewTurn
Interview N──1 JobPosition
InterviewTurn 1──1 TurnScore
```

## 表结构

### users

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 用户ID |
| username | VARCHAR(50) | 用户名 |
| password_hash | VARCHAR(128) | 密码哈希 |
| created_at | TIMESTAMP | 创建时间 |

### resumes

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 简历ID |
| user_id | UUID FK → users | 所属用户 |
| filename | VARCHAR(255) | 原始文件名 |
| raw_text | TEXT | 解析后的纯文本 |
| file_path | VARCHAR(500) | 文件存储路径 |
| vectorized | BOOLEAN | 是否已向量化 |
| created_at | TIMESTAMP | 上传时间 |

### job_positions

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 岗位ID |
| title | VARCHAR(100) | 岗位名称 |
| description | TEXT | 岗位JD |
| requirements | TEXT | 技能要求 |
| difficulty | VARCHAR(20) | 难度: junior/mid/senior |

### interviews

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 面试ID |
| user_id | UUID FK → users | 面试者 |
| resume_id | UUID FK → resumes | 使用的简历 |
| job_id | UUID FK → job_positions | 目标岗位 |
| status | VARCHAR(20) | pending/active/completed |
| overall_score | FLOAT | 总分 |
| report | JSON | 面试报告JSON |
| started_at | TIMESTAMP | 开始时间 |
| ended_at | TIMESTAMP | 结束时间 |

### interview_turns

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 轮次ID |
| interview_id | UUID FK → interviews | 所属面试 |
| turn_number | INT | 第几轮 |
| ai_question | TEXT | 面试官问题 |
| user_answer | TEXT | 用户回答(转写文本) |
| audio_duration | FLOAT | 回答音频时长(秒) |
| expression_data | JSON | 微表情采集数据 |
| created_at | TIMESTAMP | 时间戳 |

### turn_scores

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 评分ID |
| turn_id | UUID FK → interview_turns | 所属轮次 |
| content_accuracy | FLOAT | 内容准确性 0-10 |
| logic_clarity | FLOAT | 逻辑清晰度 0-10 |
| technical_depth | FLOAT | 技术深度 0-10 |
| communication | FLOAT | 表达能力 0-10 |
| nonverbal | FLOAT | 非语言表现 0-10 |
| comment | TEXT | AI点评 |
