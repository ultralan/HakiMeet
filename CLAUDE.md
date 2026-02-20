# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
You need to update it when executing the /init command.

## 项目概述

HakiMeet - 基于多模态大模型的 AI 模拟面试系统。支持 WebRTC 实时音视频交互、3D 数字人面试官、RAG 知识库驱动的智能提问、多维度面试评分。

## 开发命令

### 可用的mcp工具

## 架构说明

### 主要框架

- 前端: Vue 3 + Vite + Pinia + Three.js
- 后端: Python 3.11+ / FastAPI / aiortc / LangChain
- AI模型: 豆包语音大模型(实时语音对话) + Gemini 2.0 Flash(视觉分析+评分)
- 向量库: ChromaDB (本地)
- TTS: 豆包语音大模型自带(Edge-TTS为降级备选)
- 数据库: SQLite (开发) / PostgreSQL (生产)



### 插件工具



### 项目目录（该文本只允许扩展而非删除或修改）
├── backend/              # 后端（项目主体）
│   ├── app/              # FastAPI 应用
│   ├── ai/               # AI引擎（LangChain + RAG）
│   ├── rtc/              # WebRTC（aiortc）
│   └── tts/              # 语音合成（Edge-TTS）
├── docs/                 # 文档（开发过程中产生的计划文档）
│   └── design/           # 技术设计文档
├── frontend/             # 前端（Vue 3 + Vite）
│   ├── src/components/   # 组件
│   ├── src/views/        # 页面
│   └── src/stores/       # Pinia状态管理
├── logs/                 # 日志（统一用.log文件输出而非终端）
├── scripts/              # 脚本（开发过程中用于执行一次性任务）
├── ...
└── CLAUDE.md             # 项目宪法（本文档）

## 设计文档

详见 `docs/design/` 目录：
- `00-architecture.md` - 整体架构
- `01-tech-stack.md` - 技术栈选型
- `02-communication.md` - 通信协议设计（WebRTC + WebSocket + REST）
- `03-ai-engine.md` - AI引擎（豆包语音 + Gemini视觉 + RAG）
- `04-3d-avatar.md` - 3D数字人 + 口型同步
- `05-scoring.md` - 评分系统
- `06-data-model.md` - 数据模型
- `07-dev-plan.md` - 开发阶段规划

## 注意事项

- 开发按 Phase 1→5 顺序推进，先跑通文字对话核心链路
- 双模型架构：豆包负责实时语音对话(支持打断)，Gemini负责视觉分析+评分
- 语音走 WebRTC → 后端aiortc → 桥接豆包WebSocket API（后端做RAG注入+录音+对话控制）
- 3D数字人有降级方案：完整口型同步 → 简单张嘴 → 2D动画
