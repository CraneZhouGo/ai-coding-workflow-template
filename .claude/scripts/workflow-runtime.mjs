#!/usr/bin/env node

/**
 * AI Coding Workflow V3.3 确定性控制器。
 *
 * AI 负责提取事实和执行开发工作；本脚本只负责确定性路由、节点编排、
 * 状态迁移、评审范围校验，以及 Claude Code 生命周期 Hook。
 */

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";

const WORKFLOW_VERSION = "3.3.0";
const GOVERNED_FACTS = [
  "critical_semantics_changed",
  "incompatible_public_contract",
  "coordinated_release",
  "schema_migration",
  "data_backfill",
  "global_security_or_infrastructure",
  "no_credible_rollback",
  "cross_repo_release_ordering",
  "unbounded_impact",
  "critical_validation_unavailable",
  "requested_governed",
];
const FAST_FACTS = [
  "clear_acceptance",
  "localized_change",
  "consumers_known",
  "no_boundary_change",
  "easy_rollback",
  "direct_validation",
  "no_design_tradeoff",
];
const GATES = ["data", "security", "contract", "infrastructure", "release", "observability"];
const REROUTE_CHECKPOINTS = [
  "post-exploration",
  "root-cause-known",
  "boundary-discovered",
  "diff-expanded",
  "pre-delivery",
];
const REROUTE_PREREQUISITES = {
  "post-exploration": "C2",
  "root-cause-known": "M-BU2",
  "boundary-discovered": "C4",
  "diff-expanded": "C5",
  "pre-delivery": "C6",
};
const TERMINAL_NODE_STATUSES = new Set(["done", "N/A"]);

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
}

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

function digest(value) {
  const content = typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value);
  return createHash("sha256").update(content).digest("hex");
}

function parseArgs(argv) {
  const result = { _: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (!value.startsWith("--")) {
      result._.push(value);
      continue;
    }
    const key = value.slice(2).replaceAll("-", "_");
    const next = argv[index + 1];
    if (next === undefined || next.startsWith("--")) result[key] = true;
    else {
      result[key] = next;
      index += 1;
    }
  }
  return result;
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function readInput(options) {
  if (options.input) return readJson(resolve(options.input));
  if (options.json) return JSON.parse(options.json);
  if (!process.stdin.isTTY) {
    const content = readFileSync(0, "utf8").trim();
    if (content) return JSON.parse(content);
  }
  throw new Error("需要通过 --input、--json 或 stdin 提供 JSON 输入");
}

function writeJsonAtomic(path, value) {
  const target = resolve(path);
  mkdirSync(dirname(target), { recursive: true });
  const temporary = `${target}.tmp-${process.pid}`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  renameSync(temporary, target);
}

function bool(facts, name) {
  return facts[name] === true;
}

function classifyIntent(facts) {
  if (bool(facts, "requested_change")) return "change";
  if (bool(facts, "requested_plan")) return "plan-only";
  if (bool(facts, "requested_diagnosis")) return "diagnose-only";
  if (bool(facts, "requested_review")) return "review";
  return "explain";
}

function classifyTaskType(facts) {
  if (bool(facts, "migration_or_infrastructure")) return "migration-infrastructure";
  if (bool(facts, "bug_or_failure")) return "bug";
  if (bool(facts, "refactor_only")) return "refactor";
  if (bool(facts, "upgrade_or_configuration")) return "upgrade-config";
  if (bool(facts, "maintenance_only")) return "maintenance";
  if (bool(facts, "feature_or_behavior") || bool(facts, "requested_change")) return "feature";
  return null;
}

function classifyMode(facts, intent, taskType, profileReady = true) {
  if (intent !== "change") return null;
  if (GOVERNED_FACTS.some((name) => bool(facts, name))) return "governed";
  const fastEligible = FAST_FACTS.every((name) => bool(facts, name));
  // Superpowers brainstorming 要求设计批准，因此 Feature 最低为 Standard。
  if (profileReady && taskType !== "feature" && fastEligible && !bool(facts, "requested_standard")) {
    return "fast";
  }
  return "standard";
}

function classifyGates(facts) {
  return GATES.filter((gate) => bool(facts, `${gate}_gate`));
}

function executionPolicy(mode, taskType) {
  if (mode === "fast") {
    return {
      planning_depth: "concise",
      validation_scope: "targeted",
      isolation: "current-worktree",
      review_policy: "none",
      execution_strategy: "sequential",
    };
  }
  if (mode === "governed") {
    return {
      planning_depth: "extensive",
      validation_scope: "full",
      isolation: "mandatory-worktree",
      review_policy: "spec-and-code-diff",
      execution_strategy: taskType === "migration-infrastructure" ? "staged" : "dependency-parallel",
    };
  }
  return {
    planning_depth: taskType === "refactor" ? "extensive" : "normal",
    validation_scope: "affected",
    isolation: "isolate-if-dirty",
    review_policy: "spec-diff",
    execution_strategy: "sequential",
  };
}

function routeDecision(input) {
  const facts = input.facts ?? input;
  // Fail closed：只有项目画像明确完成后才允许 Fast，避免缺少配置时误判为低风险。
  const profileReady = input.profile_ready === true;
  const intent = classifyIntent(facts);
  const taskType = classifyTaskType(facts);
  const mode = classifyMode(facts, intent, taskType, profileReady);
  const route = {
    intent,
    task_type: taskType,
    mode,
    specialized_gates: classifyGates(facts),
    execution_policy: mode ? executionPolicy(mode, taskType) : null,
  };
  return {
    workflow_version: WORKFLOW_VERSION,
    route_facts: facts,
    route,
    route_fingerprint: digest({ workflow_version: WORKFLOW_VERSION, facts, profileReady, route }),
  };
}

function node(id, phase, source, prerequisites = [], humanGate = false) {
  return {
    id,
    phase,
    source,
    required: true,
    human_gate: humanGate,
    prerequisites,
    status: "pending",
    evidence: [],
  };
}

const METHODS = {
  feature: {
    planning: ["M-FE1", "M-FE2"],
    implementation: ["M-FE3"],
    verification: [],
  },
  bug: {
    planning: ["M-BU1", "M-BU2"],
    implementation: ["M-BU3", "M-BU4"],
    verification: [],
  },
  refactor: {
    planning: ["M-RE1", "M-RE2"],
    implementation: ["M-RE3", "M-RE4"],
    verification: [],
  },
  "upgrade-config": {
    planning: ["M-UP1", "M-UP2", "M-UP3"],
    implementation: ["M-UP4"],
    verification: [],
  },
  "migration-infrastructure": {
    planning: ["M-MI1"],
    implementation: ["M-MI2", "M-MI3", "M-MI4"],
    verification: [],
  },
  maintenance: {
    planning: ["M-MA1"],
    implementation: ["M-MA2"],
    verification: ["M-MA3"],
  },
};

function composeNodes(route) {
  if (route.intent !== "change") return [];
  const method = METHODS[route.task_type];
  if (!method) throw new Error(`不支持的 task_type: ${route.task_type}`);
  const specs = [];
  const push = (id, phase, source, humanGate = false) => {
    const previous = specs.at(-1)?.id;
    specs.push(node(id, phase, source, previous ? [previous] : [], humanGate));
  };

  push("C1", "planning", "core");
  push("C2", "planning", "core");
  if (route.mode === "standard") push("S-WS0", "planning", "mode");
  if (route.mode === "governed") push("G-WS0", "planning", "mode");
  push("C3", "planning", "core");
  push("C4", "planning", "core");
  if (route.mode === "governed") {
    push("G-EX1", "planning", "mode");
    push("G-IA1", "planning", "mode");
  }
  for (const id of method.planning) push(id, "planning", "method");

  if (route.mode !== "fast") {
    push("S-OS1", "planning", "mode");
    for (const gate of route.specialized_gates) push(`X-${gate.toUpperCase()}-P`, "planning", "gate");
    push(route.mode === "governed" ? "G-PL1" : "S-PL1", "planning", "mode");
    push("S-DF1", "planning", "mode");
    push("S-HG1", "human_gate", "mode", true);
  }

  push("C5", "implementation", "core");
  if (route.mode === "standard") push("S-IM1", "implementation", "mode");
  if (route.mode === "governed") push("G-IM1", "implementation", "mode");
  for (const id of method.implementation) push(id, "implementation", "method");
  push("C6", "verification", "core");
  for (const id of method.verification) push(id, "verification", "method");
  for (const gate of route.specialized_gates) push(`X-${gate.toUpperCase()}-V`, "verification", "gate");
  if (route.mode === "standard") push("S-RV1", "verification", "mode");
  if (route.mode === "governed") {
    push("G-RV1", "verification", "mode");
    push("G-HG1", "human_gate", "mode", true);
  }
  if (route.mode !== "fast") push("S-FI1", "completion", "mode");
  push("C7", "completion", "core");
  return specs;
}

function stateRoute(route, initialMode = route.mode) {
  return {
    intent: route.intent,
    task_type: route.task_type,
    initial_mode: initialMode,
    current_mode: route.mode,
    specialized_gates: route.specialized_gates,
    execution_policy: route.execution_policy,
  };
}

function nodeIdentities(nodes) {
  return nodes.map(({ id, phase, source, required, human_gate, prerequisites }) => ({
    id,
    phase,
    source,
    required,
    human_gate,
    prerequisites,
  }));
}

function workflowHash(route, nodes) {
  return digest({ route, nodes: nodeIdentities(nodes) });
}

function initializeState(input) {
  const decision = routeDecision(input);
  if (decision.route.intent !== "change") throw new Error("只有 change 意图创建 workflow-state");
  if (!input.change_id) throw new Error("init-state 需要 change_id");
  const nodes = composeNodes(decision.route);
  const completed = input.completed_nodes ?? {};
  let prefixOpen = true;
  for (const item of nodes) {
    if (Object.hasOwn(completed, item.id)) {
      if (!prefixOpen) throw new Error("completed_nodes 必须是 ordered_nodes 的连续前缀");
      if (item.human_gate || ["S-DF1", "S-FI1", "C7"].includes(item.id)) {
        throw new Error(`${item.id} 不能通过 completed_nodes 导入，必须执行专用校验命令`);
      }
      const evidence = String(completed[item.id] ?? "").trim();
      if (!evidence) throw new Error(`${item.id} 缺少完成证据`);
      item.status = "done";
      item.evidence = [evidence];
    } else prefixOpen = false;
  }
  const route = decision.route;
  const persistedRoute = stateRoute(route);
  const state = {
    schema_version: 2,
    workflow_version: WORKFLOW_VERSION,
    change_id: input.change_id,
    requirement: input.requirement ?? "",
    requirement_fingerprint: digest(input.requirement ?? ""),
    profile_ready: input.profile_ready === true,
    route_fingerprint: decision.route_fingerprint,
    workflow_hash: workflowHash(persistedRoute, nodes),
    route_facts: decision.route_facts,
    route: persistedRoute,
    current_node: nodes.find((item) => item.status === "pending")?.id ?? null,
    status: "active",
    review_base: null,
    spec_review: route.mode === "fast" ? { status: "N/A" } : { status: "pending", diff_type: "uncommitted", expected_paths: [], displayed_paths: [], artifact_hashes: [] },
    code_review: route.mode === "governed" ? { status: "pending", diff_type: "since-base" } : { status: "N/A" },
    archive_status: route.mode === "fast" ? "N/A" : "pending",
    nodes,
    reroutes: [],
    blocked_reason: null,
    compaction_count: 0,
    updated_at: new Date().toISOString(),
  };
  return state;
}

function validateState(state) {
  const errors = [];
  if (state.schema_version !== 2) errors.push("schema_version 必须为 2");
  if (state.workflow_version !== WORKFLOW_VERSION) errors.push(`workflow_version 必须为 ${WORKFLOW_VERSION}`);
  if (!state.change_id) errors.push("缺少 change_id");
  if (typeof state.profile_ready !== "boolean") errors.push("profile_ready 必须是 boolean");
  if (state.requirement_fingerprint !== digest(state.requirement ?? "")) errors.push("requirement_fingerprint 与 requirement 不一致");
  if (!Array.isArray(state.nodes) || state.nodes.length === 0) errors.push("nodes 必须是非空数组");
  const ids = new Set();
  for (const item of state.nodes ?? []) {
    if (ids.has(item.id)) errors.push(`重复节点: ${item.id}`);
    ids.add(item.id);
    if (!Array.isArray(item.evidence)) errors.push(`${item.id}.evidence 必须是数组`);
    if (!["pending", "in_progress", "done", "N/A", "blocked"].includes(item.status)) errors.push(`${item.id} 状态非法`);
    if (["done", "N/A", "blocked"].includes(item.status) && item.evidence.length === 0) errors.push(`${item.id} 缺少 evidence`);
    for (const prerequisite of item.prerequisites ?? []) {
      if (!ids.has(prerequisite)) errors.push(`${item.id} 的前置节点 ${prerequisite} 不在它之前`);
    }
  }
  if (state.current_node !== null && !ids.has(state.current_node)) errors.push("current_node 不存在于 nodes");
  const expectedCurrent = state.nodes?.find((item) => !TERMINAL_NODE_STATUSES.has(item.status))?.id ?? null;
  if (state.status !== "completed" && state.current_node !== expectedCurrent) errors.push(`current_node 应为 ${expectedCurrent}`);
  if (state.status === "completed" && expectedCurrent !== null) errors.push("completed 状态仍有未完成节点");
  if (state.route_facts && state.route) {
    const decision = routeDecision({ facts: state.route_facts, profile_ready: state.profile_ready });
    if (state.route_fingerprint !== decision.route_fingerprint) errors.push("route_fingerprint 与 route_facts 不一致");
    if (state.route.intent !== decision.route.intent || state.route.task_type !== decision.route.task_type) errors.push("intent/task_type 与确定性路由结果不一致");
    if (state.route.current_mode !== decision.route.mode) errors.push("current_mode 与确定性路由结果不一致");
    if (canonical(state.route.specialized_gates) !== canonical(decision.route.specialized_gates)) errors.push("specialized_gates 与确定性路由结果不一致");
    if (canonical(state.route.execution_policy) !== canonical(decision.route.execution_policy)) errors.push("execution_policy 与确定性路由结果不一致");
    if (decision.route.intent === "change" && canonical(nodeIdentities(state.nodes ?? [])) !== canonical(nodeIdentities(composeNodes(decision.route)))) {
      errors.push("ordered nodes 与确定性组合结果不一致");
    }
    if (state.workflow_hash !== workflowHash(state.route, state.nodes ?? [])) errors.push("workflow_hash 与当前有序节点不一致");
  }
  return errors;
}

function loadState(path) {
  const state = readJson(resolve(path));
  const errors = validateState(state);
  if (errors.length) throw new Error(`workflow-state 无效:\n- ${errors.join("\n- ")}`);
  return state;
}

function saveState(path, state) {
  state.updated_at = new Date().toISOString();
  const errors = validateState(state);
  if (errors.length) throw new Error(`拒绝写入无效状态:\n- ${errors.join("\n- ")}`);
  writeJsonAtomic(path, state);
}

function currentNode(state) {
  return state.nodes.find((item) => item.id === state.current_node) ?? null;
}

function advance(state) {
  const next = state.nodes.find((item) => !TERMINAL_NODE_STATUSES.has(item.status));
  state.current_node = next?.id ?? null;
  state.status = next?.status === "blocked" ? "blocked" : next ? "active" : "completed";
  state.blocked_reason = next?.status === "blocked" ? next.evidence.at(-1) : null;
}

function resetStaleSpecReview(state, statePath, root) {
  if (state.route.current_mode === "fast" || state.spec_review.status !== "approved") return false;
  const changed = state.spec_review.artifact_hashes.some(({ path, sha256 }) => {
    const artifact = join(root, path);
    return !existsSync(artifact) || digest(readFileSync(artifact)) !== sha256;
  });
  if (!changed) return false;
  state.spec_review.status = "stale";
  state.spec_review.displayed_paths = [];
  for (const id of ["S-DF1", "S-HG1"]) {
    const reviewNode = state.nodes.find((candidate) => candidate.id === id);
    if (reviewNode) {
      reviewNode.status = "pending";
      reviewNode.evidence = [];
    }
  }
  advance(state);
  saveState(statePath, state);
  return true;
}

function transition(statePath, options, root) {
  const state = loadState(statePath);
  const item = currentNode(state);
  if (!item) throw new Error("没有可执行节点");
  if (options.node && options.node !== item.id) throw new Error(`只能操作 current_node ${item.id}`);
  const target = options.to;
  const allowed = {
    pending: new Set(["in_progress", "N/A"]),
    in_progress: new Set(["done", "blocked", "N/A"]),
    blocked: new Set(["in_progress"]),
  };
  if (!allowed[item.status]?.has(target)) throw new Error(`非法状态转换: ${item.status} -> ${target}`);
  const evidence = String(options.evidence ?? "").trim();
  if (["done", "blocked", "N/A"].includes(target) && !evidence) throw new Error(`${target} 必须提供 --evidence`);
  if (item.human_gate && target === "done") throw new Error("人工 Gate 必须使用 review 命令完成");
  if (item.id === "C7" && state.route.current_mode !== "fast" && target === "done") throw new Error("Standard/Governed 必须使用 archive-complete 完成 C7");
  if (item.id === "C5" && target === "in_progress" && resetStaleSpecReview(state, statePath, root)) {
    throw new Error("规划工件哈希已变化；已将流程退回 S-DF1，必须重新执行 Spec Diff Review");
  }
  item.status = target;
  if (evidence) item.evidence.push(evidence);
  if (item.id === "S-FI1" && target === "done") state.archive_status = "ready";
  advance(state);
  saveState(statePath, state);
  return state;
}

function git(root, args) {
  return execFileSync("git", ["-c", `safe.directory=${root.replaceAll("\\", "/")}`, "-c", "core.excludesFile=", ...args], {
    cwd: root,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  }).trim();
}

function parsePorcelainZ(output) {
  const entries = output.split("\0").filter(Boolean);
  const paths = [];
  for (let index = 0; index < entries.length; index += 1) {
    const entry = entries[index];
    const status = entry.slice(0, 2);
    let path = entry.slice(3);
    if (status.includes("R") || status.includes("C")) {
      path = entries[index + 1] ?? path;
      index += 1;
    }
    paths.push(path.replaceAll("\\", "/"));
  }
  return [...new Set(paths)].sort();
}

function hashArtifacts(root, paths, stateRelative) {
  return paths
    .filter((path) => path !== stateRelative && existsSync(join(root, path)) && statSync(join(root, path)).isFile())
    .map((path) => ({ path, sha256: digest(readFileSync(join(root, path))) }));
}

function captureSpecDiff(statePath, root) {
  const state = loadState(statePath);
  const item = currentNode(state);
  if (item?.id !== "S-DF1") throw new Error("capture-spec-diff 只能在 S-DF1 执行");
  const changed = parsePorcelainZ(git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"]));
  const prefix = `openspec/changes/${state.change_id}/`;
  const unrelated = changed.filter((path) => !path.startsWith(prefix));
  if (unrelated.length) throw new Error(`Spec Diff 混入无关文件:\n- ${unrelated.join("\n- ")}`);
  if (changed.length === 0) throw new Error("没有可评审的 OpenSpec 文件变化");
  const stateRelative = relative(root, resolve(statePath)).split(sep).join("/");
  state.review_base = {
    head: git(root, ["rev-parse", "HEAD"]),
    branch: git(root, ["branch", "--show-current"]),
  };
  state.spec_review.expected_paths = changed;
  state.spec_review.displayed_paths = [];
  state.spec_review.artifact_hashes = hashArtifacts(root, changed, stateRelative);
  state.spec_review.status = "pending";
  item.status = "done";
  item.evidence.push(`已确认 ${changed.length} 个 uncommitted 文件全部属于 ${prefix}`);
  advance(state);
  saveState(statePath, state);
  return state;
}

function review(statePath, options) {
  const state = loadState(statePath);
  const type = options.type;
  const decision = options.decision;
  const item = currentNode(state);
  const expectedNode = type === "spec" ? "S-HG1" : type === "code" ? "G-HG1" : null;
  if (!expectedNode) throw new Error("--type 必须为 spec 或 code");
  if (item?.id !== expectedNode) throw new Error(`${type} review 只能在 ${expectedNode} 执行`);
  if (!item.human_gate) throw new Error(`${expectedNode} 不是人工 Gate`);
  if (!["approved", "rejected"].includes(decision)) throw new Error("--decision 必须为 approved 或 rejected");
  const reviewState = type === "spec" ? state.spec_review : state.code_review;
  const diffType = options.diff_type ?? reviewState.diff_type;
  if (type === "spec" && diffType !== "uncommitted") throw new Error("Spec Diff Review 必须使用 uncommitted 视图");
  if (type === "code" && diffType !== "since-base") throw new Error("Code Diff Review 必须使用 since-base 视图");
  if (type === "spec") {
    const displayed = String(options.displayed_paths ?? "").split(",").map((value) => value.trim().replaceAll("\\", "/")).filter(Boolean).sort();
    const expected = [...reviewState.expected_paths].sort();
    if (canonical(displayed) !== canonical(expected)) throw new Error("Plannotator 展示文件与 expected_paths 不一致");
    reviewState.displayed_paths = displayed;
  }
  reviewState.diff_type = diffType;
  reviewState.status = decision;
  reviewState.reviewed_at = new Date().toISOString();
  reviewState.evidence = String(options.evidence ?? decision);
  if (decision === "approved") {
    item.status = "done";
    item.evidence.push(reviewState.evidence);
    advance(state);
  } else {
    item.status = "in_progress";
    item.evidence.push(reviewState.evidence);
  }
  saveState(statePath, state);
  return state;
}

function archiveComplete(statePath, options) {
  const state = loadState(statePath);
  const item = currentNode(state);
  if (state.route.current_mode === "fast") throw new Error("Fast 不执行 OpenSpec archive");
  if (item?.id !== "C7" || state.archive_status !== "ready") throw new Error("只有完成 S-FI1 后才能确认 archive");
  if (state.spec_review.status !== "approved") throw new Error("Spec Diff Review 尚未批准");
  if (state.route.current_mode === "governed" && state.code_review.status !== "approved") throw new Error("Code Diff Review 尚未批准");
  const normalized = resolve(statePath).replaceAll("\\", "/");
  if (!normalized.includes("/openspec/changes/archive/")) throw new Error("状态文件尚未进入 OpenSpec archive 目录");
  const evidence = String(options.evidence ?? "").trim();
  if (!evidence) throw new Error("archive-complete 必须提供 --evidence");
  state.archive_status = "completed";
  item.status = "done";
  item.evidence.push(evidence);
  advance(state);
  saveState(statePath, state);
  return state;
}

function reroute(statePath, input, options) {
  if (!REROUTE_CHECKPOINTS.includes(options.checkpoint)) throw new Error(`非法重路由检查点: ${options.checkpoint}`);
  const reason = String(options.reason ?? "").trim();
  if (!reason) throw new Error("reroute 必须提供 --reason");
  const state = loadState(statePath);
  const checkpointNode = state.nodes.find((item) => item.id === REROUTE_PREREQUISITES[options.checkpoint]);
  if (!checkpointNode || !TERMINAL_NODE_STATUSES.has(checkpointNode.status)) {
    throw new Error(`检查点 ${options.checkpoint} 尚未到达；${REROUTE_PREREQUISITES[options.checkpoint]} 必须先完成`);
  }
  const mergedFacts = { ...state.route_facts, ...(input.facts ?? input) };
  const profileReady = input.profile_ready ?? state.profile_ready;
  const decision = routeDecision({ facts: mergedFacts, profile_ready: profileReady });
  const oldMode = state.route.current_mode;
  const rank = { fast: 0, standard: 1, governed: 2 };
  if (rank[decision.route.mode] < rank[oldMode] && !options.allow_downgrade) throw new Error("自动重路由只允许升级；降级需要 --allow-downgrade");
  let outputPath = resolve(statePath);
  if (oldMode === "fast" && decision.route.mode !== "fast") {
    const changeId = String(input.change_id ?? "").trim();
    if (!changeId || !options.output) throw new Error("Fast 升级到 OpenSpec 模式需要 change_id 和 --output");
    outputPath = resolve(options.output);
    const expectedSuffix = `/openspec/changes/${changeId}/workflow-state.json`;
    if (!outputPath.replaceAll("\\", "/").endsWith(expectedSuffix)) {
      throw new Error(`升级状态必须迁移到 openspec/changes/${changeId}/workflow-state.json`);
    }
    if (outputPath !== resolve(statePath) && existsSync(outputPath)) throw new Error(`目标状态文件已存在: ${outputPath}`);
    state.change_id = changeId;
  }
  const oldById = new Map(state.nodes.map((item) => [item.id, item]));
  const newNodes = composeNodes(decision.route).map((item) => {
    const old = oldById.get(item.id);
    return old ? { ...item, status: old.status, evidence: old.evidence } : item;
  });
  state.route_facts = mergedFacts;
  state.profile_ready = profileReady === true;
  state.route_fingerprint = decision.route_fingerprint;
  state.route.current_mode = decision.route.mode;
  state.route.specialized_gates = decision.route.specialized_gates;
  state.route.execution_policy = decision.route.execution_policy;
  if (decision.route.mode === "fast") {
    state.spec_review = { status: "N/A" };
    state.code_review = { status: "N/A" };
    state.archive_status = "N/A";
  } else {
    if (state.spec_review.status === "N/A") {
      state.spec_review = { status: "pending", diff_type: "uncommitted", expected_paths: [], displayed_paths: [], artifact_hashes: [] };
    }
    state.code_review = decision.route.mode === "governed"
      ? state.code_review.status === "N/A" ? { status: "pending", diff_type: "since-base" } : state.code_review
      : { status: "N/A" };
    if (state.archive_status === "N/A") state.archive_status = "pending";
  }
  state.nodes = newNodes;
  state.workflow_hash = workflowHash(state.route, newNodes);
  state.reroutes.push({
    checkpoint: options.checkpoint,
    from_mode: oldMode,
    to_mode: decision.route.mode,
    reason,
    at: new Date().toISOString(),
  });
  advance(state);
  saveState(statePath, state);
  if (outputPath !== resolve(statePath)) {
    mkdirSync(dirname(outputPath), { recursive: true });
    renameSync(resolve(statePath), outputPath);
  }
  return state;
}

function installHooks(root) {
  const fragmentPath = join(root, ".claude", "hooks", "workflow-hooks.json");
  const settingsPath = join(root, ".claude", "settings.json");
  const profilePath = join(root, ".claude", "project-profile.yaml");
  if (!existsSync(fragmentPath)) throw new Error(`Hook 配置不存在: ${fragmentPath}`);
  const fragment = readJson(fragmentPath);
  const settings = existsSync(settingsPath) ? readJson(settingsPath) : {};
  settings.hooks ??= {};
  let added = 0;
  for (const [event, entries] of Object.entries(fragment.hooks ?? {})) {
    settings.hooks[event] ??= [];
    const existing = new Set(settings.hooks[event].map(canonical));
    for (const entry of entries) {
      if (!existing.has(canonical(entry))) {
        settings.hooks[event].push(entry);
        existing.add(canonical(entry));
        added += 1;
      }
    }
  }
  writeJsonAtomic(settingsPath, settings);
  if (existsSync(profilePath)) {
    const profile = readFileSync(profilePath, "utf8");
    const updated = profile.replace(/^(\s*hooks_installed:\s*).+$/m, "$1true");
    if (updated !== profile) {
      const temporary = `${profilePath}.tmp-${process.pid}`;
      writeFileSync(temporary, updated, "utf8");
      renameSync(temporary, profilePath);
    }
  }
  return { settings: relative(root, settingsPath).replaceAll("\\", "/"), added, installed: true };
}

function walkForState(directory, depth = 0) {
  if (!existsSync(directory) || depth > 4) return [];
  const found = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) found.push(...walkForState(path, depth + 1));
    else if (entry.name === "workflow-state.json") found.push(path);
  }
  return found;
}

function activeStates(root) {
  const paths = [
    ...walkForState(join(root, "openspec", "changes")),
    ...walkForState(join(root, ".claude", "workflow-runs")),
  ];
  return paths
    .map((path) => {
      try {
        return { path, state: loadState(path) };
      } catch {
        return null;
      }
    })
    .filter((entry) => entry && entry.state.status !== "completed");
}

function hookSessionStart(root) {
  const active = activeStates(root);
  if (active.length === 0) return;
  if (active.length > 1) {
    process.stdout.write(`[Workflow V${WORKFLOW_VERSION}] 发现 ${active.length} 个未完成 change；先按请求语义消歧，不得擅自选择。\n`);
    return;
  }
  const { path, state } = active[0];
  const item = currentNode(state);
  process.stdout.write(`[Workflow V${WORKFLOW_VERSION}] 恢复 ${state.change_id}：current_node=${state.current_node}，phase=${item?.phase}，state=${relative(root, path)}。从该节点继续，done 节点不得重复。\n`);
}

function hookPreCompact(root) {
  for (const { path, state } of activeStates(root)) {
    state.compaction_count = (state.compaction_count ?? 0) + 1;
    saveState(path, state);
  }
}

function hookPreToolUse(root, input) {
  const active = activeStates(root);
  if (active.length !== 1) return;
  const { state } = active[0];
  const item = currentNode(state);
  if (!item || !["planning", "human_gate"].includes(item.phase)) return;
  const requested = input.tool_input?.file_path;
  if (!requested) return;
  if (state.route.current_mode === "fast") {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: `当前 Fast 节点 ${item.id} 仍处于 planning；完成规划节点后才能编辑文件`,
      },
    }));
    return;
  }
  const absolute = isAbsolute(requested) ? resolve(requested) : resolve(root, requested);
  const allowed = resolve(root, "openspec", "changes", state.change_id);
  const withinAllowed = absolute === allowed || absolute.startsWith(`${allowed}${sep}`);
  if (!withinAllowed) {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: `当前节点 ${item.id} 尚处于 ${item.phase}；Spec Diff Review 批准前只能修改 openspec/changes/${state.change_id}/**`,
      },
    }));
  }
}

function hookStop(root, input) {
  const active = activeStates(root);
  if (active.length !== 1) return;
  const { state } = active[0];
  const item = currentNode(state);
  if (!item || item.human_gate || state.status === "blocked" || input.stop_hook_active === true) return;
  process.stdout.write(JSON.stringify({
    decision: "block",
    reason: `工作流 ${state.change_id} 尚未完成；继续执行 current_node=${item.id}。只有人工 Gate、真实 blocked 或全部 REQUIRED 节点完成时才能停止。`,
  }));
}

function hookCommand(event, root) {
  let input = {};
  try {
    const content = readFileSync(0, "utf8").trim();
    if (content) input = JSON.parse(content);
  } catch {
    input = {};
  }
  if (event === "session-start") return hookSessionStart(root);
  if (event === "pre-compact") return hookPreCompact(root);
  if (event === "pre-tool-use") return hookPreToolUse(root, input);
  if (event === "stop") return hookStop(root, input);
  throw new Error(`未知 hook: ${event}`);
}

function print(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

function main() {
  const [command, subcommand, ...rest] = process.argv.slice(2);
  const options = parseArgs(command === "hook" ? rest : [subcommand, ...rest].filter(Boolean));
  const root = resolve(options.root ?? process.env.CLAUDE_PROJECT_DIR ?? process.cwd());
  if (command === "route") return print(routeDecision(readInput(options)));
  if (command === "compose") {
    const decision = routeDecision(readInput(options));
    return print({ ...decision, nodes: composeNodes(decision.route) });
  }
  if (command === "init-state") {
    if (!options.output) throw new Error("init-state 需要 --output");
    const state = initializeState(readInput(options));
    saveState(options.output, state);
    return print(state);
  }
  if (command === "validate-state") {
    if (!options.state) throw new Error("validate-state 需要 --state");
    const state = readJson(resolve(options.state));
    const errors = validateState(state);
    print({ valid: errors.length === 0, errors });
    if (errors.length) process.exitCode = 1;
    return;
  }
  if (command === "next") {
    const state = loadState(options.state);
    return print({ status: state.status, current_node: currentNode(state) });
  }
  if (command === "transition") return print(transition(options.state, options, root));
  if (command === "capture-spec-diff") return print(captureSpecDiff(options.state, root));
  if (command === "review") return print(review(options.state, options));
  if (command === "archive-complete") return print(archiveComplete(options.state, options));
  if (command === "reroute") return print(reroute(options.state, readInput(options), options));
  if (command === "install-hooks") return print(installHooks(root));
  if (command === "hook") return hookCommand(subcommand, root);
  throw new Error("用法: workflow-runtime.mjs <route|compose|init-state|validate-state|next|transition|capture-spec-diff|review|reroute|archive-complete|install-hooks|hook>");
}

try {
  main();
} catch (error) {
  fail(`[workflow-runtime] ${error.message}`);
}
