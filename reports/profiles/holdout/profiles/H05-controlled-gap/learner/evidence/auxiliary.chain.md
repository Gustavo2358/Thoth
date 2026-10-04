# Learner State

Sessions: 2; accepted observations: 22

Facts below are deterministic. Interpretations are hypotheses, not diagnoses.

- Only supported grammatical attempts enter accuracy counts.
- Reports may be selective and attempts correlated: credible intervals are conditional on the independence model, not full real-world certainty.
- Opportunities and self-corrections are recorded separately; no inference of avoidance from a single event.

## Auxiliary chains (`auxiliary.chain`)

Sessions observed: 2; last seen: 2026-01-08

| Production mode | Successes | Failures | Posterior mean | 95% credible interval |
|---|---:|---:|---:|---|
| spontaneous | 0 | 6 | 0.125 | [0.004, 0.410] |
| prompted | 0 | 0 | prior only | [0.025, 0.975] |
| controlled | 16 | 0 | 0.944 | [0.805, 0.999] |
| unknown | 0 | 0 | prior only | [0.025, 0.975] |

Model: Beta(1,1) prior; posterior Beta(1+successes, 1+failures).
Opportunities: 0; self-corrections: 0; uncertain: 0
Trend: insufficient_data

Hypothesis: Preliminary evidence of inconsistent spontaneous production; retrieval cause is unproven.
Mode comparison: Prompted/controlled successes exceed spontaneous accuracy in the observed contexts. Task and context differences may explain this; no retrieval diagnosis.
Recent failed spontaneous evidence IDs: OBS-c4b8d72caae9de0195c5, OBS-5c80bfc7df42585ff066, OBS-55597c4d9cdb12a706f1, OBS-db0394138fbb20e26837, OBS-8ef8670fb5a24915ba8a, OBS-5f9ebda27f3b5dc0749d

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).

Recent evidence IDs: OBS-86c3aba0d2a4268fa791, OBS-22fa07437c048fe80a22, OBS-63f461430525cf8486e7, OBS-aa02fd43354535c5f25f, OBS-e6021e30df727636b573

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-c4b8d72caae9de0195c5

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [51, 239) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-5c80bfc7df42585ff066

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [241, 429) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-55597c4d9cdb12a706f1

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [431, 619) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-6da3b8ed0148d03535a7

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [621, 765) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 4. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-04e27a6c8612b4330c33

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [767, 911) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 5. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-ffb2df54a30f68d3a70e

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [913, 1057) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 6. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-da49e0bc25377f3db9f3

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1059, 1203) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 7. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-4613e88426400f783002

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1205, 1349) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 8. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-51237625e4f1437018f7

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1351, 1495) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 9. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-bf4b707c8923e8bb28fd

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1497, 1642) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 10. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-f99d1b9559a7c8f53fdb

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1644, 1789) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 11. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-db0394138fbb20e26837

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [51, 239) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-8ef8670fb5a24915ba8a

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [241, 429) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-5f9ebda27f3b5dc0749d

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: gold-ir-profiles-1
Source offsets: [431, 619) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-924587a70c046e4d0e5a

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [621, 765) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 4. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-65edeff8e27330290e5b

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [767, 911) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 5. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-8eb653a9feab936ebd66

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [913, 1057) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 6. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-86c3aba0d2a4268fa791

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1059, 1203) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 7. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-22fa07437c048fe80a22

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1205, 1349) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 8. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-63f461430525cf8486e7

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1351, 1495) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 9. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-aa02fd43354535c5f25f

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1497, 1642) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 10. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-e6021e30df727636b573

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: gold-ir-profiles-1
Source offsets: [1644, 1789) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Author-defined gold fixture; no model verdict executed.

Source excerpt:

> Block 11. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.
