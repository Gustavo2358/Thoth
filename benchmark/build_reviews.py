import json
from pathlib import Path

from thoth.contracts import Evidence

CASES = [
    ("I'm with a doubt about that plan.", "The learner meant being unsure about a proposal in informal conversation.",
     "Natural expression of personal uncertainty", "Used an unusual noun-based uncertainty formulation", "The wording is consistent with Portuguese influence; the mental process is unobserved.", "keep"),
    ("We should make a meeting.", "The learner meant arranging a group discussion, not attending an existing meeting.",
     "Conventional verbs for arranging meetings", "Used make with meeting to mean arrange or hold", None, "keep"),
    ("I work here since 2020.", "The job began in 2020 and still continues today.",
     "Expressing ongoing duration", "Selected simple present for a situation continuing from a past beginning", None, "keep"),
    ("I have doubts about the safety of this plan.", "The learner was expressing skepticism about the plan's safety.",
     "Natural expression of uncertainty", "Incorrectly used the noun doubts instead of I'm not sure", None, "reject"),
    ("I would like a coffee, please.", "The learner was politely ordering in a café.",
     "Natural informal requests", "Used overly formal wording; should have said Can I get a coffee", None, "reject"),
    ("We met at the weekend.", "This conversation uses British English and describes when they met.",
     "Natural time reference", "Used at the weekend instead of on the weekend; this is an English error", None, "reject"),
    ("i dont know", "The report uses automated transcription and gives no evidence of a spoken-form problem.",
     "Producing accurate spoken English", "Omitted capitalization and apostrophe in speech", None, "reject"),
    ("I have a question about that.", "The learner was asking for clarification in an ordinary conversation.",
     "Natural clarification requests", "Used a noun-based formulation instead of a shorter alternative", "The learner directly translated from Portuguese.", "reject"),
    ("I have a doubt about it.", "The report does not explain the intent or English variety; it could mean skepticism or a question.",
     "Conversational uncertainty phrasing", "Used doubt as a noun and may have intended a question", "Could be compatible with Portuguese influence, but intent is unclear.", "uncertain"),
    ("I hereby request the loan of your pen.", "The learner was asking a close friend for a tiny nonurgent favor in casual conversation.",
     "Register of everyday favor requests", "Used ceremonial official wording in a relaxed friendship context", None, "keep"),
    ("He suggested me to go.", "The report does not identify whether this quote came from the learner or the teacher's deliberately incorrect example.",
     "Natural reporting of suggestions", "The learner used an unsuitable suggest complement", None, "uncertain"),
    ("It would have been better to call earlier.", "The learner produced this valid regret expression spontaneously after previously practicing another equivalent form.",
     "Spontaneous past-regret phrasing", "Used a valid alternative rather than a previously practiced form", "The learner knows the form but cannot retrieve it and deliberately avoided it.", "reject"),
]

if __name__ == "__main__":
    proposals, gold = [], {}
    for i, (quote, context, dimension, behavior, hypothesis, expected) in enumerate(CASES):
        excerpt = f'Review case {i + 1}. The report quotes: "{quote}" {context}'
        o = Evidence(source_excerpt=excerpt, learner_quote=quote, production_mode="spontaneous", performance="difficulty",
                     evidence_type="observed_use", communicative_intent=context, learning_dimension=dimension,
                     observed_behavior=behavior, suggested_forms=[], hypothesis=hypothesis)
        key = f"case-{i + 1:02d}"
        proposals.append(dict(id=key, observation=o.model_dump()))
        gold[key] = expected
    path = Path("benchmark/data/review")
    path.mkdir(parents=True, exist_ok=True)
    (path / "proposals.json").write_text(json.dumps(proposals, indent=2, ensure_ascii=False) + "\n")
    (path / "gold.json").write_text(json.dumps(gold, indent=2) + "\n")
