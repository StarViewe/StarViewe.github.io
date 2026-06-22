---
title: Claude Code Dynamic Workflow：把复杂任务变成可执行编排
date: 2026-06-22 12:00:00
tags:
  - AI
  - Claude Code
  - Dynamic Workflow
  - Agent
  - 工程效率
categories:
  - AI 工程化
---

如果你最近关注 Claude Code，大概率会看到一个新词：Dynamic Workflow。

它听起来像又一个“多 Agent”包装，但真正有意思的地方不在于 Agent 数量变多，而在于编排方式变了：Claude 不再只是在对话里一步步想下一步，而是会为任务生成一个可运行的 JavaScript 工作流脚本，由这个脚本在后台调度大量 subagent，把复杂任务拆成阶段、分支、验证和汇总。

这篇文章整理一下它是什么、为什么重要、适合什么场景，以及使用时要注意哪些坑。

## 1. 为什么大家开始讨论 Dynamic Workflow

2026 年 5 月 28 日，Anthropic 发布 Claude Opus 4.8，同时把 Dynamic Workflows 作为 Claude Code 的重要能力推出。官方对它的描述非常直接：很多过去需要按季度规划的大任务，现在有机会压缩到按天完成。

![Anthropic 官方发布 Dynamic Workflows](/images/claude-code-dynamic-workflow/official-announcement.png)

这个说法听起来很夸张，但它解决的问题确实是传统单 Agent 很难稳定处理的：

- 全代码库级别的 bug hunt
- 大规模迁移或重构
- 需要从多个角度交叉验证的研究任务
- 一次对话难以装下的多阶段工程任务

这些任务的问题不只是“上下文不够大”，而是控制流太复杂：要拆任务、分发任务、等待结果、做聚类、再验证、再汇总。以前这些动作大多靠 Claude 在聊天上下文里临时维持，一旦任务跑长，状态就会挤占上下文，模型也更容易忘掉边界或提前收敛。

Dynamic Workflow 的变化是：把计划写进代码，把中间状态留在脚本里，把验证变成流程的一部分。

![Dynamic Workflow 重写 Bun 的官方案例摘要](/images/claude-code-dynamic-workflow/bun-migration-case.png)

## 2. Dynamic Workflow 到底是什么

按官方文档的说法，Dynamic Workflow 是 Claude 写出来、可以重新运行的脚本，用来编排大量 subagent。它适合代码库审计、大迁移、交叉验证研究等任务。

我的理解是：

> Dynamic Workflow 是由 Claude 根据任务现场生成的 orchestration script。脚本负责控制阶段、循环、并发和中间状态；真正读代码、改文件、跑命令的是被脚本调度的 subagent。

这和普通 Claude Code 对话有一个本质区别。

普通对话里，Claude 是编排者。它每一步都要在上下文里记住自己做过什么、还有什么没做、哪个 subagent 返回了什么。

Dynamic Workflow 里，脚本成了编排者。Claude 生成脚本后，runtime 在后台执行脚本，脚本再调度 subagent。中间状态不必全部塞回主对话，主会话更多接收阶段性摘要和最终结果。

可以把它想成三层：

1. **外层 runtime**：负责运行 workflow，管理并发、状态、暂停、恢复和观察。
2. **中层 workflow script**：Claude 生成的 JavaScript 编排脚本，定义阶段、分支、agent 任务和汇总逻辑。
3. **内层 subagents**：真正执行读写文件、分析代码、跑测试、验证结论的工作单元。

![Dynamic Workflow 的三层结构](/images/claude-code-dynamic-workflow/three-layer-architecture.png)

这就是它比“多开几个 subagent”更重要的原因。它不是只增加执行者，而是把协调者从“临时对话”升级成了“可运行脚本”。

## 3. 它是怎么跑起来的

一次 Dynamic Workflow 大致会经历这几步：

1. 用户用自然语言描述目标。
2. Claude 根据目标生成 workflow script。
3. 用户可以在执行前查看和调整计划。
4. runtime 在后台执行脚本。
5. 脚本按阶段启动多个 subagent。
6. 每个 subagent 返回结构化结果。
7. workflow 汇总、聚类、验证、收敛。
8. 最终结果返回给用户。

一个非常简化的脚本形态可能像这样：

```js
export const meta = {
  name: 'repo-wide-duplication-audit',
  description: '扫描大型前端代码库中的重复逻辑，聚类后给出重构建议',
  phases: [
    { title: 'Detect', detail: '按目录并行检测重复逻辑' },
    { title: 'Cluster', detail: '合并重复签名并识别跨模块重复' },
    { title: 'Verify', detail: '逐簇验证是否真的值得抽象' },
  ],
}

phase('Detect')
const detections = await parallel(groups.map(group => () =>
  agent(`扫描 ${group.name} 下的重复逻辑，只返回结构化结果`, {
    label: `detect:${group.name}`,
    phase: 'Detect',
    schema: detectSchema,
  })
))

phase('Cluster')
const clusters = await agent('对所有检测结果做跨目录聚类和去重', {
  label: 'cluster',
  phase: 'Cluster',
  schema: clusterSchema,
})

phase('Verify')
const verified = await parallel(clusters.map(cluster => () =>
  agent(`对这个重复簇做对抗式验证：${JSON.stringify(cluster)}`, {
    label: `verify:${cluster.id}`,
    phase: 'Verify',
    schema: verifySchema,
  })
))

return summarize(verified)
```

重点不在语法，而在结构：检测、聚类、验证被显式拆成阶段；每个阶段的产物是下一阶段的输入；并发、收敛和验证都不再靠主对话临时记忆。

## 4. 它适合什么场景

Dynamic Workflow 不适合所有任务。它最适合“单个 agent 一遍看不完、一个对话协调不了”的任务。

![适合使用 Dynamic Workflow 的任务类型](/images/claude-code-dynamic-workflow/use-cases.png)

典型场景包括：

### 4.1 全库审计

比如扫描一个大型代码库里的重复逻辑、潜在 bug、安全风险、跨端兼容问题。单个 agent 很容易只看到局部，Dynamic Workflow 可以按目录或模块扇出多个 subagent，再统一聚类和复核。

### 4.2 大规模迁移

比如把一套旧框架迁移到新框架，把一种语言迁移到另一种语言，或把大量文件按同一套规则重写。官方文章里提到的 Bun 迁移案例，就是这类任务的代表。

### 4.3 交叉验证研究

当你不只是要一个答案，而是要多个视角互相质疑、互相校验时，workflow 很适合把同一个问题分给不同 subagent，再比较它们的交集与分歧。

### 4.4 多阶段问题排查

有些 bug 不是看一两个文件就能定位的，而是涉及调用链、状态流、平台差异、历史兼容和测试覆盖。Dynamic Workflow 可以先广泛探索，再逐步收敛到高可信候选。

我的判断标准是：

> 如果任务涉及大量文件、多个阶段、需要并行探索和交叉验证，考虑 Dynamic Workflow。如果任务边界很小、步骤稳定、路径明确，普通 Claude Code 对话、subagent 或静态命令通常更划算。

## 5. 它和 Skill、Slash Command 有什么区别

很多人第一次看到 Dynamic Workflow，会把它和 Skill、Slash Command 混在一起。它们确实都能沉淀经验，但沉淀的东西不同。

| 维度 | Skill | Slash Command | Dynamic Workflow |
| --- | --- | --- | --- |
| 本质 | Claude 遵循的说明书 | 可复用的触发入口 | runtime 执行的编排脚本 |
| 谁负责控制流 | Claude | Claude | 脚本 |
| 中间状态在哪里 | Claude 上下文 | Claude 上下文 | 脚本变量 / runtime 状态 |
| 适合规模 | 小到中型任务 | 固定流程入口 | 大规模、多阶段任务 |
| 可复用的是 | 方法和约束 | 命令入口和 prompt | 编排结构本身 |

Skill 更像“做事规范”：告诉 Claude 遇到某类任务时怎么思考、怎么执行、怎么验收。

Slash Command 更像“快捷入口”：把常用动作封装成 `/review`、`/release`、`/handoff` 这样的命令。

Dynamic Workflow 更像“执行系统”：把循环、分支、并发、状态和验证写成脚本，让 runtime 去跑。

所以它们不是互相替代的关系。更合理的组合是：

- 用 Skill 定义团队工作原则和验收标准。
- 用 Slash Command 固化常用入口。
- 用 Dynamic Workflow 承接大规模、长链路、高并发的任务。

![普通 subagent/skill 与 Workflow 的上下文占用对比](/images/claude-code-dynamic-workflow/context-comparison.png)

## 6. 优点：它把 harness 门槛降下来了

我觉得 Dynamic Workflow 最有价值的点，是它把 harness 的技术门槛降低了。

![Dynamic Workflow 的主要优点](/images/claude-code-dynamic-workflow/advantages.png)

过去，如果你想做一个稳定的 agent loop，通常需要自己写脚本、设计状态机、处理并发、定义输出 schema、加验证环节。这更像工程系统开发，而不是普通使用者能随手完成的事情。

Dynamic Workflow 把这件事往前推了一步：

1. 你用自然语言描述目标。
2. Claude 生成一个临时 harness。
3. 你查看计划，调整边界。
4. 运行后观察效果。
5. 如果有价值，再把脚本保存、复用、继续打磨。

也就是说，它让“临时 prompt”有机会升级成“可复用工程资产”。

这和 Loop Engineering 的趋势是一致的：未来真正重要的不是写出某一次漂亮回答，而是设计能持续运行、持续观察、持续验证、持续收敛的工作循环。

## 7. 缺点：它很贵，也不是总能跑好

Dynamic Workflow 很强，但不是银弹。

![Dynamic Workflow 的主要限制](/images/claude-code-dynamic-workflow/tradeoffs.png)

### 7.1 Token 成本高

它可能启动几十到几百个 subagent。每个 agent 都要读上下文、查文件、输出结果。任务一大，token 消耗会非常明显。

所以不要把它当默认模式。它更像重型工具，适合用在确实复杂、确实需要并行和验证的任务上。

### 7.2 启动前必须明确边界

如果你给的目标太宽，workflow 可能会把问题展开得过大，导致时间和成本都失控。

比较好的做法是执行前要求 Claude 先展示计划：

- 有哪些阶段
- 每个阶段预计启动多少 agent
- 每个阶段使用什么模型
- 输入范围是什么
- 输出物是什么
- 预计 token 上限是多少

确认后再跑。

### 7.3 自动生成的 workflow 不一定最优

Claude 能生成 workflow，但它第一次生成的不一定是最高效的 harness。尤其在迁移、重构、全库扫描这类任务里，目录分片、模型分配、schema 设计、验证策略都会影响结果。

更现实的用法是：让 Claude 先生成一个版本，人再审查和优化，把跑通的 workflow 变成团队资产。

### 7.4 运行中不适合频繁交互

Workflow 本质是后台运行的脚本。它不是每一步都等你插话确认，更多是在执行前确认计划、执行中观察状态、执行后复盘结果。

如果任务需要高频人类判断，普通对话或分阶段手动推进可能更稳。

## 8. 实践建议

### 8.1 先让它展示 workflow plan

不要一上来就让它执行。可以先要求：

```text
请先不要执行。先展示 Dynamic Workflow 计划：
1. 阶段划分
2. 每阶段 agent 数量
3. 每阶段模型选择
4. 每阶段输入范围
5. 每阶段输出 schema
6. 预计 token 预算
7. 失败或不确定时如何收敛
等我确认后再执行。
```

这一步能显著减少“任务发散过大”的问题。

### 8.2 广度任务用便宜模型，收敛任务用强模型

很多 workflow 可以拆成两类阶段：

- 广度探索：大量文件扫描、候选发现、初步分类
- 深度收敛：对候选做验证、排序、方案设计

前者可以用更便宜、更快的模型；后者再交给更强模型。这样通常比全程昂贵模型更可控。

### 8.3 输出必须结构化

如果每个 subagent 都自由发挥，最后汇总会很痛苦。建议在 workflow 里给每个阶段定义 schema。

比如检测重复逻辑时，要求每个 agent 返回：

- `signature`
- `category`
- `severity`
- `instances`
- `suggestedTarget`
- `rationale`

结构化输出越稳定，后续聚类和验证越可靠。

### 8.4 一定要有验证阶段

Dynamic Workflow 最容易被滥用的地方，是让很多 agent 产生大量候选，然后把候选直接当结论。

更稳的做法是：候选发现只是第一阶段，后面必须有验证阶段。验证 agent 要默认怀疑前面的结论，重新读源文件、检查差异、评估风险，最后再决定是否确认。

### 8.5 把跑通的 workflow 保存下来

一次跑通只是开始。真正有价值的是把它保存成可复用脚本或命令。

团队可以逐渐沉淀出一批高价值 workflow：

- 全库重复逻辑审计
- 移动端兼容性排查
- 安全敏感路径 review
- 大版本迁移计划生成
- 多模型交叉 bug hunt

这些东西比一次 prompt 更有长期价值。

## 9. 我会如何选择工具

我的使用偏好大概是：

- **小改动**：直接 Claude Code 对话。
- **独立探索**：用 subagent。
- **固定流程**：用 Slash Command。
- **团队规范**：用 Skill。
- **大规模复杂任务**：用 Dynamic Workflow。

一个任务如果只是“帮我改这个函数”，开 Dynamic Workflow 就太重了。

但如果任务是“扫描整个项目，找出重复逻辑，聚类，验证，给出可执行重构方案”，那 Dynamic Workflow 就很合适。因为它的优势正好在于多阶段、并行、状态外置和最终收敛。

## 10. 结语

Dynamic Workflow 的核心变化，不是让 Claude Code 多几个 agent，而是让 AI 从即时响应式助手，变成能承接大型复杂任务的执行结构。

它把原本需要工程师手写的 harness，变成了 Claude 可以现场生成、用户可以审查、团队可以沉淀的工作流资产。

这也是我觉得它值得关注的原因：它代表的不是某个按钮或某个模型能力，而是 Agent 工程化的一种方向。

未来的 Agent 不会只比“谁回答得更好”，还会比谁更会组织工作、验证结果、控制成本、沉淀流程。

Dynamic Workflow 就是朝这个方向迈出的一步。

## 参考资料

- [Introducing dynamic workflows in Claude Code](https://claude.com/blog/introducing-dynamic-workflows-in-claude-code)
- [Claude Code Docs: Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows)
- [Claude Code Docs: Run agents in parallel](https://code.claude.com/docs/en/agents)
- [Claude Code Docs: Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8)
