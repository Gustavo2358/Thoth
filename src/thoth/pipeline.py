from __future__ import annotations

from pathlib import Path

import numpy as np

from thoth.contracts import Extraction, Observation, Policy, Resolution, Review, digest
from thoth.embeddings import pedagogical_text
from thoth.provenance import locate
from thoth import prompts


def policy_from_file(path: Path | None = None) -> Policy:
    return Policy.model_validate_json((path or Path(__file__).with_name("policy.json")).read_bytes())


def candidates(vector, records, patterns, neighbors):
    # One candidate per evidence group, ranked by its closest observation.
    # Searching all exemplars lets positive and negative manifestations retrieve
    # the same group; no centroid or nearest-quote decision is treated as truth.
    groups = {}
    for record in records:
        o = record["observation"]
        if o.review.decision != "keep":
            continue
        if vector.shape != record["vector"].shape:
            raise ValueError("Embedding dimensions differ; use one local model for this database")
        score = float(np.dot(vector, record["vector"]))
        root = record["root_id"]
        if root not in groups or score > groups[root][0]:
            groups[root] = (score, record)
    result = []
    for root, (score, representative) in sorted(groups.items(), key=lambda item: (-item[1][0], item[0]))[:neighbors]:
        members = [r for r in records if r["root_id"] == root]
        result.append(dict(candidate_id=representative["id"], root_id=root, similarity=round(score, 6),
                           pattern=patterns.get(root),
                           evidence=[dict(id=r["id"], date=r["occurred_on"],
                                          **r["observation"].model_dump(exclude={"id", "review", "source_start", "source_end", "session_id"})) for r in members]))
    return result


def resolve(observation, vector, records, patterns, policy, llm):
    retrieved = candidates(vector, records, patterns, policy.neighbors)
    if observation.review.decision != "keep":
        decision = Resolution(decision="insufficient_evidence", candidate_id=None,
                              reason="Observation review is unresolved; retain isolated evidence.",
                              pattern_label=None, pattern_description=None, conversation_contexts=[])
    elif not retrieved:
        decision = Resolution(decision="new_pattern", candidate_id=None,
                              reason="No earlier supported evidence to compare; retain an isolated observation.",
                              pattern_label=None, pattern_description=None, conversation_contexts=[])
    else:
        decision = llm.call("resolve", prompts.RESOLVE,
                            {"observation": observation.model_dump(), "candidates": retrieved}, Resolution)
        if decision.candidate_id and decision.candidate_id not in {c["candidate_id"] for c in retrieved}:
            raise ValueError("Resolver chose an ID outside the retrieved candidates")
    root = observation.id
    if decision.decision == "same_pattern":
        chosen = next(c for c in retrieved if c["candidate_id"] == decision.candidate_id)
        root = chosen["root_id"]
    return decision, root, retrieved


def ingest(raw, occurred_on, store, embedder, llm, policy):
    # A pending/invalid interaction never commits a partial session.
    if store.existing(raw, occurred_on):
        return {"already_ingested": True}
    previous = store.records()
    if any(r["embedding_model"] != embedder.model for r in previous):
        raise ValueError("Embedding model differs from the stored vectors")
    extraction = llm.call("extract", prompts.EXTRACT, {"report": raw}, Extraction)
    sid = "SES-" + digest(raw)[:16]
    observations, rejected = [], []
    seen = set()
    for proposal in extraction.observations:
        start, end = locate(raw, proposal.source_excerpt, proposal.learner_quote)
        identity = (start, proposal.learner_quote, proposal.learning_dimension)
        if identity in seen:
            raise ValueError("Duplicate evidence for the same occurrence and ability")
        seen.add(identity)
        review = llm.call("review", prompts.REVIEW,
                          {"excerpt": proposal.source_excerpt, "observation": proposal.model_dump()}, Review)
        if review.decision == "reject":
            rejected.append({"proposal": proposal.model_dump(), "review": review.model_dump()})
            continue
        values = proposal.model_dump()
        if review.decision == "uncertain":
            values["performance"] = "uncertain"
        observations.append(Observation(**values, id="OBS-" + digest([sid, identity])[:16], session_id=sid,
                                        source_start=start, source_end=end, review=review))
    vectors = embedder.embed([pedagogical_text(o) for o in observations])
    records, summaries, retrieval_audit = [], {}, []
    patterns = store.patterns()
    for o, vector in zip(observations, vectors):
        decision, root, retrieved = resolve(o, vector, previous + records, patterns, policy, llm)
        if decision.decision == "same_pattern":
            summaries[root] = (decision.pattern_label, decision.pattern_description, decision.conversation_contexts)
        records.append(dict(id=o.id, observation=o, root_id=root, vector=vector,
                            occurred_on=occurred_on, embedding_model=embedder.model, resolution=decision))
        retrieval_audit.append({"observation_id": o.id, "candidates": retrieved, "decision": decision.model_dump()})
    audit = {"model": llm.metadata(), "embedding": embedder.metadata, "interactions": llm.trace,
             "rejected": rejected, "grouping": retrieval_audit}
    store.commit_session(raw, occurred_on, records, summaries, audit, policy)
    return {"session_id": sid, "observations": len(records), "rejected": len(rejected)}
