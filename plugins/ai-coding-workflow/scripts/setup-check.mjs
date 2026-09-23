#!/usr/bin/env node

/**
 * Codex 工作流依赖检查器。
 *
 * 默认只读取命令、Skill、插件缓存与启用配置；传入 --write-profile 时，
 * 仅更新项目画像中的 setup 状态块，不安装任何软件。
 */

import { spawnSync } from "node:child_process";
import {
  existsSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";

function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const item = argv[index];
    if (!item.startsWith("--")) continue;
    const key = item.slice(2).replaceAll("-", "_");
    const next = argv[index + 1];
    if (next === undefined || next.startsWith("--")) result[key] = true;
    else {
      result[key] = next;
      index += 1;
    }
  }
  return result;
}

function commandAvailable(name) {
  const command = process.platform === "win32" ? "where.exe" : "sh";
  const args = process.platform === "win32" ? [name] : ["-lc", `command -v ${name}`];
  const result = spawnSync(command, args, { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
  return result.status === 0 && Boolean(result.stdout.trim());
}

function commandOutput(name, args = []) {
  const result = spawnSync(name, args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
  });
  return result.status === 0 ? result.stdout.trim() : "";
}

function versionAtLeast(version, minimum) {
  const current = String(version ?? "").match(/(\d+)\.(\d+)\.(\d+)/);
  const required = String(minimum).match(/(\d+)\.(\d+)\.(\d+)/);
  if (!current || !required) return false;
  for (let index = 1; index <= 3; index += 1) {
    const delta = Number(current[index]) - Number(required[index]);
    if (delta !== 0) return delta > 0;
  }
  return true;
}

function walk(directory, predicate, depth = 0) {
  if (!existsSync(directory) || depth > 8) return false;
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (predicate(path, entry)) return true;
    if (entry.isDirectory() && walk(path, predicate, depth + 1)) return true;
  }
  return false;
}

function skillAvailable(name, roots) {
  return roots.some((root) => {
    if (existsSync(join(root, name, "SKILL.md"))) return true;
    return walk(root, (path, entry) => entry.isFile() && entry.name === "SKILL.md"
      && path.replaceAll("\\", "/").includes(`/${name}/SKILL.md`));
  });
}

function pluginEnabled(configPath, pluginName) {
  if (!existsSync(configPath)) return false;
  const content = readFileSync(configPath, "utf8");
  const escaped = pluginName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const header = new RegExp(`^\\[plugins\\."${escaped}@[^"]+"\\]\\s*$`, "m").exec(content);
  if (!header) return false;
  const remainder = content.slice((header.index ?? 0) + header[0].length);
  const nextSection = remainder.search(/^\s*\[/m);
  const section = nextSection >= 0 ? remainder.slice(0, nextSection) : remainder;
  return /^\s*enabled\s*=\s*true\s*$/m.test(section);
}

function setProfileSetup(profilePath, status) {
  if (!existsSync(profilePath)) throw new Error(`项目画像不存在: ${profilePath}`);
  const start = "# ai-coding-workflow-setup:start";
  const end = "# ai-coding-workflow-setup:end";
  const block = [
    start,
    "setup:",
    `  status: "${status.ready ? "ready" : "incomplete"}"`,
    `  checked_at: "${status.checked_at}"`,
    `  node: ${status.node.available}`,
    `  node_version: "${status.node.version}"`,
    `  node_supported: ${status.node.supported}`,
    `  superpowers_plugin: ${status.superpowers.ready}`,
    `  openspec_cli: ${status.openspec.cli_available}`,
    `  openspec_skills: ${status.openspec.skills_available}`,
    `  plannotator_cli: ${status.plannotator.cli_available}`,
    "  hooks_trust: \"manual\"",
    end,
  ].join("\n");
  const original = readFileSync(profilePath, "utf8");
  const pattern = new RegExp(`${start}[\\s\\S]*?${end}\\n?`, "m");
  const base = original.replace(pattern, "").trimEnd();
  writeFileSync(profilePath, `${base}\n\n${block}\n`, "utf8");
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  const root = resolve(options.root ?? process.cwd());
  const userHome = homedir();
  const codexHome = resolve(process.env.CODEX_HOME ?? join(userHome, ".codex"));
  const skillRoots = [
    join(userHome, ".agents", "skills"),
    join(codexHome, "skills"),
    join(codexHome, "plugins", "cache"),
    join(root, ".agents", "skills"),
  ];
  const probe = options.probe_json ? JSON.parse(String(options.probe_json)) : {};
  const configPath = join(codexHome, "config.toml");
  const pluginCache = join(codexHome, "plugins", "cache");
  const superpowersInstalled = probe.superpowers_installed ?? walk(
    pluginCache,
    (path, entry) => entry.isFile() && entry.name === "SKILL.md"
      && path.replaceAll("\\", "/").includes("/superpowers/")
      && path.replaceAll("\\", "/").includes("/using-superpowers/"),
  );
  const superpowersEnabled = probe.superpowers_enabled ?? pluginEnabled(configPath, "superpowers");
  const openspecSkills = ["openspec-propose", "openspec-apply-change"].every((name) =>
    existsSync(join(root, ".agents", "skills", name, "SKILL.md"))
  );
  const nodeAvailable = probe.node ?? commandAvailable("node");
  const nodeVersion = probe.node_version
    ?? (probe.node === true ? "20.19.0" : (nodeAvailable ? commandOutput("node", ["--version"]) : ""));
  const status = {
    checked_at: new Date().toISOString(),
    project_root: root,
    node: {
      available: nodeAvailable,
      version: nodeVersion,
      minimum_version: "20.19.0",
      supported: nodeAvailable && versionAtLeast(nodeVersion, "20.19.0"),
    },
    superpowers: {
      installed: superpowersInstalled,
      enabled: superpowersEnabled,
      ready: superpowersInstalled && superpowersEnabled,
    },
    openspec: {
      cli_available: probe.openspec_cli ?? commandAvailable("openspec"),
      skills_available: openspecSkills,
      skills_path: join(root, ".agents", "skills").replaceAll("\\", "/"),
    },
    plannotator: {
      cli_available: probe.plannotator_cli ?? commandAvailable("plannotator"),
      skill_available: skillAvailable("plannotator-review", skillRoots),
    },
    hooks: {
      trust: "manual",
    },
  };
  status.ready = status.node.supported
    && status.superpowers.ready
    && status.openspec.cli_available
    && status.openspec.skills_available
    && status.plannotator.cli_available;
  status.missing = [];
  if (!status.node.available) status.missing.push("node");
  else if (!status.node.supported) status.missing.push("node-version");
  if (!status.superpowers.installed) status.missing.push("superpowers-plugin");
  else if (!status.superpowers.enabled) status.missing.push("superpowers-enable");
  if (!status.openspec.cli_available) status.missing.push("openspec-cli");
  if (!status.openspec.skills_available) status.missing.push("openspec-project-skills");
  if (!status.plannotator.cli_available) status.missing.push("plannotator-cli");

  if (options.write_profile) {
    const profilePath = resolve(
      options.profile ?? join(root, ".codex", "ai-coding-workflow", "project-profile.yaml"),
    );
    setProfileSetup(profilePath, status);
    status.profile_updated = profilePath.replaceAll("\\", "/");
  }
  process.stdout.write(`${JSON.stringify(status, null, 2)}\n`);
  if (options.require_ready && !status.ready) process.exitCode = 1;
}

try {
  main();
} catch (error) {
  process.stderr.write(`[setup-check] ${error.message}\n`);
  process.exitCode = 1;
}
