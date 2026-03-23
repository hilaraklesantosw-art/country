# gstack 由浅入深教程

## 1. gstack 是什么

`gstack` 是 Garry Tan 开源的一套 AI 编程工作流工具箱。它的核心不是提供一个新的大模型，也不是一个单独的命令行二进制，而是一组可安装的 skills 和一条完整的软件交付流程。

它试图解决的问题是：很多人已经开始用 Claude Code、Codex、Gemini CLI 之类的代理写代码，但流程仍然是碎片化的。你可能会让模型写功能、修 bug、生成文档，但缺少一套稳定的“从想法到上线”的协作顺序。`gstack` 的做法是把这个顺序做成一组角色化技能，让代理像一个小型软件团队一样工作。

官方给出的核心流程是：

```text
Think → Plan → Build → Review → Test → Ship → Reflect
```

在这个流程里，`/office-hours` 负责重新定义问题，`/plan-eng-review` 负责把架构和测试边界锁住，`/review` 负责做严格代码审查，`/qa` 用真实浏览器测站点，`/ship` 开 PR，`/land-and-deploy` 负责合并部署，`/retro` 做复盘。

如果只用一句话总结它，可以这么理解：

**gstack 不是“再多一些 prompt”，而是把 AI 编程变成一条有步骤、有角色、有衔接的软件交付流水线。**

参考：

- GitHub 仓库: https://github.com/garrytan/gstack
- README: https://github.com/garrytan/gstack/blob/main/README.md

## 2. 它适合什么人

根据 README，`gstack` 主要适合以下几类人：

- 技术创始人和 CEO
- 第一次用 Claude Code 的人
- Tech Lead 和高级工程师
- 想让 AI 不只是“写代码”，而是“推动完整 sprint”的开发者

如果你只是偶尔问模型一个函数怎么写，那么未必需要 `gstack`。但如果你已经在真实项目里频繁用 AI，并且开始遇到这些问题：

- 需求一会儿这样一会儿那样，没有收敛
- 写完代码后没人做严格 review
- 改完页面没人做真正的 QA
- 发布前后缺少统一流程
- 每次都从空 prompt 开始

那 `gstack` 就很值得试。

## 3. 它的核心思想

`gstack` 的关键，不是技能数量多，而是技能之间有上下游关系。

官方在 README 里明确强调：每个技能都会给下一个技能提供输入。例如：

- `/office-hours` 写设计文档
- `/plan-ceo-review` 读取设计文档进一步收敛产品
- `/plan-eng-review` 基于设计文档输出架构、边界、测试计划
- `/qa` 会读取前面的测试计划和页面上下文
- `/ship` 会验证 review 和 QA 后的结果是否收敛

这意味着它不是“工具集合”，而是“流程系统”。

如果你照着这个流程跑下来，AI 的角色不再是“时不时帮你写点代码”，而是像一支小团队：

- 产品负责人
- 工程经理
- 设计顾问
- 代码审查者
- QA
- 安全负责人
- 发布工程师

这也是 `gstack` 最有特色的地方。

## 4. 安装方式

### 4.1 Claude Code 安装

README 推荐将 `gstack` 安装到 `~/.claude/skills/gstack`，然后运行 `./setup`，再在 `CLAUDE.md` 中声明 `gstack` 相关配置。

安装命令在 README 中是直接给 Claude Code 执行的整段说明，这里不重复展开，建议直接参考官方 README 安装部分。

### 4.2 Codex / Gemini CLI / Cursor 安装

如果你用的是 Codex 这类支持 `SKILL.md` 标准的代理宿主，README 推荐两种方式。

单仓库安装：

```bash
git clone https://github.com/garrytan/gstack.git .agents/skills/gstack
cd .agents/skills/gstack && ./setup --host codex
```

全局安装：

```bash
git clone https://github.com/garrytan/gstack.git ~/gstack
cd ~/gstack && ./setup --host codex
```

自动检测宿主：

```bash
git clone https://github.com/garrytan/gstack.git ~/gstack
cd ~/gstack && ./setup --host auto
```

README 还说明了：

- repo-local 安装会放在当前仓库的 `.agents/skills/gstack`
- user-global 安装会放在 `~/.codex/skills/gstack`
- 所有技能会按宿主自动生成和链接

参考：

- README 安装章节: https://github.com/garrytan/gstack/blob/main/README.md

## 5. 最小上手路线

如果你第一次用 `gstack`，不要试图把所有技能都学会。官方推荐的最小体验路径非常明确：

1. 安装 `gstack`
2. 跑 `/office-hours`
3. 跑 `/plan-ceo-review`
4. 在有改动的分支上跑 `/review`
5. 对 staging URL 跑 `/qa`

这条路径的目的不是“全功能体验”，而是让你先感受到它的工作流价值。

如果这一步你已经明显感觉到：

- 需求定义更清楚了
- review 更严格了
- QA 更像真的在测产品

那你就知道它值不值得继续用。

## 6. 先学会最重要的 5 个技能

### 6.1 `/office-hours`

这是 `gstack` 的起点技能。它像 YC 式的产品讨论，不是简单接受你说的需求，而是会反问、质疑、重新定义问题。

适用场景：

- 想做一个新产品
- 想加一个大功能
- 不确定问题是否定义正确

典型效果：

- 把“我要做个什么功能”重构成“我到底要解决什么问题”
- 逼你从用户痛点而不是表面功能出发

示例：

```text
我想做一个 AI 日历简报工具，帮我先用 /office-hours 梳理这个产品方向。
```

### 6.2 `/plan-ceo-review`

这个技能站在 CEO / Founder 的角度重新审题。它更关注：

- 这个需求是不是太大了
- 有没有更尖锐的切入点
- 是否真的有 10x 价值

适用场景：

- 产品方向刚刚形成
- 想让范围更收敛
- 想避免“功能很多但价值模糊”

### 6.3 `/plan-eng-review`

这个技能从工程视角做计划审查。它不是单纯写架构文档，而是逼你把隐含前提显性化。

会关注：

- 数据流
- 边界条件
- 状态流转
- 错误路径
- 测试矩阵
- 安全问题

适用场景：

- 开工前锁技术方案
- 复杂功能上线前做工程把关

### 6.4 `/review`

这是最值得日常高频使用的技能之一。它做严格代码审查，目标是找出那些：

- CI 不一定发现
- 运行时才会炸
- 逻辑完整性有缺口
- 看起来能跑但长期会出问题

适用场景：

- 每次 feature 开发完成后
- 提交 PR 前
- 合并前再做一次把关

### 6.5 `/qa`

这是 `gstack` 的另一个亮点。它不是只看代码，而是会在真实浏览器里点页面、走流程、发现 bug，必要时还会补回归测试。

适用场景：

- Web 项目
- 有 staging 环境
- 改了交互流程后想做回归

如果你已经有一个可访问的预发布地址，可以直接这样用：

```text
/qa https://staging.example.com
```

## 7. 完整流程怎么跑一遍

假设你要做一个“小型日历每日简报应用”，可以按下面的顺序体验一次真正的 `gstack` 流程。

### 第一步：先重新定义产品

```text
/office-hours
我想做一个每日简报 app，连接多个日历，自动生成一天的准备信息。
```

这一步的重点不是马上写代码，而是搞清楚：

- 用户真正的问题是什么
- “每日简报”是不是正确切入点
- 最小可验证版本是什么

### 第二步：做产品收敛

```text
/plan-ceo-review
```

让它判断：

- 范围是不是太大
- 是否存在更清晰的第一阶段
- 用户价值是否足够强

### 第三步：锁技术方案

```text
/plan-eng-review
```

这一步会把：

- 架构
- 数据流
- 边界情况
- 测试策略

都拉出来讨论。

### 第四步：开始实现

当 plan 过关后，再进入编码阶段。

### 第五步：做代码审查

```text
/review
```

这一步的目的是在你自己感觉“差不多写完了”的时候，再用更严苛的标准审一次。

### 第六步：做页面 QA

```text
/qa https://staging.example.com
```

让它真实打开页面、点击流程、发现交互问题。

### 第七步：准备发版

```text
/ship
```

README 里对 `/ship` 的描述是：

- 同步 main
- 跑测试
- 审查覆盖率
- push
- 开 PR

### 第八步：合并上线

```text
/land-and-deploy
```

它负责从“PR 已批准”推进到“CI 和部署完成，并验证生产健康”。

### 第九步：上线后复盘

```text
/retro
```

这一步可以帮助你建立持续改进节奏，而不是做完就结束。

## 8. 其他实用技能

### `/investigate`

用于系统化定位根因。README 里强调“没有 investigation 就不要修复”。这很适合：

- 遇到反复修不好的 bug
- 需要先搞清楚数据流和出错路径

### `/design-review`

用于审查和修正界面设计，适合前端项目。

### `/design-consultation`

更偏完整设计系统和创意方向，适合做新产品设计探索。

### `/benchmark`

适合做性能基准和前后对比，特别是 Web 项目。

### `/cso`

做安全审查。README 中提到它结合 OWASP Top 10 和 STRIDE。

### `/document-release`

发版后同步更新项目文档，避免 README 和实际功能脱节。

### `/codex`

这是一个“第二意见”技能，会调用 OpenAI Codex CLI 做独立审查或咨询。很适合：

- 关键 PR 做交叉验证
- 想让不同模型给第二意见

## 9. 安全相关技能怎么理解

`gstack` 还提供一些“保险丝”技能。

### `/careful`

在执行危险命令前提醒你，例如：

- `rm -rf`
- 强制 push
- 可能影响生产的命令

### `/freeze`

把编辑范围锁在某个目录里，适合：

- 调试时只想动一个模块
- 不希望代理误改其他目录

### `/guard`

把 `/careful` 和 `/freeze` 组合起来，适合高风险工作。

### `/unfreeze`

解除限制。

这几个技能不是让你变慢，而是帮你在高风险环境里更稳。

## 10. 浏览器能力为什么重要

`gstack` 的浏览器能力是一个非常实用的差异点。

README 里提到：

- `/browse` 使用真实 Chromium 浏览器
- `/qa` 会用真实浏览器测试页面
- `/setup-browser-cookies` 可以把你真实浏览器里的 cookies 导入到 headless session

这意味着你可以让它测试：

- 登录后页面
- 后台系统
- 复杂 Web 流程
- 带权限控制的页面

对 Web 项目来说，这个能力比“只看代码”更接近真实交付。

## 11. 目录结构怎么看

从仓库目录看，`gstack` 基本采用“一技能一目录”的组织方式，例如：

- `office-hours`
- `plan-ceo-review`
- `plan-eng-review`
- `review`
- `qa`
- `ship`
- `retro`
- `browse`
- `benchmark`
- `cso`

此外还有几个值得看的文件：

- `README.md`
- `ARCHITECTURE.md`
- `BROWSER.md`
- `CONTRIBUTING.md`
- `SKILL.md`

如果你想理解它的内部机制，建议优先从这些文档开始。

## 12. 初学者最容易踩的坑

### 12.1 一开始就想把所有技能都学会

这会让你感觉复杂。正确方式是先掌握：

- `/office-hours`
- `/plan-eng-review`
- `/review`
- `/qa`

### 12.2 把 gstack 当成全自动驾驶

它能大幅提高流程质量，但不意味着你可以完全不判断结果。尤其是：

- 产品方向
- 风险取舍
- 最终是否上线

这些仍然需要你自己把关。

### 12.3 没有 staging 就硬跑 `/qa`

`/qa` 最适合可访问的测试环境。没有环境时，也可以先用 `/review` 和局部测试。

### 12.4 安装后没配好宿主文档

README 里明确要求 Claude/Codex 等宿主要知道这些技能的存在。否则可能出现“装了但代理看不见”的问题。

## 13. 一个最值得做的入门练习

找一个自己的小项目，按下面顺序跑一遍：

1. `/office-hours`
2. `/plan-eng-review`
3. 实现一个小功能
4. `/review`
5. `/qa`
6. `/ship`
7. `/retro`

如果这一轮你真的跑完了，你对 `gstack` 的理解会远超过只读 README。

## 14. 总结

`gstack` 的真正价值，不在于它有多少个命令，而在于它把 AI 编程从“随机问答”变成“有角色、有流程、有交付闭环”的工作方式。

对于独立开发者、技术创始人和高频使用 AI 的工程师来说，它提供的不是单点提效，而是一套更像现代软件工厂的做法：

- 先重新定义问题
- 再锁定方案
- 然后实现
- 再 review
- 再 QA
- 再 ship
- 最后复盘

如果你已经在用 Claude Code、Codex 或其他代理写代码，那么最值得做的不是再找一个更花哨的 prompt，而是试着把自己的开发节奏升级成这种有明确阶段的流程。

## 15. 参考链接

- 仓库主页: https://github.com/garrytan/gstack
- README: https://github.com/garrytan/gstack/blob/main/README.md
- Architecture: https://github.com/garrytan/gstack/blob/main/ARCHITECTURE.md
- Browser Reference: https://github.com/garrytan/gstack/blob/main/BROWSER.md
