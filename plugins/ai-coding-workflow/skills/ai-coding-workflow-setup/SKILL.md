---
name: ai-coding-workflow-setup
description: 检查、安装或修复 AI Coding Workflow 在 Codex 中需要的 Superpowers、OpenSpec、Plannotator、项目画像和 Hooks 配置。用户要求安装、初始化、配置、修复或检查该工作流时使用；普通开发任务不要主动安装外部组件。
---

# AI Coding Workflow Setup

为当前 Codex 环境和当前项目完成一次性初始化。预检永远只读；安装软件、插件或写入项目配置必须来自用户明确的 setup/install 请求，或在自动检测缺失后取得一次集中授权。

## 检测

1. 定位插件根目录和项目 Git 根目录。
2. 运行只读预检，不创建或修改文件：

   ```text
   node <plugin-root>/scripts/setup-check.mjs --root <project-root>
   ```

3. 如果 `ready` 为 true，只提醒用户确认插件 Hooks 已在 Codex UI 中受信任，然后结束。不得重复安装。
4. 如果存在缺失项，按照“一次性授权”判断是否可以继续；未获授权时汇总全部缺失项并询问一次，然后停止。

## 初始化

获得授权后，先初始化项目支持文件；该操作不得覆盖已有画像：

   ```text
   node <plugin-root>/scripts/workflow-runtime.mjs init-project --host codex --root <project-root>
   ```

初始化后按检查结果修复缺失项，最后再由收尾步骤写入最新状态。

## 一次性授权

- 用户显式调用 `$ai-coding-workflow-setup`，或明确要求“安装/配置工作流”，视为授权执行下面列出的标准安装和当前项目初始化；先用一条简短进度说明列出将发生的外部修改，不再追加流程确认。
- 若本 Skill 是被普通开发请求自动触发，只能先检测。把全部缺失项和将执行的命令汇总后询问一次；未获授权不得安装。
- 工具自身的系统权限、网络或 Hook 信任提示仍由用户处理，不能绕过。

## 修复缺失项

只处理检查结果中的缺失项：

- `superpowers-plugin`：Superpowers 的官方 Codex 安装入口是 Desktop 侧边栏的插件页，或 Codex CLI 交互界面的 `/plugins` 搜索。当前能力能调用官方插件管理器时直接打开对应入口；否则让用户只完成“搜索 Superpowers → Install Plugin”这一个 UI 动作。不得猜测 `codex plugin add` 等未被当前 CLI 支持的命令，也不得直接修改 `config.toml` 或插件缓存。
- `superpowers-enable`：在 Codex 插件页启用 Superpowers；不直接编辑用户配置。
- `openspec-cli`：要求 Node.js `20.19.0` 或更高。优先使用 PATH 中已有的 npm 执行 `npm install -g @fission-ai/openspec@latest`；npm 不可用时依次检查 pnpm、bun、Yarn 1，不根据项目 lockfile 猜包管理器，不修改 PATH 或 shell profile。
- `openspec-project-skills`：执行前扫描旧版 OpenSpec 命令目录、AGENTS/CLAUDE marker 和用户目录的 `opsx-*.md`。若发现残留，说明 `openspec init` 会清理哪些文件并取得确认；没有残留时在已确认的项目根目录执行 `openspec init --tools codex`。已有 `openspec/` 目录不是错误，不手工创建 `.agents/skills/openspec-*`。
- `plannotator-cli`：仅在用户已授权安装时使用官方安装器。Windows PowerShell 执行 `irm https://plannotator.ai/install.ps1 | iex`；macOS/Linux/WSL 执行 `curl -fsSL https://plannotator.ai/install.sh | bash`。这是下载并执行远程安装器，必须使用宿主的权限确认，且不得把下载失败当作安装成功。
- `node` 或 `node-version`：停止自动安装，说明 Node.js `20.19.0` 是 OpenSpec runtime 前置条件，并报告当前版本或缺失证据。

Plannotator 只要 CLI 可用即可满足本工作流；`$plannotator-review` Skill 可用时优先调用，否则主工作流使用 `plannotator review --git`，不重复安装。

## 收尾

1. 重新运行 `setup-check.mjs --write-profile --require-ready`。
2. 若命令返回 ready，报告已完成项和项目画像路径。
3. Superpowers 或其他新 Skill 安装后，要求用户开启一个新任务再运行 `$ai-coding-workflow`；不要在旧任务中声称新 Skill 已加载。
4. Hooks 信任必须由用户在 Codex UI 审查；未信任时 Skill 仍可运行，但自动恢复、Stop 续跑和 strict 写入保护不会完整生效。
