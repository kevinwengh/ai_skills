---
name: fp-rca
description: Investigate incidents, defects, failures, and unexpected outcomes with first-principles reasoning and evidence-based root-cause analysis. Use when Codex needs to separate observation from inference, reconstruct a mechanism, test causal hypotheses, or use 5 Whys without inventing a linear or certain cause.
---

# FP RCA

Investigate from observable evidence toward a causal model. Do not begin with a familiar label, a presumed culprit, or a solution.

## Frame the investigation

State the decision the investigation must support, the unexpected outcome, its impact, the expected outcome, and the scope: affected system, time window, and conditions. Record assumptions that limit the conclusion.

## Establish the evidence

Build a timeline and label every claim as one of:

- **Observation** — directly supported by a source; cite it.
- **Inference** — an interpretation of observations; state confidence and what could falsify it.
- **Unknown** — a material missing fact; state how to obtain it.

Do not treat sequence as causation. Prefer contemporaneous telemetry, traces, code, and reproducible tests over recollection. Reconcile contradictory evidence before relying on it.

## Reconstruct the mechanism

Describe the smallest system that can produce the outcome: inputs, state, transformations or decisions, dependencies, outputs, and constraints. Identify the expected invariant or control that failed. Explain the observed outcome in terms of this mechanism, not a component name alone.

## Test causal hypotheses

Generate competing explanations, including a non-change or external-cause explanation when plausible. For each hypothesis, record:

| Hypothesis | Predicted evidence | Discriminating check | Result |
| --- | --- | --- | --- |
| … | … | … | supported, weakened, or unresolved |

Choose the safest, least-invasive check that most clearly separates hypotheses; do not choose a check only because it is convenient. Update or discard a hypothesis when evidence contradicts it.

## Map causes and controls

Represent the supported explanation as a chain or a branching map. Distinguish:

- **Trigger** — the event immediately preceding the outcome.
- **Causal condition** — a condition that was necessary or materially increased the likelihood of the outcome within the stated scope.
- **Contributor** — a condition that worsened impact or removed resilience but did not by itself explain the outcome.
- **Control gap** — a prevention, detection, or mitigation control that was absent or ineffective.

Do not assume there is one root cause. Call a cause confirmed only to the strength supported by evidence; otherwise label it probable or unresolved. State the evidence that would change the conclusion.

## Use 5 Whys as a probe

Use 5 Whys only after validating one causal link. For each “why,” name the system condition, decision, or control that allowed the preceding condition, with supporting evidence. Branch when multiple conditions are required. Stop when the next link is speculative, out of scope, or no longer changes a prevention decision; five is a maximum, not a target.

## Recommend and verify

Tie every action to a causal condition or control gap. State the intended prevention or mitigation mechanism, the owner when known, and the test or metric that will verify it. Prefer actions that remove the causal condition or add a reliable control over actions that merely restate the incident.

## Deliverable

Report, in this order:

1. **Question, scope, outcome, and impact**
2. **Timeline and evidence** — observations, inferences, contradictions, and material unknowns
3. **Mechanism and tested hypotheses** — include results and confidence
4. **Causal map** — trigger, confirmed/probable causes, contributors, and control gaps
5. **Actions and verification** — link each action to the map
6. **Remaining uncertainty** — the next evidence needed, if any

Avoid blame, unsupported certainty, and treating a symptom or incident label as an explanation.
