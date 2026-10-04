# Learner State

Sessions: 2; accepted observations: 4

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Present perfect — duration (`present_perfect.duration`)

Sessions observed: 2; last seen: 2026-01-08

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 3 | 0.200 | [0.006, 0.602] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 1 | 0 | 0.667 | [0.158, 0.987] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Errors concentrated on one recent date; collect more independent spontaneous evidence.
Mode comparison: Insufficient evidence of a prompted/controlled versus spontaneous gap.
Recent failed spontaneous evidence IDs: OBS-8c691e5f1d5e76c416ed, OBS-e7fb65db18edecc5fc5a, OBS-f5615a2cee1c9e8b4246

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-8c691e5f1d5e76c416ed, OBS-e7fb65db18edecc5fc5a, OBS-f5615a2cee1c9e8b4246, OBS-676b03b0ae08e426d88d

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-8c691e5f1d5e76c416ed

Session: SES-1ae5e2349a3905be28eb; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [53, 230) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-e7fb65db18edecc5fc5a

Session: SES-1ae5e2349a3905be28eb; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [232, 409) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-f5615a2cee1c9e8b4246

Session: SES-1ae5e2349a3905be28eb; construction: present_perfect.duration
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [411, 588) (Python Unicode characters)

Learner:

> I live here since 2021.

Reported correction (not automatically authoritative):

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "I live here since 2021." The teacher corrected this to: "I've lived here since 2021." The situation still continues.

## OBS-676b03b0ae08e426d88d

Session: SES-63c3576f70e587244fcf; construction: present_perfect.duration
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [53, 191) (Python Unicode characters)

Learner:

> I've lived here since 2021.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During controlled conversation, the learner said: "I've lived here since 2021." The sentence was correct in the reported context.
