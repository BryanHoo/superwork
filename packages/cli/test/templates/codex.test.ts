import { describe, expect, it } from "vitest";
import {
  getAllAgents,
  getAllCodexSkills,
  getAllSkills,
  getConfigTemplate,
} from "../../src/templates/codex/index.js";

const EXPECTED_SKILL_NAMES = [
  "superwork-before-dev",
  "superwork-brainstorm",
  "superwork-break-loop",
  "superwork-check",
  "superwork-check-cross-layer",
  "superwork-create-command",
  "superwork-debug-root-cause",
  "superwork-execute-plan",
  "superwork-finish-work",
  "superwork-improve-ut",
  "superwork-integrate-skill",
  "superwork-onboard",
  "superwork-record-session",
  "superwork-spec-plan",
  "superwork-start",
  "superwork-tdd-core",
  "superwork-update-spec",
];

const EXPECTED_AGENT_NAMES = [
  "check",
  "implement",
  "research",
];

describe("codex getAllSkills", () => {
  it("returns the expected skill set", () => {
    const skills = getAllSkills();
    const names = skills.map((skill) => skill.name);
    expect(names).toEqual(EXPECTED_SKILL_NAMES);
  });

  it("each skill has matching frontmatter name", () => {
    const skills = getAllSkills();
    for (const skill of skills) {
      expect(skill.content.length).toBeGreaterThan(0);
      expect(skill.content).toContain("description:");
      const nameMatch = skill.content.match(/^name:\s*(.+)$/m);
      expect(nameMatch?.[1]?.trim()).toBe(skill.name);
    }
  });

  it("preserves bundled skill files when present", () => {
    const skills = getAllSkills();
    const specPlan = skills.find(
      (skill) => skill.name === "superwork-spec-plan",
    );
    expect(specPlan?.files.map((file) => file.path)).toContain("SKILL.md");
    expect(specPlan?.files.map((file) => file.path)).toContain(
      "agents/openai.yaml",
    );
  });

  it("does not include unsupported platform-specific syntax", () => {
    const skills = getAllSkills();
    for (const skill of skills) {
      expect(skill.content).not.toContain("/superwork:");
      expect(skill.content).not.toContain(".claude/");
      expect(skill.content).not.toContain("Task(");
      expect(skill.content).not.toContain("subagent_type");
      expect(skill.content).not.toContain('model: "opus"');
    }
  });
});

describe("codex getAllAgents", () => {
  it("returns the expected custom agent set", () => {
    const agents = getAllAgents();
    const names = agents.map((agent) => agent.name);
    expect(names).toEqual(EXPECTED_AGENT_NAMES);
  });

  it("each agent has required fields (name, description, developer_instructions)", () => {
    for (const agent of getAllAgents()) {
      expect(agent.content.length).toBeGreaterThan(0);
      expect(agent.content).toContain("name = ");
      expect(agent.content).toContain("description = ");
      expect(agent.content).toContain("developer_instructions = ");
    }
  });
});

describe("codex getAllCodexSkills (platform-specific)", () => {
  it("returns codex-specific skills", () => {
    const skills = getAllCodexSkills();
    const names = skills.map((skill) => skill.name);
    expect(names).toEqual(["superwork-parallel"]);
  });

  it("codex-specific skills contain --platform codex", () => {
    const skills = getAllCodexSkills();
    for (const skill of skills) {
      expect(skill.content).toContain("--platform codex");
    }
  });
});

describe("codex getConfigTemplate", () => {
  it("returns project config.toml content", () => {
    const config = getConfigTemplate();
    expect(config.targetPath).toBe("config.toml");
    expect(config.content).toContain("project_doc_fallback_filenames");
    expect(config.content).toContain("AGENTS.md");
  });
});
