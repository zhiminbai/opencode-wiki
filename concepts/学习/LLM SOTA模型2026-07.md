---
type: concept
date_updated: 2026-07-25
tags: [学习/, 学习/深度学习]
confidence: high
---

# LLM SOTA 模型概况（2026 年 7 月）

> 数据来源：BenchLM BenchAlign、LMArena Chatbot Arena、Artificial Analysis Intelligence Index、SWE-bench、LiveCodeBench 等多个排行榜。

## 综合排名 Top 10（BenchLM BenchAlign）

| # | 模型 | 厂商 | 评分 | 备注 |
|---|------|------|------|------|
| 1 | Claude Opus 5 | Anthropic | 85.9 | 最新旗舰（Estimated） |
| 2 | Claude Mythos 5 | Anthropic | 83.0 | Mythos 级旗舰 |
| 3 | Claude Fable 5 | Anthropic | 82.8 | 7 月 1 日回归 |
| 4 | GPT-5.6 Sol | OpenAI | 81.5 | 7 月 9 日发布 |
| 5 | Kimi K3 | Moonshot AI | 80.0 | 2.8T 参数，1M 上下文 |
| 6 | Claude Opus 4.8 | Anthropic | 77.4 | 5 月 28 日发布 |
| 7 | Muse Spark 1.1 | Meta | 76.6 | |
| 8 | Grok 4.5 | xAI | 75.6 | 7 月 8 日发布，$2/$6 |
| 9 | Gemini 3.6 Flash | Google | 75.5 | |
| 10 | GPT-5.4 | OpenAI | 73.4 | |

## 按能力分赛道冠军

### Coding（编码）

- **最强**：Claude Mythos 5 — SWE-bench Pro 80.3%，SWE-bench Verified 95.5%
- Fable 5 紧随其后（80% Pro），Opus 4.8 性价比之选（69.2% Pro）
- GPT-5.6 Sol — BrowseComp 92.2%，Terminal-Bench 2.1 88.8%（Agent 方向领先）

### Reasoning（推理）

- **最强**：Gemini 3.1 Pro — GPQA Diamond 94.3%，HLE 44.4%，ARC-AGI-2 77.1%
- Claude Mythos 5 — HLE（人类最后考试）64.5%，断崖领先

### Multimodal（多模态）

- **最强**：Gemini 3.1 Pro — MMMU-Pro 81%，2M token 上下文，支持音频视频

### Arena（人类偏好）

- **最强**：Claude Fable 5 — Arena Elo 1525
- GPT-5.6 Sol 1514，Opus 4.8 1512，前三差距极小

### 竞技编程

- **最强**：Qwen3.7 Max — LiveCodeBench 91.6%

### 开源模型

- **综合最强**：MiniMax M3 — BenchAlign 68.8
- **编码最强**：GLM-5.2
- **性价比之王**：DeepSeek V4 Pro — GPQA 90.1%，MIT 开源，$0.87/M output，1.6T 参数

## 格局判断

1. **Anthropic 三旗舰包揽前三**：Opus 5 > Mythos 5 > Fable 5 全面领先
2. **GPT-5.6 Sol 在 Agent 赛道反超**：BrowseComp 92.2% 为 SOTA
3. **Kimi K3 代表中国最高水平**：综合第 5，$3/$15
4. **开源差距仍约 14 分**：MiniMax M3 68.8 vs Mythos 83，DeepSeek V4 Pro 用价格弥补
5. **Grok 4.5 定价激进**：$2/$6 对标 Opus 4.8 $5/$25
6. **多模态 Gemini 无对手**：2M 上下文 + 音视频输入
