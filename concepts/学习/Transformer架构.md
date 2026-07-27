---
type: concept
date_updated: 2026-07-25
tags: [学习/, 学习/深度学习]
confidence: high
---

# Transformer 架构

> 源：[[sources/学习/Transformer论文]] — Vaswani et al., "Attention Is All You Need", NeurIPS 2017

## 架构总览

Transformer 采用 Encoder-Decoder 结构，完全基于注意力机制，不含任何循环或卷积：

```
Encoder: 6× [Multi-Head Self-Attention → Add & Norm → FFN → Add & Norm]
Decoder: 6× [Masked Multi-Head Self-Attention → Add & Norm
             → Multi-Head Cross-Attention → Add & Norm → FFN → Add & Norm]
Output:  Linear → Softmax
```

每个子层后接残差连接（Residual Connection）+ 层归一化（LayerNorm），即 `LayerNorm(x + Sublayer(x))`。

## Scaled Dot-Product Attention

### 公式

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中：
- **Q (Query)**：[seq_len, d_k] — 当前要查询的位置
- **K (Key)**：[seq_len, d_k] — 要被查询的所有位置
- **V (Value)**：[seq_len, d_v] — 实际携带信息的表示

### 为什么除以 √d_k

当 d_k 较大时，点积 QK^T 的方差增大（~d_k），导致 softmax 进入梯度极小的饱和区。除以 √d_k 将方差缩放回 1，保持 softmax 在合理的梯度区间。这是论文中最精巧的工程细节之一。

## Multi-Head Attention

### 机制

将 Q、K、V 分别线性投影 h 次（h=8），每个头独立计算 Scaled Dot-Product Attention，最后拼接结果再投影：

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h) W^O$$

$$\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

### 维度

- d_model = 512
- h = 8（头数）
- d_k = d_v = d_model / h = 64

### 为什么多头

不同头关注不同的表示子空间——有的头关注相邻位置（局部语法），有的头关注远距离语义关联（指代消解），相当于让模型同时从多个角度理解序列。论文通过可视化验证了不同头确实学到了互补的注意力模式。

## 三种注意力用法

Transformer 中使用三种注意力形式：

| 类型 | 位置 | Q 来源 | K, V 来源 | 说明 |
|------|------|--------|-----------|------|
| Encoder Self-Attention | Encoder 每层 | 当前 Encoder 层输出 | 同左 | 每个位置注意输入序列所有位置 |
| Decoder Masked Self-Attention | Decoder 每层 | 当前 Decoder 层输出 | 同左 | 用 mask 防止注意未来位置（自回归约束） |
| Encoder-Decoder Cross-Attention | Decoder 每层 | Decoder 前一子层输出 | Encoder 最终输出 | Decoder 每个位置查询 Encoder 所有位置，实现跨序列信息整合 |

## Position-wise Feed-Forward Network

每层 Attention 后接一个全连接前馈网络，对每个位置独立应用相同的变换：

$$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

- 输入维度：512 → 内层升维到 2048 → 降回 512
- 激活函数：ReLU（max(0, x)）
- 两层之间有大量参数集中于此（d_model × d_ff × 2），是模型容量的主要来源

## Positional Encoding

由于 Transformer 不含循环或卷积，本身没有序列位置信息。论文用正弦/余弦函数将位置编码注入输入表示：

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

### 为什么用正弦/余弦

- 每个维度对应不同频率的正弦波，从 2π 到 ~20000π
- 允许模型通过线性组合关注相对位置（PE_{pos+k} 可由 PE_{pos} 线性表示）
- **可以外推**到训练时未见过的更长序列长度

## 关键超参数

| 参数 | 值 | 说明 |
|------|-----|------|
| d_model | 512 | 词嵌入和所有子层输出的维度 |
| d_ff | 2048 | FFN 内层维度（4× d_model） |
| h | 8 | Multi-Head Attention 头数 |
| d_k, d_v | 64 | 每个头的 Query/Key 和 Value 维度 |
| N | 6 | Encoder 和 Decoder 层数 |
| Dropout | 0.1 | 每个子层和嵌入层的 dropout 率 |
| Label Smoothing | 0.1 | 正则化，防止模型对训练标签过度自信 |

## 模型规模

| 模型 | 层数 | d_model | d_ff | h | 参数量 |
|------|------|---------|------|---|--------|
| Transformer Base | N=6 | 512 | 2048 | 8 | 65M |
| Transformer Big | N=6 | 1024 | 4096 | 16 | 213M |

## 训练策略

- **优化器**：Adam（β1=0.9, β2=0.98, ε=10^−9），β2 接近 1 以应对注意力稀疏梯度的噪声
- **学习率调度（Noam）**：前 4000 步线性 warmup，之后按 step_num^−0.5 衰减
- **硬件**：8× P100 GPU；Base 训练 12 小时，Big 训练 3.5 天

## 架构意义

Transformer 的核心洞察是：*序列处理不需要序列计算*。通过自注意力，任意两个位置之间建立直接的、常数步的计算路径，从根本上绕开了 RNN 的顺序瓶颈。这一洞察使训练可大规模并行化，直接催生了后续的 GPT、BERT、LLaMA 等预训练大模型范式。

## 相关概念

- [[sources/学习/Transformer论文]] — 论文原文摘要与完整结果
