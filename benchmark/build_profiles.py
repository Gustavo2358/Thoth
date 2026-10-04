"""Author-defined longitudinal decision fixtures, not predictions from the engine.

S/F = supported success/failure; O = opportunity; R = self-repair;
U = unresolved; T = stylistic feedback. Each run is a separate report block.
Expectations below are specified before executing either split.
"""
import json
from pathlib import Path

D = "present_perfect.duration"
Q = "question.do_support"
A = "article.indefinite"
M = "modal_perfect.should_have"
F = "duration.since_for"
X = "auxiliary.chain"
C = "present_perfect.continuous"
P = "present_perfect.vs_simple_past"


def run(family, outcomes, mode="spontaneous", feature=None):
    return dict(family=family, outcomes=outcomes, mode=mode,
                feature=feature or ("question" if family == Q else "affirmative"))


def sessions(*runs, same_day=False):
    return [dict(day=0 if same_day else i * 7, runs=r if isinstance(r, list) else [r])
            for i, r in enumerate(runs)]


def fact(sp=(0, 0), prompted=(0, 0), controlled=(0, 0), **other):
    return dict(counts=dict(spontaneous=sp, prompted=prompted, controlled=controlled,
                            unknown=(0, 0)), **other)


def profile(id, description, lessons, families, primary=(), strengths=(), collect=(), split="development"):
    return dict(id=id, split=split, description=description, sessions=lessons,
                expected=dict(primary=primary, strengths=strengths, collect=collect, families=families))


PROFILES = [
    profile("D01-empty", "Uma aula sem evidências não demonstra competência nem dificuldade.",
            [dict(day=0, runs=[])], {}),
    profile("D02-sparse", "Um acerto isolado pede coleta, sem declarar domínio.",
            sessions(run(D, "S")), {D: fact(sp=(1, 0), trend="insufficient_data")}, collect=[D]),
    profile("D03-prompt-gap", "Acerta quando guiado, mas erra espontaneamente em dias distintos.",
            sessions([run(Q, "FS"), run(Q, "SSSS", "prompted")],
                     [run(Q, "F"), run(Q, "SSSS", "prompted")],
                     [run(Q, "F"), run(Q, "SSSS", "prompted")]),
            {Q: fact(sp=(1, 3), prompted=(12, 0), mode_gap=True)}, primary=[Q]),
    profile("D04-controlled-only", "Exercício controlado não comprova transferência para conversa.",
            sessions(run(A, "SSSSS", "controlled"), run(A, "SSSSS", "controlled")),
            {A: fact(controlled=(10, 0), trend="insufficient_data")}, collect=[A]),
    profile("D05-clustered-errors", "Três erros na mesma aula mais exercício em outra não provam recorrência.",
            sessions(run(D, "FFF"), run(D, "S", "controlled")),
            {D: fact(sp=(0, 3), controlled=(1, 0))}, collect=[D]),
    profile("D06-recovery", "Erros antigos seguidos de três aulas corretas: melhora, sem dificuldade atual afirmada.",
            sessions(run(D, "FFF"), run(D, "FFF"), run(D, "SSS"), run(D, "SSS"), run(D, "SSS")),
            {D: fact(sp=(9, 6), trend="improving", historical_only=True)}, collect=[D]),
    profile("D07-relapse", "Muitos acertos históricos não anulam recaída recente nem autorizam força estável.",
            sessions(*([run(Q, "SSSSSSSSSS")] * 4 + [run(Q, "FFF")] * 2)),
            {Q: fact(sp=(40, 6), trend="declining")}, primary=[Q]),
    profile("D08-opportunities", "Escolhas alternativas são oportunidades, sem erro nem diagnóstico de evitação.",
            sessions(run(F, "O"), run(F, "O"), run(F, "O")),
            {F: fact(opportunities=3, uncertain_observations=3)}, collect=[F]),
    profile("D09-self-repair", "Autocorreções são evidência distinta de acerto ou erro independente.",
            sessions(run(F, "R"), run(F, "R"), run(F, "R")),
            {F: fact(self_corrections=3, uncertain_observations=3)}, collect=[F]),
    profile("D10-style-ambiguity", "Preferência de estilo e contexto incerto não contaminam accuracy.",
            sessions(run(A, "TUU"), run(A, "TUU")),
            {A: fact(uncertain_observations=6)}, collect=[A]),
    profile("D11-form-transfer", "Perguntas corretas em exercício não cobrem perguntas espontâneas.",
            sessions([run(M, "SSSSS"), run(M, "SSS", "controlled", "question")],
                     [run(M, "SSSSS"), run(M, "SSS", "controlled", "question")]),
            {M: fact(sp=(10, 0), controlled=(6, 0), missing_forms=["negative", "question"])},
            strengths=[M], collect=[M]),
    profile("D12-opportunities-after-errors", "Oportunidades posteriores não apagam tentativas falhas ou suas citações.",
            sessions(run(D, "FSS"), run(D, "SSF"), run(D, "FFF"), run(D, "O"), run(D, "O"), run(D, "O")),
            {D: fact(sp=(4, 5), opportunities=3, uncertain_observations=3)}, primary=[D]),
    profile("D13-competing-targets", "Priorizar duas dificuldades recorrentes mais frequentes e citar falhas reais.",
            sessions(*[[run(Q, "FFF"), run(A, "FFS"), run(D, "FSS")] for _ in range(3)]),
            {Q: fact(sp=(0, 9)), A: fact(sp=(3, 6)), D: fact(sp=(6, 3))}, primary=[Q, A]),
    profile("D14-same-day", "Três relatos no mesmo dia não demonstram dificuldade longitudinal independente.",
            sessions(run(Q, "FFF"), run(Q, "FFF"), run(Q, "FFF"), same_day=True),
            {Q: fact(sp=(0, 9), trend="insufficient_data")}, collect=[Q]),
    profile("H01-repeated-mixed", "Erros em duas datas com algum sucesso: prática, apesar de exercícios perfeitos.",
            sessions([run(D, "FS"), run(D, "SSSSSSS", "controlled")],
                     [run(D, "SF"), run(D, "SSSSSSS", "controlled")]),
            {D: fact(sp=(2, 2), controlled=(14, 0), mode_gap=True)}, primary=[D], split="holdout"),
    profile("H02-observed-strength", "Acertos distribuídos: força observada, mantendo lacunas de perguntas e negações.",
            sessions(*[run(P, "SSS") for _ in range(4)]),
            {P: fact(sp=(12, 0), trend="stable", missing_forms=["negative", "question"])},
            strengths=[P], collect=[P], split="holdout"),
    profile("H03-recovered-modal", "Recuperação em outra construção: reconhecer histórico sem insistir no erro antigo.",
            sessions(run(M, "FFFF"), run(M, "FFFF"), run(M, "SSSS"), run(M, "SSSS"), run(M, "SSSS")),
            {M: fact(sp=(12, 8), trend="improving", historical_only=True)}, collect=[M], split="holdout"),
    profile("H04-declining-duration", "Recaída em since/for deve sobrepor força histórica.",
            sessions(*([run(F, "SSSSSSSS")] * 4 + [run(F, "FFFF")] * 2)),
            {F: fact(sp=(32, 8), trend="declining")}, primary=[F], split="holdout"),
    profile("H05-controlled-gap", "Bom desempenho controlado com falhas espontâneas não prova causa cognitiva.",
            sessions([run(X, "FFF"), run(X, "SSSSSSSS", "controlled")],
                     [run(X, "FFF"), run(X, "SSSSSSSS", "controlled")]),
            {X: fact(sp=(0, 6), controlled=(16, 0), mode_gap=True)}, primary=[X], split="holdout"),
    profile("H06-unresolved", "Contexto ambíguo, paráfrases e autocorreção: coletar, sem inventar falhas.",
            sessions(run(C, "UO"), run(C, "OR")),
            {C: fact(opportunities=2, self_corrections=1, uncertain_observations=4)}, collect=[C], split="holdout"),
    profile("H07-single-failed-day", "Uma aula ruim mais três aulas controladas não prova repetição espontânea.",
            sessions(run(Q, "FFF"), run(Q, "SSS", "controlled"),
                     run(Q, "SSS", "controlled"), run(Q, "SSS", "controlled")),
            {Q: fact(sp=(0, 3), controlled=(9, 0))}, collect=[Q], split="holdout"),
    profile("H08-negative-transfer", "Negação controlada não elimina lacuna de negação em conversa.",
            sessions([run(A, "SSSS"), run(A, "SSS", "controlled", "negative")],
                     [run(A, "SSSS"), run(A, "SSS", "controlled", "negative")], run(A, "SSSS")),
            {A: fact(sp=(12, 0), controlled=(6, 0), missing_forms=["negative", "question"])},
            strengths=[A], collect=[A], split="holdout"),
]

if __name__ == "__main__":
    path = Path(__file__).with_name("profiles.json")
    path.write_text(json.dumps(dict(version="profiles-1", design="same-author synthetic gold IR; not blinded",
                                   profiles=PROFILES), indent=2, ensure_ascii=False) + "\n")
