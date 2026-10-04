# Learner State

Sessions: 4; accepted observations: 12

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Question formation — do support (`question.do_support`)

Sessions observed: 4; last seen: 2026-01-22

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 3 | 0.200 | [0.006, 0.602] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 9 | 0 | 0.909 | [0.692, 0.997] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Errors concentrated on one recent date; collect more independent spontaneous evidence.
Mode comparison: Prompted/controlled successes exceed spontaneous accuracy in the observed contexts. Task and context differences may explain this; no retrieval diagnosis.
Recent failed spontaneous evidence IDs: OBS-cb554cec9a7d785cb5e8, OBS-53adb02b41d5ddb62646, OBS-cca9cbd14fb9c290c656

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-a18b241ab9854f28591c, OBS-bf8cc99809e5d73dcbac, OBS-07c4177779e212310e8f, OBS-6be757a5bd71a0bda935, OBS-aa5f2d97f9ba942da42a

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-cb554cec9a7d785cb5e8

Session: SES-7b0ac8a69af07c0aa313; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [54, 214) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-53adb02b41d5ddb62646

Session: SES-7b0ac8a69af07c0aa313; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [216, 376) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-cca9cbd14fb9c290c656

Session: SES-7b0ac8a69af07c0aa313; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [378, 538) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-de46c3eae4e0ffe7c074

Session: SES-ac202a796e39647486d3; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [54, 183) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-d83fc4b36b3231e306fc

Session: SES-ac202a796e39647486d3; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [185, 314) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-abe4540ea0e147c797a9

Session: SES-ac202a796e39647486d3; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [316, 445) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-91e5cc50de4665b97c91

Session: SES-970ae27f38fc8a59f85b; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [54, 183) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-a18b241ab9854f28591c

Session: SES-970ae27f38fc8a59f85b; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [185, 314) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-bf8cc99809e5d73dcbac

Session: SES-970ae27f38fc8a59f85b; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [316, 445) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-07c4177779e212310e8f

Session: SES-6d0d71d80c58c8157961; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [54, 183) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-6be757a5bd71a0bda935

Session: SES-6d0d71d80c58c8157961; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [185, 314) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-aa5f2d97f9ba942da42a

Session: SES-6d0d71d80c58c8157961; construction: question.do_support
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [316, 445) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During controlled conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.
