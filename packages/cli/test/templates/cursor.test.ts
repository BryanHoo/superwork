import { describe, expect, it } from "vitest";
import { getAllCommands } from "../../src/templates/cursor/index.js";

// =============================================================================
// getAllCommands — reads cursor command templates
// =============================================================================

// Cursor uses prefix naming: superwork-<name>.md (no subdirectory, no parallel)
const EXPECTED_COMMAND_NAMES = [
  "superwork-before-dev",
  "superwork-brainstorm",
  "superwork-break-loop",
  "superwork-check-cross-layer",
  "superwork-check",
  "superwork-create-command",
  "superwork-finish-work",
  "superwork-integrate-skill",
  "superwork-onboard",
  "superwork-record-session",
  "superwork-start",
  "superwork-update-spec",
];

describe("cursor getAllCommands", () => {
  it("returns the expected command set", () => {
    const commands = getAllCommands();
    const names = commands.map((cmd) => cmd.name);
    expect(names).toEqual(EXPECTED_COMMAND_NAMES);
  });

  it("each command has name and content", () => {
    const commands = getAllCommands();
    for (const cmd of commands) {
      expect(cmd.name.length).toBeGreaterThan(0);
      expect(cmd.content.length).toBeGreaterThan(0);
    }
  });

  it("command names do not include .md extension", () => {
    const commands = getAllCommands();
    for (const cmd of commands) {
      expect(cmd.name).not.toContain(".md");
    }
  });
});
