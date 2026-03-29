import { afterEach, beforeEach, describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {
  getConfiguredPlatforms,
  configurePlatform,
  collectPlatformTemplates,
  PLATFORM_IDS,
} from "../../src/configurators/index.js";
import { AI_TOOLS } from "../../src/types/ai-tools.js";
import { setWriteMode } from "../../src/utils/file-writer.js";
import {
  getAllAgents as getAllCodexAgents,
  getAllSkills,
  getConfigTemplate as getCodexConfigTemplate,
  getHooksConfig as getCodexHooksConfig,
} from "../../src/templates/codex/index.js";
import { resolvePlaceholders } from "../../src/configurators/shared.js";

describe("getConfiguredPlatforms", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "superwork-platforms-"));
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("returns empty set when no platform dirs exist", () => {
    const result = getConfiguredPlatforms(tmpDir);
    expect(result.size).toBe(0);
  });

  it("detects .claude directory as claude-code", () => {
    fs.mkdirSync(path.join(tmpDir, ".claude"));
    const result = getConfiguredPlatforms(tmpDir);
    expect(result.has("claude-code")).toBe(true);
  });

  it("detects .codex directory as codex", () => {
    fs.mkdirSync(path.join(tmpDir, ".codex"), { recursive: true });
    const result = getConfiguredPlatforms(tmpDir);
    expect(result.has("codex")).toBe(true);
  });

  it(".agents/skills alone does NOT detect as codex (shared standard)", () => {
    fs.mkdirSync(path.join(tmpDir, ".agents", "skills"), { recursive: true });
    const result = getConfiguredPlatforms(tmpDir);
    expect(result.has("codex")).toBe(false);
  });

  it("detects multiple platforms simultaneously", () => {
    for (const id of PLATFORM_IDS) {
      fs.mkdirSync(path.join(tmpDir, AI_TOOLS[id].configDir), {
        recursive: true,
      });
    }
    const result = getConfiguredPlatforms(tmpDir);
    expect(result.size).toBe(PLATFORM_IDS.length);
    for (const id of PLATFORM_IDS) {
      expect(result.has(id)).toBe(true);
    }
  });

  it("ignores unrelated directories", () => {
    fs.mkdirSync(path.join(tmpDir, ".vscode"));
    fs.mkdirSync(path.join(tmpDir, ".git"));
    const result = getConfiguredPlatforms(tmpDir);
    expect(result.size).toBe(0);
  });
});

describe("configurePlatform", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "superwork-configure-"));
    setWriteMode("force");
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
    setWriteMode("ask");
  });

  it("configurePlatform('claude-code') creates .claude directory", async () => {
    await configurePlatform("claude-code", tmpDir);
    expect(fs.existsSync(path.join(tmpDir, ".claude"))).toBe(true);
  });

  it("configurePlatform('claude-code') includes commands directory", async () => {
    await configurePlatform("claude-code", tmpDir);
    expect(fs.existsSync(path.join(tmpDir, ".claude", "commands"))).toBe(true);
  });

  it("configurePlatform('claude-code') includes settings.json", async () => {
    await configurePlatform("claude-code", tmpDir);
    const settingsPath = path.join(tmpDir, ".claude", "settings.json");
    expect(fs.existsSync(settingsPath)).toBe(true);
    const content = fs.readFileSync(settingsPath, "utf-8");
    expect(() => JSON.parse(content)).not.toThrow();
  });

  it("configurePlatform('codex') creates .agents/skills and .codex", async () => {
    await configurePlatform("codex", tmpDir);
    expect(fs.existsSync(path.join(tmpDir, ".agents", "skills"))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, ".codex"))).toBe(true);
  });

  it("configurePlatform('codex') writes all shared skill templates", async () => {
    await configurePlatform("codex", tmpDir);

    const expectedSkills = getAllSkills();
    const expectedNames = expectedSkills.map((skill) => skill.name).sort();
    const skillsRoot = path.join(tmpDir, ".agents", "skills");
    const actualNames = fs
      .readdirSync(skillsRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort();

    expect(actualNames).toEqual(expectedNames);

    for (const skill of expectedSkills) {
      const skillPath = path.join(skillsRoot, skill.name, "SKILL.md");
      expect(fs.existsSync(skillPath)).toBe(true);
      expect(fs.readFileSync(skillPath, "utf-8")).toBe(skill.content);
    }
  });

  it("configurePlatform('codex') writes custom agents and config", async () => {
    await configurePlatform("codex", tmpDir);

    const expectedAgents = getAllCodexAgents();
    const codexAgentsRoot = path.join(tmpDir, ".codex", "agents");
    const actualAgentNames = fs
      .readdirSync(codexAgentsRoot)
      .map((file) => file.replace(".toml", ""))
      .sort();

    expect(actualAgentNames).toEqual(
      expectedAgents.map((agent) => agent.name).sort(),
    );

    for (const agent of expectedAgents) {
      const agentPath = path.join(codexAgentsRoot, `${agent.name}.toml`);
      expect(fs.existsSync(agentPath)).toBe(true);
      expect(fs.readFileSync(agentPath, "utf-8")).toBe(agent.content);
    }

    const config = getCodexConfigTemplate();
    const configPath = path.join(tmpDir, ".codex", config.targetPath);
    expect(fs.existsSync(configPath)).toBe(true);
    expect(fs.readFileSync(configPath, "utf-8")).toBe(config.content);
  });

  it("configurePlatform('codex') resolves PYTHON_CMD in hooks.json", async () => {
    await configurePlatform("codex", tmpDir);

    const hooksPath = path.join(tmpDir, ".codex", "hooks.json");
    expect(fs.existsSync(hooksPath)).toBe(true);
    const content = fs.readFileSync(hooksPath, "utf-8");
    const expectedPythonCmd = process.platform === "win32" ? "python" : "python3";
    expect(content).toContain(
      `"command": "${expectedPythonCmd} .codex/hooks/session-start.py"`,
    );
    expect(content).not.toContain("{{PYTHON_CMD}}");
  });

  it("does not throw for any platform", async () => {
    for (const id of PLATFORM_IDS) {
      const platformDir = fs.mkdtempSync(
        path.join(os.tmpdir(), `superwork-cfg-${id}-`),
      );
      try {
        setWriteMode("force");
        await expect(configurePlatform(id, platformDir)).resolves.not.toThrow();
      } finally {
        fs.rmSync(platformDir, { recursive: true, force: true });
      }
    }
  });

  it("collectPlatformTemplates('codex') resolves placeholders in hooks.json", () => {
    const templates = collectPlatformTemplates("codex");
    expect(templates).toBeInstanceOf(Map);
    expect(templates?.get(".codex/hooks.json")).toBe(
      resolvePlaceholders(getCodexHooksConfig()),
    );
  });

  it("codex hooks.json template keeps PYTHON_CMD placeholder", () => {
    const rawTemplate = getCodexHooksConfig();
    expect(rawTemplate).toContain("{{PYTHON_CMD}} .codex/hooks/session-start.py");
  });
});
