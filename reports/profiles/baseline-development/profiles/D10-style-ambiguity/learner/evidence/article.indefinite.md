# Learner State

Sessions: 2; accepted observations: 6

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Indefinite articles (`article.indefinite`)

Sessions observed: 2; last seen: 2026-01-08

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 0 | prior only | [0.025, 0.975] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 6
Trend: insufficient_data

Hypothesis: Insufficient spontaneous attempt evidence.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-608e25f9925554704f3e, OBS-97838fbf3d6947769c7d, OBS-3a77dc96500fb10b27eb, OBS-1034250578e33b989ab2, OBS-96be1ca7910143ecdcff

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-d5f6a51042b17c4a5acb

Session: SES-d792d588badb0d4d872a; construction: article.indefinite
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [52, 212) (Python Unicode characters)

Learner:

> I bought an umbrella.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I bought an umbrella." The teacher suggested a more formal style; this was not a grammatical error.

## OBS-608e25f9925554704f3e

Session: SES-d792d588badb0d4d872a; construction: article.indefinite
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: uncertain; support score: 2/4; pipeline: gold-ir-profiles-1
Source offsets: [214, 364) (Python Unicode characters)

Learner:

> I bought an umbrella.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I bought an umbrella." Context is missing; grammatical interpretation remains unresolved.

## OBS-97838fbf3d6947769c7d

Session: SES-d792d588badb0d4d872a; construction: article.indefinite
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: uncertain; support score: 2/4; pipeline: gold-ir-profiles-1
Source offsets: [366, 516) (Python Unicode characters)

Learner:

> I bought an umbrella.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "I bought an umbrella." Context is missing; grammatical interpretation remains unresolved.

## OBS-3a77dc96500fb10b27eb

Session: SES-54d689682dd615b724f7; construction: article.indefinite
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [52, 212) (Python Unicode characters)

Learner:

> I bought an umbrella.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I bought an umbrella." The teacher suggested a more formal style; this was not a grammatical error.

## OBS-1034250578e33b989ab2

Session: SES-54d689682dd615b724f7; construction: article.indefinite
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: uncertain; support score: 2/4; pipeline: gold-ir-profiles-1
Source offsets: [214, 364) (Python Unicode characters)

Learner:

> I bought an umbrella.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I bought an umbrella." Context is missing; grammatical interpretation remains unresolved.

## OBS-96be1ca7910143ecdcff

Session: SES-54d689682dd615b724f7; construction: article.indefinite
Outcome: uncertain; mode: spontaneous; evidence: other
Verifier: uncertain; support score: 2/4; pipeline: gold-ir-profiles-1
Source offsets: [366, 516) (Python Unicode characters)

Learner:

> I bought an umbrella.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "I bought an umbrella." Context is missing; grammatical interpretation remains unresolved.
