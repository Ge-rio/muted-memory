# Intro 草稿（实验驱动版）

**Working title**：
Muted Memory: When State Machines Fail Because Prompts Tell Them to Be Quiet

---

## 摘要（中文，约 250 字）

长期陪伴 Agent 的核心体验是“情感连续性”，但现有评测几乎只测“记不记得”，很少问“让不让说”。本文报告一个反直觉的发现：在上下文截断后，一个真实触发了的状态机，可能因为人设提示中的行为抑制（如“别发作”）而在外部观测上完全不可见。我们用 20 个“承诺—违约—回归”剧本、4 种条件、3 个随机种子（共 720 次调用）做了析因实验。结果显示：强唤醒条件下，剧本级事实召回率为 58.3%，显著高于纯上下文（30.0%，p=0.003）与“被抑制的状态机”（28.3%，p=0.002）；而被抑制组与纯上下文几乎相同，恰好复现了既有研究报告的“状态机无增益”。我们据此提出“触发—表达”分离模型：记忆系统的有效性，取决于“状态是否被允许表达”。我们同时发现，LLM-as-Judge 会系统性高估“表面共情”，评测必须引入事实锚定。

## 1. Introduction（中文）

**她不是忘了，她只是被要求别说。**

这是本文的起点。我们原本想验证一个常见的工程假设：给陪伴 Agent 外挂一个跨会话的状态机，它就能在长对话里“记得”用户此前的承诺、情绪与关系。实验结果却把我们引向一个更尴尬、也更有解释力的结论：**状态被触发，不等于状态被表达。**

在 20 个“承诺—违约—回归”剧本中，我们设置了四种条件：

- **A（强唤醒）**：状态机触发，并在生成点附近明确要求“自然提及约定”；
- **A2（抑制）**：状态机同样触发，但保留人设中的“别发作/别主动”；
- **A3（自然注入）**：只给“心情低 + 原因 + 请自然回应”，不命令、不抑制；
- **B（纯上下文）**：不挂状态机，承诺在 20 轮填充后被挤出窗口。

三个随机种子、共 720 次调用后，结果稳定地呈现为一个阶梯：

| 条件 | 剧本级事实召回 | 盲评（0–2） |
|---|---|---|
| A 强唤醒 | **58.3%** | **1.22** |
| A3 自然 | 40.0% | 0.97 |
| A2 抑制 | 28.3% | 0.77 |
| B 纯上下文 | 30.0% | 0.65 |

**A 显著高于 A2（p=0.002）与 B（p=0.003）；A2 与 B 几乎无差。**

这解释了一个看似矛盾的现象：既有研究（如 ZifaMem）报告“额外增加情感状态机没有可测量增益”。他们测的很可能正是 A2 —— **状态存在，但表达被提示词层的行为抑制截断**。在外部观测上，“有记忆但不许说”与“没有记忆”无法区分。

这带来两个直接后果。

**第一，评测必须区分“失忆”与“失语”。** 我们建议同时报告两类指标：逐轮命中率（per-turn）与剧本级二值召回（per-script）。前者会被近因效应稀释——模型极少每一轮都重复同一事实；后者才对应“在给定情境下，记忆通路是否通”。本文两种都报，并说明单位选择。

**第二，记忆架构必须与表达架构解耦。** 只修“脑”（检索、存储、上下文）而不修“嘴”（人设、抑制、指令冲突），记忆系统在外部就是零。我们称之为“触发—表达”分离模型。

本文的贡献是：

1. 一个可复现的析因实验，量化“状态触发”与“状态表达”的差距（720 次调用、3 种子）；
2. 一个机制解释：行为抑制让状态机在观测上退化为无状态，复现并解释了既有“无增益”结论；
3. 一个评测建议：事实锚定 + 盲评双轨，且必须报告单位；
4. 一个设计原则：先确认她“能说”，再研究她“记不记得”。

## 2. Introduction（English）

**She did not forget. She was told not to say it.**

This paper started as a simple engineering check: if we attach an external state machine to a companion agent, will it remember promises and ruptures across sessions? The answer turned out to be less about memory than about permission.

Across 20 “promise–breach–return” scripts, four conditions, and three random seeds (720 model calls), we find a stable ladder. When the state is triggered and explicitly permitted near the generation point (**A**), script-level fact recall reaches **58.3%**, significantly above both context-only (**B**, 30.0%, p=0.003) and an *inhibited* state machine (**A2**, 28.3%, p=0.002). Crucially, **A2 is statistically indistinguishable from B**: a state machine that exists but is told to “not act up” is, from the outside, indistinguishable from no memory at all.

This reproduces, and explains, prior null results: a system whose persona suppresses expression will appear to have no benefit from memory. The failure is not in storage or retrieval, but in the expression channel.

We make four contributions:

1. A reproducible factorial study quantifying the gap between **state trigger** and **state expression**;
2. A mechanistic account: behavioral inhibition collapses an active state machine to the observational equivalent of no state;
3. An evaluation guideline: pair fact-anchored rules with blind judging, and report per-turn and per-script units;
4. A design principle: **check whether she can speak before asking whether she remembers.**

---

## 一句话

**我们不是证明了“状态机有用”，而是证明了“状态机有没有用，取决于你有没有让它开口”。**
