---
name: superwork-writing-plans
description: Use when a non-bug task in a project that uses `.superwork/` is medium-sized, or when a heavy task already has an approved design and needs a written implementation plan before execution.
---

# Writing Plans

## Overview

Write comprehensive implementation plans for the medium path and for heavy tasks that already have an approved design doc. Document everything the executor needs to know: which files to touch for each task, code, testing, docs they might need to check, and how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `.superwork/plans/YYYY-MM-DD-<feature-name>.md`

## Required Inputs

Before writing the plan, read these inputs explicitly:

- the approved design doc from `.superwork/prd/*.md` or task requirements
- `.superwork/workflow.md`
- `.superwork/spec/guides/index.md`
- the relevant package/layer spec indexes and linked concrete docs under `.superwork/spec/**`

If the relevant spec files are not obvious, use the project's scope-aware context discovery flow and read the spec paths it recommends before decomposing tasks.

Keep a short list of the exact spec paths you used. You will write that list into the generated plan document as recommended pre-read material for execution.

Artifact roles stay strict:

- `.superwork/prd/*.md` stores heavy-task design docs from `superwork-brainstorming`
- `.superwork/spec/**/*.md` stores durable project rules, contracts, and verification guidance
- `.superwork/plans/*.md` stores executable implementation plans for `superwork-executing-plans`

## Scope Check

If the task is still light enough for `superwork-tdd` (single-file or small-scope change, config/copy tweak, small test addition, or local doc update), do not write a saved plan. Reroute to `superwork-tdd`.

If the approved design doc or task requirements cover multiple independent subsystems, they should have been broken into separate design docs during brainstorming. If they were not, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**

- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superwork-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Suggested Spec Reads:**
- `.superwork/spec/guides/index.md` — shared workflow rules and project-wide checklists
- `.superwork/spec/<relevant-path>.md` — package/layer rule, contract, or verification checklist used by this plan

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**

- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat(example): 添加具体功能" -m $'- 添加失败测试覆盖目标行为\n- 更新最小实现以通过验证'
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember

- Exact file paths always
- Carry forward the exact spec paths that shaped the plan
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- Commit examples must follow the global Conventional Commit rule: `type(scope): subject`, Chinese subject, and Chinese bullet body when a body is included
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Suggested spec reads:** Check that every path in `Suggested Spec Reads` is real, relevant, and useful to the executor. Remove stale paths and add missing ones.

**3. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**4. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, route execution explicitly:

1. Announce: "Plan complete and saved to `.superwork/plans/<filename>.md`. I'm using `superwork-executing-plans` and starting execution from this saved plan now."
2. Continue immediately with `superwork-executing-plans`. Do not add any extra approval, review, or reassurance pause once self-review passes.
3. If the work is being handed off or parked for later, save the path and tell the next executor to start with `superwork-executing-plans`.

For heavy work, the handoff order is fixed:

`superwork-brainstorming` -> design doc in `.superwork/prd/*.md` -> `superwork-writing-plans` -> plan in `.superwork/plans/*.md` -> `superwork-executing-plans`

Use this handoff wording:

**"Plan complete and saved to `.superwork/plans/<filename>.md`. I'm using `superwork-executing-plans` and starting execution from this saved plan now.**

- **Immediate path:** continue in this session with `superwork-executing-plans`.
- **Later path:** resume from this saved file with `superwork-executing-plans` in a future session."
