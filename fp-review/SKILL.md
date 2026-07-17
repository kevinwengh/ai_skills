---
name: fp-review
description: Challenge proposed product, API, architecture, and implementation changes with systematic first-principles reasoning. Use when Codex needs to identify a proposal's problem essence and ground truths, test assumptions or 5 Whys, build and compare solutions from fundamentals, stress-test a recommendation, or decide whether to proceed, revise, defer, or reject.
---

# FP Review

Turn a proposal into an explicit, evidence-backed decision. Challenge the reasoning, not the person who proposed it. Do not treat popularity, an existing pattern, or parity with another system as a requirement.

Use the full review for consequential or hard-to-reverse decisions. For a small reversible change, apply the same sequence briefly and scale the output to the decision.

## 1. Find the problem essence

Complete this problem-validation gate before assessing architecture, designs, or options:

1. Collect the minimum decision-critical requirements: affected user, workflow, current pain, scale or SLO, constraints, and non-goals.
2. Restate the need without the proposed solution.
3. Test whether the proposed solution directly addresses that need, a symptom, or an analogy to another system.
4. If a missing fact could materially change that answer, ask for it or make the review explicitly conditional; do not silently fill the gap with a design assumption.

Strip away the proposed solution. State:

- **Decision:** what must be decided now.
- **Outcome:** the user, business, or operational result that matters.
- **Status quo:** how the outcome is achieved today and its demonstrated cost.
- **Success:** measurable conditions that make the decision worthwhile.
- **Scope:** affected users, systems, time horizon, and non-negotiable constraints.

Ask: “If this system or proposal did not exist, what would users actually need?” A solution statement (“add an API”) is not a problem statement (“application clients need configuration within five seconds”). Do not treat a solution as justified until the problem–solution fit is explicit.

## 2. Establish the reasoning base

Classify material claims before reasoning from them:

| Claim type | Meaning | Treatment |
| --- | --- | --- |
| **Evidence** | Directly supported by a source or measurement | Cite it and note its limits. |
| **Supplied requirement** | A stakeholder constraint, target, or customer need supplied for this decision | Treat it as an input to satisfy; verify any technical mechanism asserted to meet it. |
| **Ground truth** | A verified invariant, hard constraint, or essential user need | Build from it; state why it is non-negotiable. |
| **Assumption** | Plausible but unverified premise | Challenge it and define a safe test. |
| **Unknown** | Missing fact that could change the decision | Name the decision it blocks and how to obtain it. |

Do not call a convention a ground truth. Test an apparent constraint: can it be decomposed further, is it evidenced, and what fails if it is violated? Distinguish immutable limits from current policy, capacity, or preference.

When material evidence or requirements arrive after an initial conclusion, reclassify the affected claims, state what conclusion changes and why, and rerun only the affected reasoning chain and options. Name any retracted inference plainly.

## 3. Challenge assumptions and trace the need

List explicit and implicit assumptions, including technical, business, resource, historical, and organizational assumptions. For each material assumption, record:

| Assumption | Why it may be false or incomplete | Consequence if false | Evidence or test | Verdict |
| --- | --- | --- | --- | --- |

Use 5 Whys only when a proposed solution obscures its underlying need. Each “why” must be supported by evidence or marked as an assumption. Stop when the need is established, the next answer is speculative, or it would not change the decision. Branch when there are multiple reasons; five is a maximum, not a target.

Pay particular attention to these traps:

- **Complexity:** remove a component or capability; if the outcome still holds, it has not earned its cost.
- **Analogy or parity:** identify the other system’s users, boundaries, constraints, and incentives; compare only the relevant dimensions.
- **Legacy:** recover the original reason and test whether its conditions still exist.
- **False constraint:** separate what is physically, contractually, or legally required from a current habit or preference.

For storage, caching, queue, partition, or index proposals, inspect one layer beneath the apparent design before recommending a mechanism. Identify the physical partition and request key, the operations exposed by the actual integration, and whether the need is filtering, ordering, pagination, or projection. Do not recommend an index merely because it is a common solution.

For throughput or scale claims, establish the target RPS, latency objective, concurrency, partition cardinality, page size, required ordering, payload size, and freshness/fallback policy. Reject designs that materialize or sort O(partition size) data for each paginated request unless that bound is demonstrably acceptable.

## 4. Reason upward from fundamentals

Start with the smallest solution that satisfies the ground truths. Add a capability only when it enables a required outcome or control that the smaller solution cannot provide.

For each design choice, show the chain:

```text
Ground truth or evidenced need → required capability → design choice → expected outcome
```

If a link is an assumption, label it and give the evidence needed to validate it. A design choice with no traceable chain is optional until justified.

## 5. Compare credible options

Compare the status quo, the minimal credible solution, and the proposal. Include another option only when it is materially distinct. Evaluate each against the same success criteria:

| Option | Need addressed | Benefits | Costs and risks | Reversibility | Evidence still needed |
| --- | --- | --- | --- | --- | --- |

Assess applicable boundary and lifecycle effects: API compatibility, security and authorization, latency and availability, data correctness, operational load, ownership, migration, and retirement cost. Do not invent concerns that do not apply.

## 6. Stress-test and decide

Run a brief pre-mortem: assume the recommendation failed. Identify the most likely failure modes, the earliest signal for each, and the control or experiment that reduces the risk. Then perform a reversal check: state the smallest new fact that would change the recommendation.

Choose one:

- **Proceed** — the need, reasoning chain, and trade-offs are sufficiently supported.
- **Revise** — the direction is viable but the scope, design, or controls must change.
- **Defer** — a decision-critical unknown or prerequisite remains.
- **Reject** — the proposal does not solve an evidenced need or its trade-offs are unacceptable.

Tie the recommendation to evidence, not confidence alone. When uncertainty is material, prefer the smallest safe experiment, prototype, or staged rollout that resolves it.

## Deliverable

Present a concise review in this order:

1. **Decision, requirements, problem essence, and success criteria**
2. **Problem–solution fit** — whether the proposal addresses the need, a symptom, or an analogy
3. **Reasoning base** — evidence, ground truths, assumptions, and decision-critical unknowns
4. **Assumptions and 5 Whys** — only when useful
5. **Reasoning chain and minimal solution**
6. **Options and trade-offs**
7. **Pre-mortem and reversal check**
8. **Recommendation, validation plan, and open questions**

When later information changed the review, add **Changed conclusions** immediately before the recommendation. State the prior conclusion, the new fact, and the resulting revision.

Do not claim a perfect or universally optimal answer. The goal is a transparent decision whose reasoning can be inspected and revised when new evidence arrives.
