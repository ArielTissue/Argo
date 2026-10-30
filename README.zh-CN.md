# Argo

**知识驱动、结合个人组合上下文的投资分析与决策支持。**

Argo 将知识库、公司证据与个人组合上下文结合起来，帮助用户在决策前明确：
**为什么选择这家公司、估值依据是什么、仓位承担什么角色，以及何时需要重新判断。**

同一份财报，面对不同的组合，建议可以不同。

> **研究与学习用途，不构成投资建议。离线回放为虚构数据；Costco 历史示例使用公开财报，另行标注假设。**

## 财报分析示例：Costco FY2025

Costco 通过会员制仓储零售销售商品。示例先判断经营与现金流，再讨论估值和组合适配。

| 分析问题 | 示例观察 |
|---|---|
| 经营变化 | 全年营收增长 8.17%，营业利润率从 3.65% 升至 3.77%。 |
| 现金质量 | FCF 从 66.29 亿美元升至 78.37 亿，扣 SBC 的分析口径从 58.11 亿升至 69.77 亿。 |
| 护城河 | 要核对续费和规模经济，不能只凭会员费增长下结论。 |
| 估值 | 两组教学情景为 241.05–372.80 美元，均低于虚构的 800 美元价格，因此等待；模型假设尚未验证。 |
| 个人适配 | 另设虚构的 18% 单股占比与 15% 上限，作为补充约束。 |

[完整历史财报示例](docs/examples/costco-fy2025-analysis.md)包含官方来源、计算、
情景假设、反方判断和下一步问题。公司财务数据是真实公开披露；价格、前瞻假设和持仓均明确标注为示例，不代表当前建议。

用户可以按[实际研究操作说明](docs/research-walkthrough.md)通过自己的 Agent 宿主分析公司；
也可以运行 `argo demo --output ./demo-output`，复现另一个[全虚构的财报分析回放](docs/examples/aurx-earnings-report.md)。
公司研究不要求连接券商；离线回放不调用实时模型。

![整体框架](docs/assets/framework.svg)

*知识、公司证据与个人组合共同支持宿主 Agent 的分析；本地 harness 校验并暂存结果，
再由用户复核与确认归档。*

## 当前可以做什么

- 安装 Python CLI，自己配置 watchlist。
- 区分预计财报时间与已经验证的发布事件；没有日期的标的明确显示待确认。
- 计算示例政策下的仓位、主题和资金用途约束，保留输入时点。
- 把知识库、历史问题和账户上下文交给宿主 Agent 做分析。
- 验证结构化提案、暂存修改、展示预览，再由用户明确确认归档。
- 运行全新虚构数据的离线示例与行为测试。

## 运行示例

Python 3.11+，核心无第三方运行依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
argo demo --output ./demo-output
```

这是真实运行的 **harness 示例回放**，输入与模型回答均为固定的虚构样例。
它不调用模型、不联网、不读取账户，不能当作 Agent 分析质量评估。

自己的数据请放独立 workspace，避免混进公开仓库：

```bash
argo init ~/argo-workspace
argo watchlist ~/argo-workspace --add MSFT --company Microsoft \
  --ir-url https://www.microsoft.com/en-us/Investor
argo plan ~/argo-workspace
```

init 生成的政策、持仓和日历都是示例；真实使用前要替换。没有持仓数据时删除
portfolio.json，系统会标记上下文缺失，而不是假定空仓。

## 怎样接自己的插件

本仓库包含 Argo 本地插件与 skill。运行模型、检索公告和调用 IBKR 的能力由用户自己的
Agent 宿主提供；用户仍需在自己的宿主中安装并授权 IBKR 插件。

Argo 的 Python 核心不会自动取得宿主插件凭证。HostBroker 提供只允许读取账户和价格的
接口，但真实 IBKR transport 尚未完成集成验证。宿主本身的其他权限需要在宿主中配置。

请阅读英文 [README](README.md)、[安装说明](docs/installation.md) 和
[账户接口说明](docs/account-connection.md)。当前版本不是独立后台投资机器人，也没有下单路径。

## 框架与实现分开看

框架包括 context、research、analysis、portfolio context、skills、harness 和人工决策。
当前 Python 代码负责确定性的任务准备、计算、验收和写入；真实分析由宿主 Agent 完成。
知识摄取/维护、自动财报供应商、自动调度、ETF 穿透和回测尚未实现于此独立仓库。

[评估说明](docs/evaluation.md) 区分软件行为、模型事实正确性、分析判断和投资结果。
校验通过不等于财报提取准确、估值合理或投资有效。

### 默认分析知识库

安装包包含 15 篇价值投资概念、5 篇分析流程，以及概念索引。内容从选定的蒸馏笔记
重新用英文撰写，保留来源指引，排除个人持仓、交易、私人配置规则和练习区。
新建工作区会复制全部内容；已有工作区不会被自动覆盖。
从[框架索引](examples/knowledge/investment-framework.md)开始，
[来源与边界](docs/knowledge.md)说明哪些属于原作者框架、哪些属于分析扩展。
这些指南辅助宿主分析，不代表已验证的投资策略，也不赋予交易执行权。
