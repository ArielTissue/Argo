# Argo

**知识驱动、结合个人组合上下文的投资分析与决策支持。**

Argo 的起点是一个实际问题：凭感觉买卖后，只能希望价格朝有利方向变化。
它把公司证据、价值投资框架和个人组合放进同一个可回看的过程，帮助用户在行动前明确：
为什么买、估值依赖什么假设、这笔仓位的角色，以及什么条件下需要重新判断。

![整体框架](docs/assets/framework.svg)

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
