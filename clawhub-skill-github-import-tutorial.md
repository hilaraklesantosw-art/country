# ClawHub 技能创建与通过 GitHub 快速导入上架教程

## 1. 这篇教程解决什么问题

如果你想把自己的技能发布到 `ClawHub`，并且希望尽量少走手工上传流程，最适合你的路径是：

- 先把技能做成一个标准 `SKILL.md` 技能包
- 放到公开 GitHub 仓库
- 再通过 `ClawHub` 的 **Import from GitHub** 页面直接导入并发布

这条路径的优点很明显：

- 技能源码放在自己的 GitHub 上，便于维护
- ClawHub 可以直接识别 `SKILL.md`
- 导入时会自动探测技能目录、预选文件、生成 slug 和版本
- 发布后的版本会保留 GitHub 来源信息和 commit 溯源

## 2. 我确认到的 ClawHub 关键规则

基于 `openclaw/clawhub` 仓库当前文档和代码，做技能和 GitHub 导入时你需要先知道这些硬约束：

- 技能本质上是一个**文件夹**
- 文件夹里**必须有** `SKILL.md`，也兼容 `skill.md`
- 发布内容只接受**文本类文件**
- 单次发布总大小上限是 **50MB**
- `slug` 必须是小写、URL 安全格式：`^[a-z0-9][a-z0-9-]*$`
- 发布到 ClawHub 的技能采用 **MIT-0**
- 发布、CLI publish、GitHub import 都要求你的 **GitHub 账号年龄至少 14 天**
- GitHub 导入当前只支持**公开仓库**
- GitHub 导入支持三类 URL：
  - 仓库根目录
  - `tree/<ref>/<path>`
  - `blob/<ref>/<path>`

这意味着，如果你现在想“通过 GitHub 导入快速上架”，你的仓库最好一开始就按 ClawHub 规则组织好。

## 3. 最小可用技能长什么样

最小可用结构如下：

```text
my-skill/
├── SKILL.md
└── usage.md
```

其中 `SKILL.md` 是必须的。

一个最小可发布示例如下：

```md
---
name: github-repo-inspector
description: Analyze a GitHub repository and summarize project structure, risks, and key files.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - git
        - rg
    homepage: https://github.com/yourname/your-skill-repo
---

# GitHub Repo Inspector

Use this skill when the user wants to inspect a repository, identify important modules,
or quickly understand codebase structure.

## Workflow

1. Read the repository tree and key manifests first.
2. Search with `rg` before opening many files.
3. Summarize architecture before making changes.

## Output

- Key directories
- Important entry points
- Risks and missing tests

See [usage.md](usage.md) for examples.
```

这个结构足够让 ClawHub 识别并导入。

## 4. 推荐的技能仓库结构

如果你想后续持续维护，我建议用下面这种结构：

```text
your-skill-repo/
├── SKILL.md
├── references/
│   ├── api.md
│   └── examples.md
├── scripts/
│   └── helper.sh
└── assets/
    └── template.txt
```

但要注意：

- ClawHub 发布的是**文本型技能包**
- 技能说明核心应该写在 `SKILL.md`
- 大块参考文档放到 `references/`
- 需要稳定执行的步骤可放到 `scripts/`
- 不要把仓库做得过重

对“快速上架”来说，**最重要的是 SKILL.md 清晰、依赖声明准确、目录干净**。

## 5. `SKILL.md` 应该怎么写

ClawHub 会从 `SKILL.md` 顶部 YAML frontmatter 里提取元数据。最常用字段如下：

```yaml
---
name: my-skill
description: Short summary of what this skill does.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - MY_API_KEY
      bins:
        - curl
    primaryEnv: MY_API_KEY
    homepage: https://github.com/yourname/your-repo
---
```

建议你至少写好这些字段：

- `name`
- `description`
- `version`
- `metadata.openclaw.requires.env`
- `metadata.openclaw.requires.bins`
- `metadata.openclaw.primaryEnv`
- `metadata.openclaw.homepage`

为什么这些字段重要：

- `description` 会直接影响 ClawHub UI 和搜索摘要
- `requires.env`、`requires.bins` 会参与安全分析
- 你实际依赖什么，就要老实声明什么

如果你的技能里实际读取了 `OPENAI_API_KEY`，但 frontmatter 没写，ClawHub 的安全分析可能会把它标成元数据不一致。

## 6. 什么样的技能更适合一次导入成功

如果你的目标是“尽快上架”，建议遵守这几条：

- 技能文件夹里只放和技能直接相关的文本文件
- `SKILL.md` 不要过短，也不要只有一句空话
- 不要塞大量无关仓库文件
- 不要用混淆命令、base64 解码后执行 shell、`curl | bash` 这类高风险内容
- 依赖和权限声明保持真实
- 先从单技能仓库开始，不要一上来做超复杂多技能仓库

根据 ClawHub 当前安全文档，**可疑静态扫描结果会直接让技能隐藏，严重时还会把上传者拉入人工审核**。所以“快速上架”的本质不是走捷径，而是把技能包做干净。

## 7. 如何通过 GitHub 导入快速上架

这是最重要的部分。

### 第一步：准备公开 GitHub 仓库

你至少需要满足：

- 仓库是公开的
- 技能目录里有 `SKILL.md`
- GitHub 账号年龄不少于 14 天

推荐两种组织方式：

#### 方式 A：仓库根目录就是一个技能

```text
repo-root/
├── SKILL.md
├── usage.md
└── references/
```

这种最简单，导入成功率最高。

#### 方式 B：一个仓库里放多个技能

```text
repo-root/
├── skills/
│   ├── skill-a/
│   │   └── SKILL.md
│   └── skill-b/
│       └── SKILL.md
```

这种也支持，但导入时 ClawHub 会先探测多个候选目录，让你手动选一个。

### 第二步：把技能推到 GitHub

例如：

```bash
git init
git add .
git commit -m "init clawhub skill"
git branch -M main
git remote add origin https://github.com/yourname/your-skill-repo.git
git push -u origin main
```

### 第三步：打开 ClawHub 的 GitHub 导入页面

当前 ClawHub 前端已经有独立导入路由：

- `/import`

也就是你通常会走：

- `https://clawhub.ai/import`

进入后页面会提示：

- 只支持 **Public repos only**
- 自动检测 `SKILL.md`

### 第四步：粘贴 GitHub URL

ClawHub 目前接受这三类 URL：

1. 仓库根目录

```text
https://github.com/owner/repo
```

2. 某个目录

```text
https://github.com/owner/repo/tree/main/skills/my-skill
```

3. 某个 `SKILL.md` 文件

```text
https://github.com/owner/repo/blob/main/skills/my-skill/SKILL.md
```

如果你就是想快速上架，我建议直接贴：

- 技能目录 URL
- 或者直接贴 `SKILL.md` 的 blob URL

这样定位最准确。

### 第五步：让 ClawHub 自动探测技能

导入流程会先做两件事：

- 下载 GitHub 公开仓库归档
- 自动扫描其中包含 `SKILL.md` 的目录

如果扫描到多个技能目录，页面会让你选候选技能。

### 第六步：检查它自动生成的默认值

ClawHub 当前导入逻辑会自动帮你生成：

- `slug`
- `displayName`
- `version`
- `tags`
- 默认勾选的文件列表

默认行为大致是：

- 新技能默认版本建议为 `0.1.0`
- 默认标签是 `latest`
- 会尽量只选技能目录内的文本文件
- `SKILL.md` 必须被选中，否则不能导入

这里你需要重点检查三件事：

- `slug` 是否符合你的长期命名
- `displayName` 是否适合公开展示
- 是否把无关文件也勾上了

### 第七步：确认文件选择

ClawHub 的 GitHub import 支持预览文件并选择是否导入。

推荐你只保留：

- `SKILL.md`
- 直接引用到的 `references/*.md`
- 必要的 `scripts/*.sh` / `*.py` / `*.js`
- 少量必要配置文件

尽量不要把这些带上：

- 大量测试数据
- 无关 README
- 构建产物
- 二进制内容
- 仓库里其他无关模块

因为导入规则是文本型为主，而且总大小有 **50MB** 限制。

### 第八步：点击导入发布

导入动作最终会走发布流程，并把 GitHub 来源信息写入版本元数据，包括：

- GitHub URL
- repo
- ref
- commit
- path
- importedAt

这意味着：

- 你的 ClawHub 技能版本可以追溯到具体 GitHub commit
- 以后做版本审计、回滚、对照会更清楚

## 8. 最适合“快速上架”的仓库组织方式

如果你的核心诉求是：**通过 GitHub 导入，最短时间上架一个技能**，我建议你不要一开始就做复杂仓库，而是用下面这套最稳结构：

```text
my-clawhub-skill/
├── SKILL.md
├── usage.md
└── references/
    └── examples.md
```

对应做法：

1. 一个仓库只放一个技能
2. `SKILL.md` 放仓库根目录
3. 只带少量 markdown 参考文件
4. 先导入一个 `0.1.0`
5. 上架后再慢慢迭代

这是成功率最高的路线。

## 9. 如果你想持续用 GitHub 维护，推荐这样迭代

建议你把 GitHub 当作源仓库，把 ClawHub 当作分发入口。

最稳妥的迭代方式是：

1. 先在 GitHub 修改技能内容
2. 提交 commit
3. 再到 ClawHub 通过 GitHub import 导入新版本
4. 版本号按 semver 递增

例如：

- `0.1.0`：首次上架
- `0.1.1`：修正文案或引用文件
- `0.2.0`：增加工作流或脚本
- `1.0.0`：结构稳定后正式版

需要特别说明的一点：

- ClawHub 当前有 GitHub import
- 但官方产品 spec 里仍把更深层的 GitHub App repo sync 视为未来阶段，不应假设“推 GitHub 后会自动同步上架”

所以你现在应该按**手动触发导入发布**来设计流程，而不是指望自动镜像。

## 10. 通过 CLI 发布和通过 GitHub 导入，应该选哪个

两种都能上架，但适用场景不同。

### 选 GitHub 导入

适合你现在这个目标：

- 你想以 GitHub 为主仓
- 你想通过网页快速上架
- 你希望保留 commit 来源
- 你不想先配一套本地 CLI 发布流程

### 选 CLI publish / sync

适合你后续规模化维护：

- 本地已经有一批技能目录
- 想批量同步
- 想自动 bump 版本
- 想走更工程化的发布流程

所以对你当前需求，我的建议很直接：

- **先用 GitHub import 上第一个版本**
- **后续如果技能多了，再切 CLI sync**

## 11. 一个适合快速上架的实操流程

你可以直接照这个流程走：

1. 新建一个公开 GitHub 仓库
2. 在仓库根目录写 `SKILL.md`
3. 再补一个 `usage.md`
4. 在 `SKILL.md` 里写清楚 `name`、`description`、`version`、`metadata.openclaw`
5. push 到 GitHub
6. 打开 `https://clawhub.ai/import`
7. 粘贴仓库 URL 或 `SKILL.md` URL
8. 选择检测出的技能目录
9. 检查 `slug`、`displayName`、`version`
10. 删除无关文件，只保留必要文本文件
11. 导入发布

## 12. 常见失败原因

如果导入失败，优先检查这些：

- GitHub 仓库不是公开的
- 仓库里没有 `SKILL.md`
- `slug` 不符合格式
- 版本号不是合法 semver
- 选中的文件超过 50MB
- 选中的内容不是文本类文件
- GitHub 账号年龄不足 14 天
- `SKILL.md` 很空，或内容与声明依赖严重不一致
- 技能里有高风险脚本或可疑命令

## 13. 我的建议

如果你是第一次做 ClawHub 技能，并且明确希望通过 GitHub 快速上架，我建议你这样做：

- 不要先做“大而全”的技能仓库
- 先做一个单技能、单目录、根目录 `SKILL.md` 的公开仓库
- 先发布 `0.1.0`
- 确认导入链路跑通后，再增加引用文件、脚本和更复杂的 metadata

这条路线最省时间，也最符合 ClawHub 当前产品能力边界。

## 14. 参考依据

这篇教程基于 `openclaw/clawhub` 当前公开仓库中的文档与实现整理，重点参考了以下内容：

- `README.md`
- `docs/quickstart.md`
- `docs/cli.md`
- `docs/skill-format.md`
- `docs/security.md`
- `docs/spec.md`
- `docs/github-import.md`
- `src/routes/import.tsx`
- `convex/githubImport.ts`

其中最关键的事实包括：

- ClawHub 已经有 `/import` 路由和对应后端 action
- GitHub import 现在支持公开仓库 URL 导入
- 导入时会固定到具体 commit
- 发布规则受文本文件、50MB、GitHub 账号年龄、MIT-0 等约束
