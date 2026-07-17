---
name: okf-builder
description: Produce, maintain, validate, and consume source-linked Open Knowledge Format (OKF) knowledge for any software repository. Use when Codex needs to deeply analyze code, configuration, APIs, domains, data models, workflows, or operations into reusable repository knowledge; refresh that knowledge after changes; or automatically use an existing OKF bundle while answering repository questions.
---

# OKF Repository Knowledge

Use this skill to turn a repository into a semantic, source-linked OKF bundle. The LLM produces knowledge; the bundled script discovers eligible source files, fingerprints changes, and validates concept structure plus local links and resources. Never treat static inventory as an architectural understanding.

## Initialize

From the target repository root, run:

```bash
python3 <skill-dir>/scripts/okf_index.py --root . init
```

This installs a complete repo-local skill at `.agents/skills/okf-builder/`, then creates `.okf-index.json`, `.okf/discovery.json`, an empty OKF root index, a standalone `tools/okf_index.py`, and managed automatic-retrieval guidance in `AGENTS.md`. Codex discovers repo skills when launched within the repository. Use `--output knowledge` for a different bundle directory. Do not overwrite unrelated `AGENTS.md` instructions.

Configure `source_include` and `exclude` in `.okf-index.json`. The default tracks text files outside excluded generated, dependency, and credential directories. These rules control inventory only; inspect the relevant source directly to establish knowledge.

## Produce

Create or extend the semantic knowledge bundle as follows:

1. Run `python3 tools/okf_index.py discover`, then read `discovery.json` and the repository tree.
2. Inspect only the source, configuration, documentation, and tests needed to establish each fact. Follow imports, contracts, configuration, and call paths when they clarify a boundary or flow.
3. Choose a domain-oriented layout, such as `services/`, `domains/`, `apis/`, `data/`, `workflows/`, `operations/`, or `decisions/`. Do not mirror the source tree mechanically.
4. Produce one concept per durable subject. Use a descriptive `type` based on evidence; do not assign types merely because of a path or file extension. Include a summary, factual structure, relationships, and source citations.
5. Cross-link related concepts. Keep `index.md` files as progressive-disclosure navigation and give the root index `okf_version: "0.1"`.
6. Run `python3 tools/okf_index.py validate` and resolve every error. Validation checks required concept types and local Markdown links and `resource` targets.

Prioritize concepts that answer future engineering questions:

- system and module boundaries, responsibilities, and dependency directions;
- APIs, event contracts, authentication, and external integrations;
- domain models, persistence, data ownership, and migrations;
- important request, batch, and failure flows;
- configuration, deployment, observability, operations, and decisions.

For every non-obvious claim, link the exact source file under `# Sources` or inline. Distinguish confirmed facts from inferences, state uncertainty, and do not copy full source files into the bundle.

Example concept shape:

```markdown
---
type: Service
title: Orders API
description: Owns order lifecycle operations and their HTTP contract.
tags: [orders, api]
resource: ../../services/orders/src/main/java/example/orders/OrdersController.java
---

# Responsibility

...

# Relationships

- Calls [Payments](/services/payments.md).

# Sources

- [OrdersController](../../services/orders/src/main/java/example/orders/OrdersController.java)
```

## Maintain

Run `discover` after repository changes. Compare changed source hashes in `discovery.json` with the `resource` and source links of existing concepts. Re-analyze the affected area, update every impacted concept and relationship, create newly discovered concepts, and mark retired knowledge as deprecated rather than silently deleting history. Refresh the relevant indexes and validate.

## Consume automatically

Before answering a repository question, read the bundle root index and follow only the concepts relevant to the question. Use their source links to verify details when needed. If the bundle is missing or stale for the question, switch to `maintain`; do not require the user to name the bundle, an index, or a command.

## Deterministic commands

```bash
python3 tools/okf_index.py discover
python3 tools/okf_index.py validate
python3 tools/okf_index.py status
```

`discover` is incremental and writes only when the source inventory changes.
