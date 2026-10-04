# Validação de Evidence Packs e adaptação — 2026-10-04

**As decisões passaram nos perfis sintéticos após correções. Precisão para alunos reais e ganho de aprendizado continuam não estabelecidos.** O resultado sustenta exploração pessoal com revisão das evidências; ainda não qualifica o produto para orientar um aluno automaticamente.

## O que foi executado

Foram definidos **22 perfis, 70 sessões e 314 observações** em [profiles.json](../benchmark/profiles.json): 14 perfis de desenvolvimento e 8 reservados. As expectativas foram escritas antes da execução, sem consultar a saída do engine. Incluem dados escassos, acerto guiado com erro espontâneo, erros concentrados numa aula, relatos no mesmo dia, recuperação, recaída, prioridades concorrentes, oportunidades, autocorreção, estilo, ambiguidade e lacunas de perguntas/negações.

O teste principal recebe **observações gold já anotadas**, persiste cada histórico no SQLite, reconstrói as runs ativas e gera os mesmos learner states, Evidence Packs e lesson briefs usados pela aplicação. Verifica contagens separadas por modo, médias Beta, exclusões, tendência, seleção e ordenação de alvos, forças, desconhecidos, hipóteses, citações de falhas em datas distintas e invariância a ordem/reprocessamento. Não usa uma LLM para julgar livremente seus próprios packs.

As expectativas são independentes da execução do código, **mas compartilham autor com os dados e as correções**. O conjunto reservado foi executado somente após congelar hashes de dataset, engine, renderer, persistência, contratos, provenance e avaliador, com critérios fixos. Isso é reserva de execução, não cegamento externo. Frases são repetidas e templates se sobrepõem: o ensaio verifica decisões sob condições controladas, não representatividade de conversas reais.

## Resultados

| Execução | Perfis aprovados | Verificações aprovadas | Alvos de prática TP / FP / FN |
|---|---:|---:|---:|
| [Desenvolvimento inicial](profiles/baseline-development/report.md) | 7/14 | 221/236 | 4 / 2 / 1 |
| [Desenvolvimento final](profiles/final-development/report.md) | 14/14 | 235/235 | 5 / 0 / 0 |
| [Reservado após freeze](profiles/holdout/report.md) | 8/8 | 133/133 | 3 / 0 / 0 |

No reservado, precisão e recall dos alvos primários foram **100% neste conjunto**, com somente **3 alvos positivos**. Não é uma estimativa de precisão em alunos reais. O total final foi 368 verificações; não são 368 amostras independentes. O número de verificações muda porque as citações são auditadas para os alvos efetivamente selecionados.

Os gates exigiram todos os critérios pré-definidos aprovados, zero alvos primários indevidos e zero citações inválidas. O [freeze](profiles/freeze.json) registra implementação, dataset e gates. Não houve alteração de engine ou renderer após abrir o reservado.

## Falhas encontradas e correções

- **Recorrência falsa:** erros de uma única aula, combinados com exercício controlado em outra, podiam virar dificuldade longitudinal. Prática agora exige falhas espontâneas em pelo menos duas datas distintas.
- **Recência apagada por oportunidades:** relatos sem tentativa efetiva removiam falhas da janela. A janela agora usa as últimas três datas com tentativas espontâneas daquela construção; não é uma expiração por calendário. O brief pede reconfirmação quando o histórico estiver antigo.
- **Força contraditória após recaída:** muitos acertos históricos permitiam força e prática simultâneas. Força agora exige ausência de falhas na janela recente, além de evidência em pelo menos duas datas.
- **Citações inadequadas:** os últimos cinco eventos podiam ser apenas acertos controlados. O brief agora cita as falhas espontâneas que sustentam a prioridade, preservando a origem de cada uma.
- **Transferência presumida de formas:** perguntas/negações controladas preenchiam lacunas espontâneas. Essas coberturas são separadas e podem gerar coleta mesmo quando há força nas formas observadas.
- **Narrativa desatualizada e lacuna entre modos:** os packs distinguem erros históricos de falhas atuais e descrevem desempenho guiado superior ao espontâneo, sem atribuir causa cognitiva.
- **Corte temporal inconsistente:** múltiplos relatos no mesmo dia podiam cair em metades diferentes da tendência. O corte agora mantém cada data numa única metade.

Os limiares de recorrência, cobertura e diferença entre modos são **regras conservadoras escolhidas para o MVP**, não parâmetros com eficácia pedagógica empiricamente calibrada. A anotação de `question.do_support` foi corrigida de affirmative para question no desenvolvimento antes do freeze; as avaliações anteriores e seus inputs foram preservados.

## Extração real e adapter manual

Executei também o fluxo completo nos mesmos oito perfis usando o [baseline offline](profiles/offline-extraction/report.json). Ele acertou a lista de alvos primários em 7/8 perfis, mas omitiu toda a dificuldade de `auxiliary.chain` e muitas outras evidências. Para as tentativas gold locais, recall foi **35,2%**; não houve falso erro nos 119 controles negativos. Não é adequado para interpretar relatórios gerais.

O matching estrito desse baseline deu precisão de 61,0% para tentativas, mas **isso não significa que 39% dos julgamentos linguísticos foram errados**: o gold define construções locais, não uma anotação exaustiva de toda gramática incidental. Houve 32 acertos extras de present perfect duration em um perfil cujo alvo gold era since/for. São divergências de escopo que exigem adjudicação, não erros gramaticais automaticamente. A cobertura perdida de artigos, modal perfect e auxiliares é uma falha inequívoca do baseline. Listas vazias também acertam alguns perfis por ausência de evidência, portanto 7/8 alvos corretos isoladamente seria enganoso.

Depois executei uma [amostra completa pelo ManualChatGPTAdapter](profiles/manual-sample/result/report.json), usando minhas respostas nesta conversa para o perfil `H05-controlled-gap`:

- Dois prompts de extractor e onze prompts distintos de verifier; os mesmos excerpts/propostas nas duas sessões reutilizam respostas por hash. Foram aceitas 22 observações, com schema e provenance válidos.
- Os JSONs originais foram escritos diretamente a partir dos prompts lidos, sem copiá-los do gold. As respostas dos dois extractors são iguais porque os blocos dos documentos são iguais, mudando apenas o cabeçalho da sessão. Não houve edição pós-importação, reparo de JSON, API ou login automatizado.
- O [pack final](profiles/manual-sample/result/profiles/H05-controlled-gap/learner/evidence/auxiliary.chain.md) registra 0 acertos/6 erros espontâneos e 16 acertos/0 erros controlados. Não conclui domínio nem causa de recuperação; não afirma tendência com apenas duas datas.
- O [brief](profiles/manual-sample/result/profiles/H05-controlled-gap/learner/next-lesson.md) prioriza auxiliares e cita as seis falhas espontâneas. Precisão/recall das 22 observações locais: 100% nessa amostra.

Essa amostra comprova funcionamento do transporte manual e do percurso completo com respostas desta LLM. **Não é qualificação independente**: eu conhecia o perfil e o gold, também escrevi os exemplos e fiz ambos os estágios. O verifier recebeu somente excerpt/proposta no payload, mas meu contexto de conversa não foi apagado. Não houve execução em conversas novas da interface ChatGPT do usuário. A identidade do modelo foi registrada como `Codex / modelo ativo desta conversa`, declaração sem verificação automática. Os prompts, respostas originais, hashes, parsing, audit e resultados estão preservados em [manual-sample](profiles/manual-sample).

## Recomendação e próximo experimento

**Decisões downstream: aprovadas neste benchmark sintético. Runtime completo em relatórios reais: não qualificado. Ganho de aprendizado: não medido.** Recomendo usar o MVP como apoio pessoal com revisão das citações e das prioridades antes de cada aula, mantendo esse uso como experimento acompanhado. Os resultados não justificam prometer melhora ou substituir avaliação docente.

Para avaliar qualidade real sem API, colete inicialmente 10–20 relatórios novos, com erros e acertos, de vários dias e temas. Registre as expectativas e anotações antes de rodar os prompts; idealmente peça revisão a um professor sem mostrar a saída da aplicação. Use conversas novas para extractor e verifier, sem gold ou histórico. Meça cobertura e falsos erros, precisão das prioridades e concordância dos packs; reporte separadamente falhas de schema e oportunidades. Esse conjunto novo deve ser reservado, porque estes oito perfis já estão expostos.

Para medir benefício adaptativo, faça um piloto pessoal pré-definido: duas aulas de linha de base, quatro a seis de prática adaptativa e duas sondagens de retenção/transferência em novos temas, sem fornecer a forma-alvo. Registre oportunidades e tentativas espontâneas, acertos/erros por família, modo de elicitação e tempo de prática. Compare accuracy e cobertura antes/depois com tamanho de amostra e incerteza; meça retenção novamente após 7–14 dias. Uma melhora nesse piloto seria evidência inicial compatível com benefício, ainda confundida por prática, professor e passagem do tempo. Para atribuir vantagem à adaptação, compare com prática de duração equivalente sem priorização adaptativa, usando tarefas/famílias comparáveis e ordem contrabalançada.

## Reprodução e verificações

```bash
# Diretórios novos preservam as avaliações existentes.
.venv/bin/python -m thoth.profile_benchmark development --output /tmp/thoth-profiles-development
.venv/bin/python -m thoth.profile_benchmark freeze --freeze-file /tmp/thoth-profiles-freeze.json
.venv/bin/python -m thoth.profile_benchmark holdout --freeze-file /tmp/thoth-profiles-freeze.json --output /tmp/thoth-profiles-holdout
.venv/bin/python scripts/check_profile_extraction.py --freeze-file /tmp/thoth-profiles-freeze.json --output /tmp/thoth-offline-profiles
.venv/bin/pytest -q
```

Reexecutar o reservado confirma reprodutibilidade; não o torna novamente cego. A suíte rotineira executa somente perfis de desenvolvimento e testa a rejeição de freeze inválido antes de abrir holdout. Foram aprovados **54 testes**, incluindo regressão das decisões, agrupamento temporal por data, detecção de expectativas deliberadamente incorretas, integridade de freeze e todas as verificações existentes do adapter manual, persistência e extração. A verificação de whitespace passou nos arquivos de código; os artifacts gerados foram preservados como emitidos nas avaliações. As bases locais `*.db` são ignoradas pelo Git; `gold-input.json` permite reconstruir cada histórico.
