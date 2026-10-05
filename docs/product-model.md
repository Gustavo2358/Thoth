# Thoth: learning history compiled into the next teacher prompt

Thoth is a local persistent pedagogical brain. Its output is `teacher-prompt.md`. The user practices with an external conversational teacher, exports the full conversation as Markdown, ingests it, and pastes one self-contained prompt into the next fresh conversation. Thoth does internal LLM analysis, not the external teaching conversation.

```text
role-labelled conversation.md → analysis + provenance
                              → learner evidence → open patterns → learner state
                              → teaching evidence → small open teaching model
                              → explicitly stated goals
                              → deterministic selection + bounded compiler
                              → teacher-prompt.md + teacher-prompt.audit.json
```

## Input and source

The import boundary accepts only `## User` / `## Assistant`, or `## Learner` / `## Teacher`, case-insensitive, one complete body per turn. An optional single-level Markdown title precedes the first turn. Fenced blocks cannot create turns. A bare second-level heading with any other label, unlabelled preamble, empty turn, missing role or unclosed fence fails explicitly. Other headings inside a body use level three or deeper. There is no provider detection, universal chat importer or report contract.

UTF-8 source bytes are read without newline normalization, preserved as SQLite text and exported byte-for-byte to immutable `sessions/<id>/conversation.md`. Source SHA-256 covers the original UTF-8 bytes. Session identity derives from full source content; the same source cannot acquire a second date. Date is operator-supplied (`--date`, default today). Ingest past sessions with their actual dates and in chronological order. Multiple sources on one date do not establish independent recurrence.

Each turn has a number, deterministic speaker, code-point offsets and line interval. Observation locators are resolved within the stated turn, so identical wording in different turns is safe. An excerpt must identify one contiguous span there; ambiguous duplicate wording within one turn fails. Whitespace differences can be normalized for matching; locators always address the original source. A learner observation cannot point to a teacher turn. Nothing claims audio-level accuracy.

## Learner Model

An observation separates communicative intent, reusable production dimension, and behavior in this occurrence. Linguistic dimensions remain open text in English; they are not grammar enums. Performance is difficulty, successful or uncertain; events distinguish observed use, correction, self-correction and opportunity. Self-repairs/opportunities are not independent successes or failures. Valid alternatives and optional stylistic differences are not errors. Portuguese influence can be a cautious hypothesis, never a fact about mental translation.

The extractor receives all turns. A separate reviewer checks meaning, attribution, support and pedagogical value against that same context. Rejected proposals remain in analysis audit. Uncertain evidence stays isolated. The reviewer does not invent revised fields: an incorrect support/mode interpretation requires corrected extraction and replay.

Support is a small set: `no_support`, `contextual_prompt`, `partial_scaffold`, `explanation_before_attempt`, `model_phrase_available`, `immediate_repetition`, `unknown`. Supporting earlier turns are identified explicitly; usually they belong to the teacher, but an immediate self-echo can refer to an earlier learner repair. Model availability and immediate repetition require controlled mode. Spontaneous mode requires no support. A natural conversational question alone is not necessarily targeted scaffolding. Later reuse in another situation may be unassisted even after teaching earlier in the conversation; semantic interpretation remains reviewable.

The existing learner pipeline is retained: open observations → pedagogical text → local embedding → exemplar retrieval → semantic resolution → provisional groups → recurring patterns → state. spaCy `en_core_web_md` uses normalized mean token vectors, 300 dimensions. Dimension plus communicative intent is embedded, keeping success/failure comparable. Top three evidence groups are retrieved. Cosine never decides membership; the LLM compares all candidate members. No threshold, vector service or second embedding infrastructure was added.

Promotion needs reviewed evidence across two independent dates. Default practice needs two dates and spontaneous difficulty on two of the three most recent dates with spontaneous attempts. A clean most-recent date with unassisted success changes intent to recovery/transfer; difficulty on that same date blocks recovery. This is a conservative change of teaching action, not a mastery declaration. `recovery_dates` can require more dates. Positive-only evidence can become recent strength, also prompting transfer. Three later dates with sessions or 30 days since last evidence make a pattern old enough to observe rather than keep practicing indefinitely. Time is measured against the newest source session, making replay deterministic. These are transparent heuristics, not statistically calibrated proficiency measures.

## Teaching Model

Teaching evidence is separate from learner production: learner requests, reactions to interventions, or rejections, with exact quoted references to learner and optionally teacher turns. A teacher's assertion of a learner preference does not qualify by itself. At least one learner reference is mandatory; the semantic reviewer must verify that it actually supports the interpretation.

The representation is an open instruction, practical interpretation, kind, durability, source refs and a semantic decision. The LLM compares the small existing directive groups directly; no teaching vector index is needed. A durable instruction explicitly requested by the learner is `explicit` immediately. A one-off scoped request can form a `tentative` group but is omitted from the next prompt. Matching scoped evidence on two dates permits an `inferred` instruction, explicitly framed as a tentative recurring hypothesis. Ambiguous praise is `evidence_only` and cannot promote itself into a rule. There are no psychological profiles or numeric confidence scores.

Contradictory instructions must not be semantically merged. The current slice does not automatically resolve every conflict between two valid durable instructions; inspect teaching evidence and replay corrected analysis when needed. This limitation matters for a pilot.

## Goals

Goals are explicit purposes, not deductions from errors. `thoth goals add "..."` persists one short text; `thoth goals` inspects it and `thoth goals remove ID` removes it. Exact normalized duplicates share an ID. Conversation goals require a learner quote and separate review. A goal extracted again during replay can be registered again; remove it afterward if it no longer applies. This is a deliberately small representation, without scheduling or a goal-management product.

## Compiler and audit

The compiler renders from state; no free LLM prose can add learner facts. General oral-production policy is clearly labelled as product defaults, separate from supported personal teaching instructions. Goals steer topics; keyword overlap provides a transparent lightweight ranking cue for patterns, followed by recency, recent difficulty and number of evidence dates. This is not semantic goal inference.

General product defaults and research context are described in [teaching-defaults.md](teaching-defaults.md).

At most two practice, two observe and two transfer items are selected, subject to an approximate character budget (default 8,000). Goal and directive blocks also have small section budgets; whole items are omitted, never clipped mid-instruction. Long quotes are omitted rather than sliced. Practice may include one earlier difficulty and one recent success with support labels. Observation/transfer render communicative purpose and strategy, not target wording, labels containing forms, quotations or suggested answers. The audit preserves full evidence separately. A mechanical guard omits an intent that copies evidence/model wording; paraphrase-level answer leakage still needs review.

A singleton can supply one optional observation intention without being declared a Pattern or weakness. Uncertain isolated proposals are excluded. Omitted items and reasons appear in audit. The prompt has no internal IDs, JSON requirement, special session report, or scripted questions.

Audit links each selected goal/directive/pattern to evidence, session source hash/path, date, speaker, turn, code-point interval and lines; learner evidence also includes support-turn references. Prompt SHA-256 and policy permit checking exactly which artifact was compiled. Full extraction, reviews, resolver candidates/decisions and original LLM responses are separately retained. The database remains internal.

## Replay and implementation

SQLite keeps sources, turns, analyses, observations with vectors/memberships, patterns, teaching evidence/directive groups and goals. There are no migrations for experimental report databases. Sources and turns cannot be updated or deleted through SQL. Reingestion of an unchanged source/date is idempotent.

`ingest existing.md --date ORIGINAL_DATE --reprocess` replays the entire small source history chronologically into an in-memory store and replaces derived analyses/model atomically only on complete success. All later semantic decisions can depend on earlier evidence, so replaying only one session would leave stale state. Pending/invalid LLM responses leave the current database intact. Manual goals are copied. Use a fresh exchange to change an interpretation, because consumed responses are immutable. Artifacts are regenerated after successful publication. This is reconstruction, not event sourcing or another pipeline.

Modules form one local application: conversation boundary; analysis pipeline; learner state; teaching state; persistence; prompt compiler; artifacts; manual/API internal LLM adapters; CLI. There is no tutor, multi-agent runtime, audio, browser integration, dashboard or cloud infrastructure.
