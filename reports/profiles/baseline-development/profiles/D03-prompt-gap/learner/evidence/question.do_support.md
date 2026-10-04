# Learner State

Sessions: 3; accepted observations: 16

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Question formation — do support (`question.do_support`)

Sessions observed: 3; last seen: 2026-01-15

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 1 | 3 | 0.333 | [0.053, 0.716] |
| prompted | 12 | 0 | 0.929 | [0.753, 0.998] |
| controlled | 0 | 0 | prior only | [0.025, 0.975] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven.

Unknowns:

- Insufficient evidence for negative forms (fewer than 3 attempts).
- Insufficient evidence for question forms (fewer than 3 attempts).
- Fewer than 5 spontaneous attempts; estimate is dominated by sparse evidence.

Recent evidence IDs: OBS-7e0c8220bc26ea1352cb, OBS-d6b3cb89f5ceebea6611, OBS-827cc66913a41a51cc15, OBS-ba1ca62025f1f3e6328a, OBS-a719be8510105b1776ae

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-08dbfb0642414d16d3bf

Session: SES-cde6b6a0d0466069d75a; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [47, 207) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-cc0f62b93ddf1a2525ee

Session: SES-cde6b6a0d0466069d75a; construction: question.do_support
Outcome: correct; mode: spontaneous; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [209, 339) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-ff7ae55cdfd0fe8b7626

Session: SES-cde6b6a0d0466069d75a; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [341, 468) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-334c54320d020b255545

Session: SES-cde6b6a0d0466069d75a; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [470, 597) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 4. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-c19db8924ba9a6cd87bc

Session: SES-cde6b6a0d0466069d75a; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [599, 726) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 5. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-361cefd863235b7cff25

Session: SES-cde6b6a0d0466069d75a; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [728, 855) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 6. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-a30b93c394e132491f4a

Session: SES-6f01796ba67f3961a8ac; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [47, 207) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-aba002990f5ab2f2fb0b

Session: SES-6f01796ba67f3961a8ac; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [209, 336) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-efb02d0b7c35fa0eaa0b

Session: SES-6f01796ba67f3961a8ac; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [338, 465) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-0c5b3971f86fea19f21c

Session: SES-6f01796ba67f3961a8ac; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [467, 594) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 4. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-14a10690f88283d944ed

Session: SES-6f01796ba67f3961a8ac; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [596, 723) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 5. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-7e0c8220bc26ea1352cb

Session: SES-9b165e240bad7241da40; construction: question.do_support
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [47, 207) (Python Unicode characters)

Learner:

> Where you work?

Reported correction (not automatically authoritative):

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "Where you work?" The teacher corrected this to: "Where do you work?" The situation still continues.

## OBS-d6b3cb89f5ceebea6611

Session: SES-9b165e240bad7241da40; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [209, 336) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-827cc66913a41a51cc15

Session: SES-9b165e240bad7241da40; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [338, 465) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-ba1ca62025f1f3e6328a

Session: SES-9b165e240bad7241da40; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [467, 594) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 4. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.

## OBS-a719be8510105b1776ae

Session: SES-9b165e240bad7241da40; construction: question.do_support
Outcome: correct; mode: prompted; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [596, 723) (Python Unicode characters)

Learner:

> Where do you work?

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 5. During prompted conversation, the learner said: "Where do you work?" The sentence was correct in the reported context.
