---
type: source
date_updated: 2026-07-25
tags: [学习/, 学习/深度学习]
---

# Attention Is All You Need

## 基本信息

- **标题**：Attention Is All You Need
- **作者**：Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin（8 人等同贡献，Google Brain / Google Research / 多伦多大学）
- **发表**：NeurIPS 2017 | arXiv: 1706.03762
- **引用地位**：深度学习领域里程碑论文，截至 2026 年引用量超过 15 万次，彻底重塑了 NLP 乃至整个 AI 领域的架构范式

## 摘要

主流的序列转换模型基于包含编码器和解码器的复杂循环或卷积神经网络。性能最佳的模型还通过注意力机制连接编码器和解码器。我们提出了一种新的简单网络架构 Transformer，完全基于注意力机制，彻底摒弃了循环和卷积。在两个机器翻译任务上的实验表明，这些模型在质量上更优，同时并行性更强，训练时间显著减少。在 WMT 2014 英德翻译任务上达到 28.4 BLEU，比此前最佳结果（包括集成模型）提高超过 2 BLEU。在 WMT 2014 英法翻译任务上，使用 8 个 GPU 训练 3.5 天后，单一模型达到 SOTA 的 41.8 BLEU。

## 核心创新

首次证明仅靠自注意力机制（Self-Attention）就能完成序列转换任务，完全不用 RNN 或 CNN。解决了 RNN 的两个根本性局限：

1. **无法并行化**：RNN 的序列计算本质（第 t 步依赖第 t−1 步的输出）使得训练时无法并行展开
2. **长距离依赖衰减**：梯度在长序列中反向传播时指数衰减，远距离位置间的信号几乎消失

> 核心架构见 [[concepts/学习/Transformer架构]]

## 架构概览

- 6 层 Encoder + 6 层 Decoder，每层含 Multi-Head Self-Attention + Position-wise FFN，每个子层后接残差连接 + LayerNorm
- **Scaled Dot-Product Attention**：Attention(Q,K,V) = softmax(QK^T/√dk)V，除以 √dk 防止点积过大导致梯度消失
- **Multi-Head Attention**：8 头并行注意力，h=8, dk=dv=dmodel/h=64，不同头关注不同表示子空间
- **Positional Encoding**：正弦/余弦位置编码，支持外推到训练时未见过的序列长度
- **超参数**：d_model=512, d_ff=2048, Dropout=0.1, Label Smoothing=0.1
- **模型规模**：Base 65M 参数，Big 213M 参数

## 为什么 Self-Attention

论文从三个维度对比 Self-Attention 与 RNN、CNN：

| 层类型            | 每层复杂度     | 最少串行操作 | 最大路径长度      |
| -------------- | --------- | ------ | ----------- |
| Self-Attention | O(n²·d)   | O(1)   | O(1)        |
| RNN            | O(n·d²)   | O(n)   | O(n)        |
| CNN            | O(k·n·d²) | O(1)   | O(log_k(n)) |

关键优势：任意两位置只需常数步操作即可交互，彻底消除长距离依赖问题。

## 训练细节

- **优化器**：Adam（β1=0.9, β2=0.98, ε=10^−9）
- **学习率**：warmup_steps=4000 后 Noam 衰减策略（linear warmup → inverse sqrt decay）
- **硬件**：8× NVIDIA P100 GPU
- **训练时间**：Base 12 小时，Big 3.5 天

## 关键结果

| 任务 | 模型 | BLEU | 备注 |
|------|------|------|------|
| WMT 2014 EN-DE | Transformer (Big) | 28.4 | 超越所有已有模型（含集成），+2 BLEU |
| WMT 2014 EN-FR | Transformer (Big) | 41.8 | 单一模型 SOTA，仅用 1/4 训练成本 |
| WSJ 句法分析 | Transformer | 92.7 F1 | 半监督设置，证明跨任务泛化能力 |

## 论文贡献与影响

1. **架构范式转换**：RNN/CNN 主导 → 纯注意力机制，开启 post-RNN 时代
2. **规模化训练成为可能**：并行化带来训练效率数量级提升，为后来的 GPT、BERT、LLaMA 等奠定基础
3. **彻底解决长距离依赖**：常数步路径长度（O(1)），任意两位置直接交互
4. **注意力可解释性**：注意力权重可直接可视化，揭示语法/语义结构（指代消解、从句边界等）
5. **多模态前瞻**：作者明确提到计划扩展到图像、音频、视频——预示了后来的 ViT、DALL·E、Sora 等多模态模型

## 参见

- [[concepts/学习/Transformer架构]] — Transformer 架构核心概念详解
