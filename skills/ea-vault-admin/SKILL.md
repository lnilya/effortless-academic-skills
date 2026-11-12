---
name: ea-vault-admin
description: |
  Batch-process the task inbox note in the root of the current Obsidian vault. Reads every open task, infers context between consecutive tasks, asks clarifying questions up front, then executes the clear tasks (adding sources with Ilya's interpretation, creating and linking notes, small edits), writes a single timestamped TaskLog for the whole run and opens it when done. Use when Ilya says "run the task inbox", "process my tasks", "vault admin", "do the inbox tasks", or invokes /ea-vault-admin.
---

# Vault Admin: batch-run the Task Inbox

This skill is vault-agnostic. Everything vault-specific (folders, templates, frontmatter schemas,
naming conventions, voice rules) comes from `AGENTS.md` in the vault root. Never hardcode paths
from one vault.

## Step 0: Load the vault context

1. Vault root = current working directory (use absolute paths for all operations).
2. Read `AGENTS.md` in the vault root (fall back to `CLAUDE.md` if missing). Treat it as the source of truth
   for folder structure, templates, frontmatter, and naming.
3. Locate the task inbox: `TaskInbox.md` in the vault root, or any root note whose filename contains "Task Inbox"
   (case-insensitive; also accept "Tasks Inbox", "TaskInbox"). If none or several match, stop and ask Ilya which note to use.
4. Find the templates folder named in `AGENTS.md` (e.g. `__Support/Templates/`) and list its templates.

## Step 1: Parse the task list

- Collect every open task: `- [ ]` lines, plus plain list items or paragraphs if the inbox has no checkboxes.
  Ignore completed `- [x]` items.
- Keep the original order. Order carries meaning.
- Resolve **chained context**: a task that refers to an earlier one implicitly belongs to it.
  Example: "record XYZ" followed by "add ABCD" means ABCD is added to the XYZ note.
  Only chain when the link is unambiguous. If a task could attach to more than one earlier task or note, it goes on the question list.
- For each task, resolve referenced notes (wikilinks, note names, URLs) by searching the vault.

## Step 2: Classify every task

| Class | Meaning | Action |
| --- | --- | --- |
| **Clear** | Intent, target note(s) and output are unambiguous | Execute |
| **Unclear** | Missing target, ambiguous chain, vague output, several possible notes | Ask |
| **Restructuring** | Deletes, moves, renames, merges, splits, or large rewrites of existing notes | Ask for permission, always |

Permission rules:
- Allowed without asking: creating new files, appending to existing notes, adding links or frontmatter values.
- Needs explicit permission: deleting, moving, renaming, merging files, removing or rewriting existing content, changing folder structure.

## Step 3: Present the plan and ask (before doing anything)

Show one compact table:

| # | Task | Class | Planned action | Parallel group |
| --- | --- | --- | --- | --- |

Then ask all questions for Unclear and Restructuring tasks in a single batch (use AskUserQuestion when available,
max 4 questions per call; otherwise a numbered list). Do not start executing until Ilya has answered.
If every task is Clear and none is Restructuring, state the plan and proceed.

## Step 4: Plan parallelism

- Tasks are independent when they touch different target notes and do not chain. Group these.
- Chained tasks, or tasks writing to the same note, run sequentially in inbox order.
- Run independent groups in parallel (parallel tool calls, or subagents for heavy tasks such as fetching and analysing several URLs).
  Each subagent gets: the task text, resolved context, relevant `AGENTS.md` rules, the template to use, and must return a short summary of what it did and its status (🟢/🟡/🔴). Only the main agent writes the TaskLog.

## Step 5: Execute

For each task:
- **Use the right template.** Pick the template matching the note type defined in `AGENTS.md`. Fill its frontmatter per the schema. Never invent a schema when a template exists.
- **Adding a source + interpretation:** fetch the URL (prefer the defuddle skill for web pages), create the source note per the vault's source conventions, keep Ilya's interpretation in his words in a clearly separate section, and link related notes. If a dedicated import skill exists for this vault (listed in `AGENTS.md`), follow it.
- **Creating notes:** follow the naming convention, set parent/links fields, and add a backlink from the parent note when the vault convention requires it.
- **Linking:** use wikilinks to existing notes only. Verify each target exists.
- Follow the voice and scope rules in `AGENTS.md`. Do only what the task asks.
- If a task turns out to be unclear mid-execution, stop that task, mark it 🟡 or 🔴 in the TaskLog, and continue with the others.

## Step 6: Write one TaskLog for the run

One file per run, covering every task processed.

- Folder: `__Support/TaskLogs/` (create it if missing).
- Filename: timestamp from `date "+%Y-%m-%d %H%M"`, e.g. `2026-11-08 1430 TaskLog.md`.
- Frontmatter: only `Type` and `Date`. No other properties.

Status emoji in each header:
- 🟢 completed
- 🟡 partially completed or needs Ilya's attention
- 🔴 could not do

```markdown
---
Type: TaskLog
Date: YYYY-MM-DD
---
## 🟢 Task: <short description>
<Ilya's full original task text, verbatim>

- Created [[...]]
- Added <what> to [[...]]

## 🟡 Task: <short description>
<full original task text>

- Done: <what was done>
- Needs attention: <what is open and why>
```

Keep the "what was done" part concise: bullets, wikilinks to touched notes, no commentary.

## Step 7: Close out

1. In the task inbox, replace the lines of every 🟢 task with a single line linking to this TaskLog: `- [[<TaskLog filename>]]`.
   If several adjacent tasks were done, collapse them into that one line. 🟡 and 🔴 tasks stay in the inbox, with ` → [[<TaskLog filename>]]` appended.
2. Open the TaskLog in Obsidian:
   - Preferred: `obsidian open path="<vault-relative path>"` (obsidian-cli skill).
   - Fallback: `open "obsidian://open?vault=<vault folder name>&file=<url-encoded vault-relative path>"`.
3. Reply in chat with one line per task (emoji + short description) and the TaskLog link. Do not restate content.
