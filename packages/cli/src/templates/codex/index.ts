/**
 * Codex templates
 *
 * These are GENERIC templates for user projects.
 * Do NOT use Superwork project's own .agents/skills or .codex directories
 * (which may be customized).
 *
 * Directory structure:
 *   codex/
 *   ├── agents/         # Project-scoped Codex custom agents (.toml)
 *   ├── codex-skills/   # Codex-specific skills → .codex/skills/
 *   ├── skills/         # Shared skills → .agents/skills/
 *   └── config.toml     # Project-scoped Codex config
 */

import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function readTemplate(relativePath: string): string {
  return readFileSync(join(__dirname, relativePath), "utf-8");
}

function listDirectories(dir: string): string[] {
  try {
    return readdirSync(join(__dirname, dir), { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort();
  } catch {
    return [];
  }
}

function listFiles(dir: string): string[] {
  try {
    return readdirSync(join(__dirname, dir)).sort();
  } catch {
    return [];
  }
}

function listFilesRecursive(dir: string): string[] {
  try {
    return readdirSync(join(__dirname, dir), { withFileTypes: true })
      .flatMap((entry) => {
        const relativePath = `${dir}/${entry.name}`;
        return entry.isDirectory()
          ? listFilesRecursive(relativePath)
          : [relativePath];
      })
      .sort();
  } catch {
    return [];
  }
}

// Keep skill metadata fast to access while preserving any bundled files.
function getSkillFiles(rootDir: string, skillName: string): SkillFileTemplate[] {
  const baseDir = `${rootDir}/${skillName}`;
  const prefix = `${baseDir}/`;

  return listFilesRecursive(baseDir).map((relativePath) => ({
    path: relativePath.startsWith(prefix)
      ? relativePath.slice(prefix.length)
      : relativePath,
    content: readTemplate(relativePath),
  }));
}

export interface SkillTemplate {
  name: string;
  content: string;
  files: SkillFileTemplate[];
}

export interface SkillFileTemplate {
  path: string;
  content: string;
}

export interface AgentTemplate {
  name: string;
  content: string;
}

export interface ConfigTemplate {
  targetPath: string;
  content: string;
}

export function getAllSkills(): SkillTemplate[] {
  const skills: SkillTemplate[] = [];

  for (const name of listDirectories("skills")) {
    const files = getSkillFiles("skills", name);
    const skillFile = files.find((file) => file.path === "SKILL.md");
    if (!skillFile) {
      continue;
    }
    skills.push({ name, content: skillFile.content, files });
  }

  return skills;
}

export function getAllAgents(): AgentTemplate[] {
  const agents: AgentTemplate[] = [];

  for (const file of listFiles("agents")) {
    if (!file.endsWith(".toml")) {
      continue;
    }

    const name = file.replace(".toml", "");
    const content = readTemplate(`agents/${file}`);
    agents.push({ name, content });
  }

  return agents;
}

/**
 * Get Codex-specific skills (installed to .codex/skills/, not shared .agents/skills/).
 */
export function getAllCodexSkills(): SkillTemplate[] {
  const skills: SkillTemplate[] = [];

  for (const name of listDirectories("codex-skills")) {
    const files = getSkillFiles("codex-skills", name);
    const skillFile = files.find((file) => file.path === "SKILL.md");
    if (!skillFile) {
      continue;
    }
    skills.push({ name, content: skillFile.content, files });
  }

  return skills;
}

export interface HookTemplate {
  name: string;
  content: string;
}

export function getAllHooks(): HookTemplate[] {
  const hooks: HookTemplate[] = [];

  for (const file of listFiles("hooks")) {
    if (!file.endsWith(".py")) {
      continue;
    }
    hooks.push({ name: file, content: readTemplate(`hooks/${file}`) });
  }

  return hooks;
}

export function getHooksConfig(): string {
  return readTemplate("hooks.json");
}

export function getConfigTemplate(): ConfigTemplate {
  return {
    targetPath: "config.toml",
    content: readTemplate("config.toml"),
  };
}
