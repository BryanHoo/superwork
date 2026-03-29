import { describe, expect, it } from "vitest";
import fs from "node:fs";
import {
  getSuperworkTemplatePath,
  getClaudeTemplatePath,
  getCodexTemplatePath,
  getSuperworkSourcePath,
  getClaudeSourcePath,
  getCodexSourcePath,
  readSuperworkFile,
  readTemplate,
  readScript,
  readMarkdown,
  readClaudeFile,
} from "../../src/templates/extract.js";

describe("template path functions", () => {
  it("getSuperworkTemplatePath returns existing directory", () => {
    const templatePath = getSuperworkTemplatePath();
    expect(fs.existsSync(templatePath)).toBe(true);
    expect(fs.statSync(templatePath).isDirectory()).toBe(true);
  });

  it("getClaudeTemplatePath returns existing directory", () => {
    const templatePath = getClaudeTemplatePath();
    expect(fs.existsSync(templatePath)).toBe(true);
    expect(fs.statSync(templatePath).isDirectory()).toBe(true);
  });

  it("getCodexTemplatePath returns existing directory", () => {
    const templatePath = getCodexTemplatePath();
    expect(fs.existsSync(templatePath)).toBe(true);
    expect(fs.statSync(templatePath).isDirectory()).toBe(true);
  });
});

describe("deprecated source path aliases", () => {
  it("getSuperworkSourcePath equals getSuperworkTemplatePath", () => {
    expect(getSuperworkSourcePath()).toBe(getSuperworkTemplatePath());
  });

  it("getClaudeSourcePath equals getClaudeTemplatePath", () => {
    expect(getClaudeSourcePath()).toBe(getClaudeTemplatePath());
  });

  it("getCodexSourcePath equals getCodexTemplatePath", () => {
    expect(getCodexSourcePath()).toBe(getCodexTemplatePath());
  });
});

describe("readSuperworkFile", () => {
  it("reads workflow.md from superwork templates", () => {
    const content = readSuperworkFile("workflow.md");
    expect(typeof content).toBe("string");
    expect(content.length).toBeGreaterThan(0);
    expect(content).toContain("#");
  });

  it("reads a script file", () => {
    const content = readSuperworkFile("scripts/task.py");
    expect(typeof content).toBe("string");
    expect(content.length).toBeGreaterThan(0);
  });

  it("throws for nonexistent file", () => {
    expect(() => readSuperworkFile("nonexistent.txt")).toThrow();
  });
});

describe("readTemplate", () => {
  it("throws for nonexistent category/file", () => {
    expect(() => readTemplate("scripts", "nonexistent.txt")).toThrow();
  });
});

describe("readScript", () => {
  it("reads a Python script from scripts/", () => {
    const content = readScript("task.py");
    expect(typeof content).toBe("string");
    expect(content.length).toBeGreaterThan(0);
  });
});

describe("readMarkdown", () => {
  it("reads workflow.md", () => {
    const content = readMarkdown("workflow.md");
    expect(typeof content).toBe("string");
    expect(content).toContain("#");
  });
});

describe("readClaudeFile", () => {
  it("reads settings.json from claude templates", () => {
    const content = readClaudeFile("settings.json");
    expect(typeof content).toBe("string");
    expect(content.length).toBeGreaterThan(0);
    expect(() => JSON.parse(content)).not.toThrow();
  });
});
