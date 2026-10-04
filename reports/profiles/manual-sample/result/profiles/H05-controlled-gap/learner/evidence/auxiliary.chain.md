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
Recent failed spontaneous evidence IDs: OBS-774a177e8041edd51bc0, OBS-03017a21023a119ff21c, OBS-43427b34fc792d625733, OBS-cac877385025291bb605, OBS-7a048edd1a7a16b74b1d, OBS-ddbfa5ed2a310917f994

Unknowns:

- Insufficient evidence for spontaneous negative forms (fewer than 3 attempts).
- Insufficient evidence for spontaneous question forms (fewer than 3 attempts).

Recent evidence IDs: OBS-fc0859b294cd67305cad, OBS-0113f151f2c75c43f38e, OBS-10f4d5a0c2fa7baf89d6, OBS-c464c229594d9a56d03a, OBS-428308e5b8292c545357

# Auditable Evidence

Raw support scores are observable signals, not probabilities.

## OBS-774a177e8041edd51bc0

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [51, 239) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: The excerpt attributes this affirmative sentence to the learner in spontaneous conversation. Present perfect progressive requires has been working; has working omits been. The reported correction supplies that auxiliary, supporting an explicit grammatical correction in auxiliary.chain.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-03017a21023a119ff21c

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [241, 429) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: The learner's spontaneous affirmative has working lacks been in the auxiliary chain. The excerpt explicitly reports the grammatical correction has been working. Attribution, mode, incorrect outcome and explicit_correction are supported.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-43427b34fc792d625733

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [431, 619) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: The quoted spontaneous learner sentence has working is not a valid present perfect progressive chain. Has been working is a valid repair and is quoted as the teacher's correction. The proposed grammar failure is supported by the source.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-2bfb0c4d5c7efb99e395

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [621, 765) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The excerpt explicitly attributes the affirmative sentence to the learner in controlled practice. Has been working forms a valid auxiliary chain for an ongoing activity over the morning. No correction is reported; correct successful_use is supported.

Source excerpt:

> Block 4. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-c234c48b2d5fd6c0c5eb

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [767, 911) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Has been working is a grammatical affirmative auxiliary chain. The source identifies this as the learner's controlled production, with no repair or teacher correction. The correct outcome and successful_use evidence are supported.

Source excerpt:

> Block 5. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-5cff13bdc6a8e5ad03d5

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [913, 1057) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The controlled learner quote has the grammatical chain has been working. Affirmative feature, learner attribution, controlled mode and successful_use all match the excerpt. There is no grammatical error requiring a corrected form.

Source excerpt:

> Block 6. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-f9e463f80f11f4310887

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1059, 1203) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The learner is explicitly quoted in controlled conversation. Has been working all morning is a valid affirmative perfect progressive auxiliary chain. The proposed correct outcome and absence of correction are supported.

Source excerpt:

> Block 7. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-b6ef1470ede8fc67d06d

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1205, 1349) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The quoted learner sentence correctly combines has, been and working. The source states controlled conversation and reports no repair. This supports affirmative, controlled, correct successful_use for auxiliary.chain.

Source excerpt:

> Block 8. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-0123974166415bcde217

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1351, 1495) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The affirmative auxiliary sequence has been working is grammatical in the reported morning-duration context. The source attributes it to the learner under controlled conditions. Correct successful_use is supported without assuming spontaneous transfer.

Source excerpt:

> Block 9. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-f428ceacad949d0e2532

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1497, 1642) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The source explicitly records a controlled learner utterance. Has been working is the grammatical perfect progressive auxiliary chain and is affirmative. No correction is present, so correct successful_use is supported.

Source excerpt:

> Block 10. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-2ad1369b840e43090a5f

Session: SES-6330e7549125afedd354; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1644, 1789) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The learner's controlled affirmative utterance uses the valid chain has been working. The attribution, production mode, successful_use and correct grammatical outcome agree with the excerpt. This does not establish spontaneous competence.

Source excerpt:

> Block 11. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-cac877385025291bb605

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [51, 239) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: The excerpt attributes this affirmative sentence to the learner in spontaneous conversation. Present perfect progressive requires has been working; has working omits been. The reported correction supplies that auxiliary, supporting an explicit grammatical correction in auxiliary.chain.

Source excerpt:

> Block 1. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-7a048edd1a7a16b74b1d

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [241, 429) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: The learner's spontaneous affirmative has working lacks been in the auxiliary chain. The excerpt explicitly reports the grammatical correction has been working. Attribution, mode, incorrect outcome and explicit_correction are supported.

Source excerpt:

> Block 2. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-ddbfa5ed2a310917f994

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: incorrect; mode: spontaneous; evidence: explicit_correction
Verifier: supported; support score: 4/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [431, 619) (Python Unicode characters)

Learner:

> She has working all morning.

Reported correction (not automatically authoritative):

> She has been working all morning.

Verifier reason: The quoted spontaneous learner sentence has working is not a valid present perfect progressive chain. Has been working is a valid repair and is quoted as the teacher's correction. The proposed grammar failure is supported by the source.

Source excerpt:

> Block 3. During spontaneous conversation, the learner said: "She has working all morning." The teacher corrected this to: "She has been working all morning." The situation still continues.

## OBS-41b4531b91f5d3f17542

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [621, 765) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The excerpt explicitly attributes the affirmative sentence to the learner in controlled practice. Has been working forms a valid auxiliary chain for an ongoing activity over the morning. No correction is reported; correct successful_use is supported.

Source excerpt:

> Block 4. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-84cb7220a7dbb6be9789

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [767, 911) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: Has been working is a grammatical affirmative auxiliary chain. The source identifies this as the learner's controlled production, with no repair or teacher correction. The correct outcome and successful_use evidence are supported.

Source excerpt:

> Block 5. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-1c2e0d420a8055d543ac

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [913, 1057) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The controlled learner quote has the grammatical chain has been working. Affirmative feature, learner attribution, controlled mode and successful_use all match the excerpt. There is no grammatical error requiring a corrected form.

Source excerpt:

> Block 6. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-fc0859b294cd67305cad

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1059, 1203) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The learner is explicitly quoted in controlled conversation. Has been working all morning is a valid affirmative perfect progressive auxiliary chain. The proposed correct outcome and absence of correction are supported.

Source excerpt:

> Block 7. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-0113f151f2c75c43f38e

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1205, 1349) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The quoted learner sentence correctly combines has, been and working. The source states controlled conversation and reports no repair. This supports affirmative, controlled, correct successful_use for auxiliary.chain.

Source excerpt:

> Block 8. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-10f4d5a0c2fa7baf89d6

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1351, 1495) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The affirmative auxiliary sequence has been working is grammatical in the reported morning-duration context. The source attributes it to the learner under controlled conditions. Correct successful_use is supported without assuming spontaneous transfer.

Source excerpt:

> Block 9. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-c464c229594d9a56d03a

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1497, 1642) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The source explicitly records a controlled learner utterance. Has been working is the grammatical perfect progressive auxiliary chain and is affirmative. No correction is present, so correct successful_use is supported.

Source excerpt:

> Block 10. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.

## OBS-428308e5b8292c545357

Session: SES-96f5e645be8e055b8f0a; construction: auxiliary.chain
Outcome: correct; mode: controlled; evidence: successful_use
Verifier: supported; support score: 3/4; pipeline: b7aafbb9804d0f40b74e5b92a6f81e7aaeed1d1569fd92cf29835c39f134e97b
Source offsets: [1644, 1789) (Python Unicode characters)

Learner:

> She has been working all morning.

Verifier reason: The learner's controlled affirmative utterance uses the valid chain has been working. The attribution, production mode, successful_use and correct grammatical outcome agree with the excerpt. This does not establish spontaneous competence.

Source excerpt:

> Block 11. During controlled conversation, the learner said: "She has been working all morning." The sentence was correct in the reported context.
