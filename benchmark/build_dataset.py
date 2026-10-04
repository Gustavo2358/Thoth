"""Explicit pedagogical fixtures; labels live only in separate gold files.

This is a same-author, gold-IR grouping experiment, not blinded extraction gold.
"""
import json
from pathlib import Path

from thoth.contracts import Observation, Review, digest


def case(group, quote, dimension, intent, behavior, performance="difficulty", kind="observed_use",
         mode="spontaneous", hypothesis=None, alternatives=(), day=0, related=None, review="keep"):
    return dict(group=group, quote=quote, dimension=dimension, intent=intent, behavior=behavior,
                performance=performance, kind=kind, mode=mode, hypothesis=hypothesis,
                alternatives=alternatives, day=day, related=related, review=review)


def cases(split):
    # Vocabulary/topics vary by split; capability wording varies within each group.
    place = {"development": "the library", "calibration": "the workshop", "holdout": "the clinic"}[split]
    topic = {"development": "budget", "calibration": "launch", "holdout": "itinerary"}[split]
    object_ = {"development": "book", "calibration": "charger", "holdout": "umbrella"}[split]
    rows = [
        case("a", f"I'm with a doubt about the {topic}.", "Conveying personal uncertainty naturally in informal conversation",
             "Say that a proposed choice is unclear to the speaker, without expressing suspicion",
             "Used a noun-based expression instead of a usual conversational uncertainty clause",
             alternatives=["I'm not sure about it."], hypothesis="The phrasing is consistent with Portuguese-like noun constructions.", day=0),
        case("b", f"We need to make a meeting about the {topic}.", "Choosing conventional verb combinations for arranging meetings",
             "Propose arranging a discussion with several people",
             "Combined make with meeting where arranging, scheduling or holding fits the purpose", alternatives=["We should arrange a meeting."], day=0),
        case("c", f"I work at {place} since 2019.", "Expressing duration of a situation that started earlier and still holds",
             "Describe a continuing situation from its starting point to the present",
             "Selected simple present with a past starting point for an ongoing situation", alternatives=["I've worked there since 2019."], day=0),
        case("d", f"I hereby request that you lend me your {object_}.", "Making requests in a register appropriate for conversation with friends",
             "Ask a close friend for a small everyday favor",
             "Used ceremonial administrative language in a relaxed exchange with a friend", alternatives=[f"Could I borrow your {object_}?"], day=0),
        case("e", "That was a bad choice. I wish I had done something else.", "Spontaneous availability of compact expressions of past regret",
             "Reflect on a past action that would have been better",
             "Used a valid paraphrase during an opportunity for a previously practiced compact regret expression",
             performance="uncertain", kind="opportunity", hypothesis="Repeated non-use could be compatible with limited spontaneous availability; its cause is unobserved.", day=0),
        case("f", f"We need to do a decision about the {topic}.", "Conventional verb combinations for reaching a decision",
             "Describe choosing among alternatives",
             "Used do with decision instead of a conventional verb-noun combination", alternatives=["We need to make a decision."], day=0, related="b"),
        case(None, "I am agree with that.", "Expressing agreement with an interlocutor",
             "State agreement with another person's view", "Added be before the lexical verb agree", day=0),
        case("a", f"I stayed in doubt about the {topic}.", "Expressing one's unresolved uncertainty using conversational English",
             "Explain remaining unsure about a possible choice",
             "Used an unusual stay plus noun phrase when describing remaining uncertain", alternatives=["I was still unsure."], day=7),
        case("b", f"They made a meeting to discuss the {topic}.", "Conventional collocations for organizing or holding a meeting",
             "Describe arranging a group discussion",
             "Used make a meeting for arranging/holding a discussion", alternatives=["They held a meeting."], day=7),
        case("c", f"I live near {place} since 2017.", "Connecting a present continuing situation to when it began",
             "State how long an unchanged living situation has continued",
             "Used present simple although the context links a past beginning to the present", alternatives=["I've lived there since 2017."], day=7),
        case("d", f"I would like to formally solicit your {object_}.", "Calibrating everyday requests to an informal relationship",
             "Ask a friend for a small favor without creating social distance",
             "Used bureaucratic request wording in casual conversation", alternatives=[f"Could you lend me your {object_}?"], day=7),
        case("e", "It would have been better to call earlier.", "Availability of concise past-regret phrasing during unprompted speech",
             "Express regret about a past action",
             "Produced a legitimate alternative instead of a previously practiced compact regret form",
             performance="uncertain", kind="opportunity", day=7),
        case("f", f"They did a decision about the {topic}.", "Selecting a conventional verb for decision as a noun",
             "Report reaching a choice among options",
             "Used do a decision rather than make/reach a decision", day=7, related="b"),
        case("a", f"I'm not sure about the {topic}.", "Natural conversational phrasing for personal uncertainty",
             "State being unsure about a proposed choice",
             "Used a conventional conversational uncertainty clause", performance="successful", day=14),
        case("b", f"Let's make a meeting about the {topic}.", "Idiomatic verb-noun combinations when proposing a meeting",
             "Propose organizing a group discussion",
             "Again selected make with meeting rather than arrange/schedule/hold", day=14),
        case("c", f"I've worked at {place} since 2019.", "Describing a state continuing from a past starting point",
             "Connect an ongoing situation with its duration up to now",
             "Used present perfect with an appropriate past starting point", performance="successful", day=14),
        case("d", f"May I respectfully petition you for the loan of your {object_}?", "Register-sensitive requests in relaxed interactions",
             "Ask a close friend for a routine favor",
             "Used unusually ceremonial request language for a casual friendship", day=14),
        case("e", "I should have called earlier.", "Compact expression of retrospective regret",
             "Express that a different past action would have been preferable",
             "Produced a grammatical compact regret expression in a teacher-directed exercise",
             performance="successful", mode="controlled", day=14),
        case(None, "I have doubts about this.", "Unresolved interpretation of doubt wording",
             "Meaning unclear: skepticism, uncertainty or a request for clarification",
             "The report lacks enough context to identify the production ability",
             performance="uncertain", review="uncertain", day=14),
        case(None, "We met at the weekend.", "Time reference appropriate to the speaker's English variety",
             "Report when an event occurred in a British English conversation",
             "Used a legitimate regional expression; no correction is pedagogically required", performance="successful", day=14),
        case("a", f"I'm still unsure about the {topic}.", "Conversational expression of not being certain",
             "Explain uncertainty about an unresolved choice",
             "Used a natural uncertainty expression without prompting", performance="successful", day=21),
        case("c", f"I've lived near {place} for several years.", "Expressing how long a current state has remained true",
             "Describe the duration of an ongoing situation",
             "Produced a suitable past-to-present duration form spontaneously", performance="successful", day=21),
    ]
    # Multiple events on one date must not become a longitudinal difficulty.
    for phrase in ["He suggested me to wait.", "She suggested me to leave.", "They suggested me to stay."]:
        rows.append(case("g", phrase, "Expressing advice with the verb suggest",
                         "Report somebody suggesting an action", "Used suggest with an unsuitable direct-object infinitive complement", day=21))
    if split != "development":
        rows.append(case(None, f"We should make a model of the {topic}.", "Describing construction of a physical model",
                         "Propose building a physical representation", "Used make naturally for creating an object",
                         performance="successful", day=21, related="b"))
        rows.append(case(None, "I'm sorry, I mean I'm not sure yet.", "Unprompted repair while expressing uncertainty",
                         "Clarify one's uncertainty", "Self-repaired an unfinished expression without a teacher cue",
                         performance="uncertain", kind="self_correction", day=21, related="a"))
    if split == "calibration":
        descriptions = {
            0: "Voicing lack of certainty with idiomatic conversational phrasing",
            1: "Selecting an idiomatic verb when a group discussion is arranged",
            2: "Choosing a form for an unchanged state spanning past and present",
            3: "Matching favor-request wording to a close informal relationship",
            4: "Unprompted access to concise expressions evaluating a regretted past action",
            5: "Combining an appropriate English verb with the noun decision",
            7: "Natural ways to convey that one remains unsure",
            8: "English collocations describing the organization of meetings",
            9: "Talking about an ongoing state and its earlier starting time",
            10: "Requesting everyday help without an inappropriately ceremonial register",
            11: "Concise retrospective evaluation of a past choice in spontaneous speech",
            12: "Conventional phrasing for making or reaching decisions",
            13: "Personal uncertainty stated naturally in informal spoken English",
            14: "Idiomatic wording for arranging a group discussion",
            15: "Locating the beginning of a state that continues at present",
            16: "Socially appropriate everyday favor requests between friends",
            17: "Expressing regret about an earlier action concisely",
            20: "Idiomatic spoken expressions of being unsure",
            21: "Verbal forms for states spanning an earlier period through now",
        }
        for index, description in descriptions.items():
            rows[index]["dimension"] = description
    if split == "holdout":
        # Reserved abilities include new lexical targets and an unseen idiomatic
        # pattern, not only changed names/topics for the development descriptions.
        replacements = {
            0: ("I am with doubt about that route.", "Natural first-person expressions of uncertainty", "Explain not being certain about a possible route", "Used an unusual noun-based uncertainty expression"),
            7: ("I remained with a doubt about that route.", "Conversationally natural wording for remaining unsure", "Describe continuing uncertainty about a proposed route", "Used with a doubt to describe remaining unsure"),
            13: ("I'm unsure which route is best.", "Expressing personal uncertainty idiomatically", "State that the best route is not clear", "Used a natural uncertainty clause spontaneously"),
            20: ("I'm not certain which route to choose.", "Natural spoken statements of uncertainty about a choice", "Say that a choice remains unresolved", "Produced a conventional uncertainty statement"),
            1: ("I made my medicine after breakfast.", "Conventional verb-noun wording for taking medication", "Report ingesting prescribed medication, not manufacturing it", "Used make for taking a dose of medication"),
            8: ("She made her pills before lunch.", "Idiomatic verb choices when medication is taken", "Explain that someone swallowed a dose of prescribed pills, not manufactured them", "Used make with pills for ingesting medication"),
            14: ("I'll make my tablets after dinner.", "Choosing conventional verbs for consuming prescribed medicine", "Say when a dose of medication will be taken", "Used make with tablets to mean taking medication"),
            2: ("We are married since 2018.", "Expressing a continuing state with its past starting point", "Describe a marriage that began earlier and remains in effect", "Selected simple present for a situation spanning past through now"),
            9: ("She owns this shop since 2016.", "Connecting a current state to an earlier beginning", "Explain an ownership situation that began earlier and still holds", "Used simple present with since and a past starting year"),
            15: ("We've been married since 2018.", "Describing an ongoing state from its initial past point", "State how long a continuing marriage has lasted", "Used an appropriate spontaneous past-to-present form"),
            21: ("She's owned that shop for years.", "Natural duration expressions for states still true now", "Explain duration of ownership that continues today", "Used an appropriate present-perfect duration expression"),
            3: ("Give me your notes now.", "Politeness calibrated to requests between unfamiliar peers", "Ask an unfamiliar colleague for a favor without imposing", "Used an abrupt command for a nonurgent discretionary favor"),
            10: ("You must send me the slides immediately.", "Interpersonal tone in nonurgent favor requests", "Request help from an unfamiliar peer who has no obligation to comply", "Used demanding wording that imposes an obligation not present in context"),
            16: ("I demand that you explain this to me.", "Appropriate request tone for voluntary help from a peer", "Ask an unfamiliar colleague for optional assistance", "Used a demand in a nonurgent voluntary-help context"),
            5: ("I did a mistake in that calculation.", "Conventional verb combinations when admitting mistakes", "Acknowledge making an error", "Used do a mistake rather than a conventional mistake collocation"),
            12: ("She did another mistake in the form.", "Idiomatic verb-noun combinations for making errors", "Report somebody making an error", "Used do with mistake for committing an error"),
            25: ("Take that chair to the conference room.", "Describing transport of a physical object", "Ask someone to carry furniture to a different place", "Used take legitimately for physical transport"),
        }
        for index, (quote, dimension, intent, behavior) in replacements.items():
            rows[index].update(quote=quote, dimension=dimension, intent=intent, behavior=behavior, alternatives=())
        for day, quote, dim, behavior, performance in [
            (0, "That ticket costs the eyes from the face.", "Natural emphatic expressions of a very high price", "Used an unusual literal body-part formulation to convey high cost", "difficulty"),
            (7, "The hotel was the eyes of the face.", "Idiomatic conversational wording for something very expensive", "Repeated a literal body-part price expression rather than a conventional English formulation", "difficulty"),
            (14, "The hotel was extremely expensive.", "Expressing high cost emphatically in conversational English", "Used a natural emphatic high-price description without needing a particular idiom", "successful"),
        ]:
            rows.append(case("h", quote, dim, "Emphasize that a price is unusually high", behavior,
                             performance=performance, hypothesis="Literal body-part wording could be consistent with Portuguese influence; the cause is unobserved." if performance == "difficulty" else None, day=day))
        rows.sort(key=lambda r: r["day"])
        rows.append(case(None, "Since I work here, I know the procedures.",
                         "Explaining causal reasons with a subordinating connector",
                         "Give a reason for familiarity with procedures, not describe duration",
                         "Used since legitimately to introduce a reason rather than a past starting point",
                         performance="successful", day=21))
    return rows


def write_split(split):
    rows = cases(split)
    output = Path("benchmark/data") / split
    output.mkdir(parents=True, exist_ok=True)
    sessions, gold = [], {}
    for day in sorted({r["day"] for r in rows}):
        selected = [r for r in rows if r["day"] == day]
        raw = f"# Synthetic speaking report — {split} — day {day}\n\n"
        parts = []
        for number, r in enumerate(selected, 1):
            excerpt = (f"Event {number}. In {r['mode']} speaking, the learner said: \"{r['quote']}\" "
                       f"Context: {r['intent']}. Reported behavior: {r['behavior']}.")
            start = len(raw)
            raw += excerpt + "\n\n"
            parts.append((r, excerpt, start, len(raw) - 2))
        sid = "SES-" + digest(raw)[:16]
        observations = []
        for r, excerpt, start, end in parts:
            oid = "OBS-" + digest([sid, start])[:16]
            observation = Observation(id=oid, session_id=sid, source_excerpt=excerpt, learner_quote=r["quote"],
                 source_start=start, source_end=end, production_mode=r["mode"], performance=r["performance"],
                 evidence_type=r["kind"], communicative_intent=r["intent"], learning_dimension=r["dimension"],
                 observed_behavior=r["behavior"], suggested_forms=list(r["alternatives"]), hypothesis=r["hypothesis"],
                 review=Review(decision=r["review"], reason="Author-defined reviewed IR for a controlled grouping experiment"))
            observations.append(observation.model_dump())
            gold[oid] = dict(group=r["group"], related=r["related"], unresolved=r["review"] == "uncertain")
        sessions.append(dict(raw=raw, occurred_on=f"2026-02-{day + 1:02d}", observations=observations))
    (output / "sessions.json").write_text(json.dumps(sessions, indent=2, ensure_ascii=False) + "\n")
    (output / "gold.json").write_text(json.dumps(gold, indent=2) + "\n")


if __name__ == "__main__":
    for split in ["development", "calibration", "holdout"]:
        write_split(split)
