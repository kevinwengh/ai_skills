# AI Skills

Reusable AI-agent skills that are safe to share publicly.

## Included skills

| Skill | Purpose |
| --- | --- |
| `fp-rca` | Investigate incidents and failures from evidence to a causal explanation, using 5 Whys where it clarifies a supported causal link. |
| `fp-review` | Challenge product, API, architecture, and implementation proposals from first principles; compare alternatives and recommend a path. |
| `okf-builder` | Create and maintain source-linked Open Knowledge Format (OKF) repository knowledge. |

## First-principles skills

Use `fp-rca` for “Why did this unexpected outcome happen?” It separates observations, inferences, causes, contributors, and control gaps so an investigation does not confuse correlation with root cause.

Use `fp-review` for “Should we make this change?” It establishes the underlying need and ground truths, tests assumptions, derives the smallest credible solution, compares options, and produces a proceed, revise, defer, or reject recommendation.

## OKF Builder

`okf-builder` creates and maintains source-linked repository knowledge in the Open Knowledge Format (OKF). It combines LLM analysis with a small Python tool that inventories eligible source files, detects changes, and validates knowledge-bundle links.

Use it to capture durable knowledge about a codebase's architecture, APIs, domain model, workflows, deployment, and operations without turning a file inventory into a substitute for analysis.

### Contents

```text
okf-builder/
├── SKILL.md                       # Agent workflow and usage instructions
├── agents/openai.yaml             # Codex UI metadata
├── assets/okf-index.config.json   # Default source-inventory configuration
└── scripts/okf_index.py           # Discovery and validation tool
```

### Use in a repository

From the repository you want to document, initialize it with the builder from this checkout:

```bash
python3 /path/to/ai_skills/okf-builder/scripts/okf_index.py --root . init
```

This creates:

- `.agents/skills/okf-builder/` and `.claude/skills/okf-builder/` — repo-local copies of the skill;
- `.okf-index.json` — source inclusion and exclusion rules;
- `.okf/discovery.json` — the incremental source inventory;
- `.okf/index.md` — the root of the OKF knowledge bundle;
- `tools/okf_index.py` — a standalone copy of the builder; and
- managed repository-knowledge sections in `AGENTS.md` and `CLAUDE.md`.

Use a different knowledge-bundle location when needed:

```bash
python3 /path/to/ai_skills/okf-builder/scripts/okf_index.py --root . init --output knowledge
```

### Maintain and validate knowledge

After initialization, run these commands from the target repository root:

```bash
python3 tools/okf_index.py discover
python3 tools/okf_index.py status
python3 tools/okf_index.py validate
```

`discover` refreshes the source inventory only when it changes. `validate` checks that OKF concepts have a type and that local Markdown links and declared resources resolve.

### Agent support

The skill content follows the portable `SKILL.md` convention and includes Codex-specific UI metadata. Copy `okf-builder/` into the relevant global skill directory for Codex or Claude, then use `init` to set up a repository for both `AGENTS.md` and `CLAUDE.md` workflows. No plugin manifests are required.
