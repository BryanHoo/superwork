import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { ensureDir, writeFile } from "../utils/file-writer.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

type TemplateCategory = "scripts" | "markdown" | "commands";

function getTemplatePath(dirName: string): string {
  const templatePath = path.join(__dirname, dirName);
  if (fs.existsSync(templatePath)) {
    return templatePath;
  }

  throw new Error(
    `Could not find ${dirName} templates directory. Expected at templates/${dirName}/`,
  );
}

/**
 * Get the path to the superwork templates directory.
 *
 * This reads from src/templates/superwork/ (development) or dist/templates/superwork/ (production).
 * These are GENERIC templates, not the Superwork project's own .superwork/ configuration.
 */
export function getSuperworkTemplatePath(): string {
  return getTemplatePath("superwork");
}

/**
 * @deprecated Use getSuperworkTemplatePath() instead.
 * This function is kept for backwards compatibility but now returns the template path.
 */
export function getSuperworkSourcePath(): string {
  return getSuperworkTemplatePath();
}

/**
 * Get the path to the claude templates directory.
 *
 * This reads from src/templates/claude/ (development) or dist/templates/claude/ (production).
 * These are GENERIC templates, not the Superwork project's own .claude/ configuration.
 */
export function getClaudeTemplatePath(): string {
  return getTemplatePath("claude");
}

/**
 * @deprecated Use getClaudeTemplatePath() instead.
 */
export function getClaudeSourcePath(): string {
  return getClaudeTemplatePath();
}

/**
 * Get the path to the Codex templates directory.
 *
 * This reads from src/templates/codex/ (development) or dist/templates/codex/ (production).
 * These are GENERIC templates, not the Superwork project's own .agents/.codex configuration.
 */
export function getCodexTemplatePath(): string {
  return getTemplatePath("codex");
}

/**
 * @deprecated Use getCodexTemplatePath() instead.
 */
export function getCodexSourcePath(): string {
  return getCodexTemplatePath();
}

/**
 * Read a file from the .superwork directory
 * @param relativePath - Path relative to .superwork/ (e.g., 'scripts/task.py')
 * @returns File content as string
 */
export function readSuperworkFile(relativePath: string): string {
  const superworkPath = getSuperworkSourcePath();
  const filePath = path.join(superworkPath, relativePath);
  return fs.readFileSync(filePath, "utf-8");
}

/**
 * Read template content from a .txt file in commands directory
 * @param category - Template category (only 'commands' uses .txt files now)
 * @param filename - Template filename (e.g., 'common/finish-work.txt')
 * @returns File content as string
 */
export function readTemplate(
  category: TemplateCategory,
  filename: string,
): string {
  const templatePath = path.join(__dirname, category, filename);
  return fs.readFileSync(templatePath, "utf-8");
}

/**
 * Helper to read script template from .superwork/scripts/
 * @param relativePath - Path relative to .superwork/scripts/ (e.g., 'task.py')
 */
export function readScript(relativePath: string): string {
  return readSuperworkFile(`scripts/${relativePath}`);
}

/**
 * Helper to read markdown template from .superwork/
 * @param relativePath - Path relative to .superwork/ (e.g., 'workflow.md')
 */
export function readMarkdown(relativePath: string): string {
  return readSuperworkFile(relativePath);
}

/**
 * Helper to read command template (these still use .txt files in src/templates/commands/)
 */
export function readCommand(filename: string): string {
  return readTemplate("commands", filename);
}

/**
 * Read a file from the .claude directory (dogfooding)
 * @param relativePath - Path relative to .claude/ (e.g., 'commands/start.md')
 * @returns File content as string
 */
export function readClaudeFile(relativePath: string): string {
  const claudePath = getClaudeSourcePath();
  const filePath = path.join(claudePath, relativePath);
  return fs.readFileSync(filePath, "utf-8");
}

/**
 * Copy a directory from .superwork/ to target, making scripts executable
 * Uses writeFile to handle file conflicts with the global writeMode setting
 * @param srcRelativePath - Source path relative to .superwork/ (e.g., 'scripts')
 * @param destPath - Absolute destination path
 * @param options - Copy options
 */
export async function copySuperworkDir(
  srcRelativePath: string,
  destPath: string,
  options?: { executable?: boolean },
): Promise<void> {
  const superworkPath = getSuperworkSourcePath();
  const srcPath = path.join(superworkPath, srcRelativePath);
  await copyDirRecursive(srcPath, destPath, options);
}

/**
 * Recursively copy directory with options
 * Uses writeFile to handle file conflicts
 */
async function copyDirRecursive(
  src: string,
  dest: string,
  options?: { executable?: boolean },
): Promise<void> {
  ensureDir(dest);

  for (const entry of fs.readdirSync(src)) {
    const srcPath = path.join(src, entry);
    const destPath = path.join(dest, entry);
    const stat = fs.statSync(srcPath);

    if (stat.isDirectory()) {
      await copyDirRecursive(srcPath, destPath, options);
    } else {
      const content = fs.readFileSync(srcPath, "utf-8");
      const isExecutable =
        options?.executable && (entry.endsWith(".sh") || entry.endsWith(".py"));
      await writeFile(destPath, content, { executable: isExecutable });
    }
  }
}
