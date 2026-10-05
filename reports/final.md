# Thoth — continuidade pedagógica entre conversas independentes

**Recomendação: piloto pessoal supervisionado.** O vertical slice está implementado: conversa Markdown completa → análise com provenance → Learner Model, Teaching Model e Goals → `teacher-prompt.md` limpo e autocontido, com audit separado. A campanha prova atualização longitudinal dos artifacts e invariantes técnicos em conversas sintéticas. Não prova eficácia educacional, precisão populacional de extração nem obediência de um professor externo real.

## Leitura e mudança de direção

Antes de modificar, li README, relatório de qualificação anterior, exemplos, módulos runtime, testes e harness. O HEAD de partida é `2d2560b`. A evidência anterior qualifica principalmente retrieval/agrupamento sobre IR sintética revisada; a ingestão anterior exercitava relatórios narrativos, não conversas completas. Não reutilizei seus percentuais como qualificação das capacidades novas.

Foram removidos o contrato de relatório como input, os exemplos narrativos, o comando `next-lesson`, o renderer de brief, `next-lesson.md`, o harness de campanhas orientadas a reports/IR com freeze e calibração automática, os datasets/exchanges/artifacts dessa definição e o gate de freeze daquele experimento. O relatório anterior foi substituído por este. Git preserva a história. Não há versões de produto paralelas, caminhos legacy, adapters de compatibilidade, migrations, feature flags ou pipelines duplicados.

Foram reutilizados o modelo aberto de observações, revisão independente de propostas, representação pedagógica em inglês, embeddings spaCy locais, retrieval por exemplares, resolução semântica, roots provisórios, promoção longitudinal, estado com evidência positiva, SQLite, adapter manual com respostas imutáveis, adapter API interno existente, evidence packs e métricas pairwise. Os testes relevantes foram adaptados ao contrato de conversa. A aplicação continua um monólito modular local.

## Conversa Markdown e provenance

A boundary aceita `## User`/`## Assistant` ou `## Learner`/`## Teacher`, case-insensitive. Título de nível um é opcional; o corpo pode conter texto, Markdown e blocos cercados. Headings dentro de cercas não criam turnos. Heading de nível dois desconhecido, papel ausente, conteúdo anterior sem atribuição, turno vazio e cerca não fechada falham. Não existiam exports reais identificáveis no repositório; o formato canônico mínimo foi documentado, sem inventar um importador universal.

O arquivo UTF-8 é lido como bytes e decodificado sem normalizar newlines. SQLite preserva a string original e SHA-256 dos bytes; os artifacts reconstituem o arquivo byte-for-byte. Fontes/turnos não podem ser alterados ou apagados por SQL. A data é declarada pelo operador, não inventada pelo modelo. Fontes iguais não podem receber outra data. A ingestão deve ser cronológica.

Cada evidência aponta para sessão, turno e speaker, com trecho, offsets em code points e linhas no source. O matching ocorre dentro do turno declarado: repetição da frase em outro turno não torna o locator ambíguo. Duas ocorrências indistinguíveis dentro do mesmo turno falham. Suporte aponta para turnos anteriores, geralmente do professor; um self-echo pode apontar para o próprio aluno. A evidência nunca tenta reconstruir o áudio.

## Evidências e estados conceituais

O **Learner Model** descreve produção: intenção, dimensão aberta, comportamento, performance, evento e suporte. O extractor vê a conversa inteira; o reviewer verifica atribuição, valor pedagógico, validade da formulação e contexto de suporte. Alternativas válidas e preferências estilísticas não viram dificuldades. Transferência do português permanece hipótese. Não existe score de mastery/confidence ou diagnóstico mental.

`no_support`, `contextual_prompt`, `partial_scaffold`, `explanation_before_attempt`, `model_phrase_available`, `immediate_repetition` e `unknown` são suficientes para esta fatia. Modelo disponível e repetição imediata exigem produção controlada. Espontaneidade exige ausência de suporte. Uma pergunta natural não é automaticamente scaffolding. Produção depois de uma explicação ou início de construção fornecido é guiada; não equivale a disponibilidade espontânea. A classificação ainda depende de interpretação semântica e revisão.

O embedding mantém dimensão + intenção, sem resultado ou frase bruta. Os pesos spaCy `en_core_web_md` 3.8.0 continuam locais, em 300 dimensões, com hash verificado pelos testes. Retrieval retorna até três grupos pelos exemplares. A LLM decide membership considerando seus membros; cosine não decide verdade. Não houve novo vector infrastructure.

O **Teaching Model** descreve pedidos, reações e rejeições. Teaching evidence guarda citações e sequência relevante; não equivale a diretiva persistente. Pelo menos uma referência do aluno é necessária. O reviewer precisa confirmar que ela sustenta a instrução, em vez de apenas aparecer perto de uma afirmação do professor.

Preferência durável explícita entra como `explicit`. Pedido sobre uma tentativa pode formar grupo `tentative`, omitido do prompt. O mesmo comportamento sustentado em duas datas pode entrar como `inferred`, sempre apresentado como hipótese recorrente a verificar. Praise ambíguo fica `evidence_only`. Chunking foi pedido em duas datas e apoiado por reação contextual, sem afirmar que é o melhor método para essa pessoa. Não foram criados enums de métodos ou perfil psicológico. Deduplicação usa comparação semântica direta entre poucos grupos, sem embeddings adicionais.

**Goals** expressam propósito: texto explícito cadastrado pela CLI ou declarado pelo aluno e revisado separadamente. Não são inferidos de erros. Normalização textual deduplica objetivos idênticos. Há inspeção, adição e remoção, sem produto de gestão de metas. Goals manuais sobrevivem ao replay; goals extraídos novamente podem ser registrados outra vez, uma limitação documentada.

## Como o estado muda o próximo prompt

A política promove padrões em duas datas independentes. O default pratica dificuldades espontâneas em duas das três datas recentes de tentativa, com pelo menos duas datas de evidência. Uma data mais recente com sucesso sem suporte e sem dificuldade espontânea na mesma data muda a intenção para testar recuperação/transferência. Isso impede reensinar automaticamente após melhora observável, sem declarar domínio. `recovery_dates` permite exigir mais datas. Sucesso apenas guiado não ativa recuperação.

Um padrão sem evidência recente — três datas posteriores com sessões ou 30 dias em relação à sessão mais nova — volta a observação. Não é ensinado para sempre. Todos esses critérios são heurísticas transparentes de ação pedagógica; os parâmetros anteriores não eram verdades estatísticas a preservar. A mudança foi validada pela propriedade de produto pedida, não por promessa de learning gain.

O compiler é determinístico. Usa goals, diretivas sustentadas e estado; ordena patterns por atualidade, sobreposição textual com goals, recência, dificuldades recentes e datas de evidência. Não pede a uma LLM que invente prioridades ou redija novos fatos. No máximo dois itens por estratégia entram, dentro do budget. O objetivo explícito orienta a agenda mesmo quando o pattern mais forte é de outro assunto; prática alheia ao objetivo não deve ser forçada.

Prática orienta tentativa → resposta ao significado → feedback seletivo → explicação/scaffold útil → nova produção → variação posterior. Observação orienta uma oportunidade natural sem revelar target ou diagnosticar fraqueza. Recuperação orienta novo contexto sem lembrar wording antigo. Os dois últimos blocos omitem exemplos, sugestões e labels com formas-alvo; um guard mecânico também impede cópia literal de wording pela intenção. Esse guard não detecta toda paráfrase de priming; a qualidade da intenção continua dependente da análise.

Defaults gerais do produto são identificados separadamente: retrieval antes do modelo, feedback seguido de produção, repetição com variação, revisitação distribuída, diferença entre imitação e transferência, aceitação de alternativas e liberdade conversacional. Não foram persistidos como preferências pessoais inventadas. O prompt não é script de perguntas nem exige relatório no final.

O budget é aproximado: 8.000 caracteres por default, sem token counting sofisticado. Uma fração simples do espaço flexível vai para goals/diretivas; o restante fica disponível às estratégias. Estrutura recebe pequena reserva. Instruções e evidências são omitidas inteiras, nunca truncadas no meio. Prática pode contrastar uma dificuldade anterior com um sucesso recente, sempre indicando suporte. O audit lista seleções, omissões, políticas, estratégias, evidências, locators e SHA-256 do prompt. O Markdown não exibe IDs internos.

## Replay, idempotência e artifacts

Uma sessão só é publicada depois de extração, revisão, agrupamento, teaching analysis e goal review concluírem. Pendência/JSON inválido não deixa meia sessão. Reingestão da mesma fonte/data não duplica evidência.

`ingest fonte-existente.md --date DATA_ORIGINAL --reprocess` recompõe o histórico inteiro em um Store temporário vazio. Somente após replay completo substitui os modelos/análises derivados em transação; fontes/turnos ficam intactos. Refazer apenas uma sessão deixaria decisões futuras desatualizadas. Uma pendência preserva o estado atual. Um novo exchange permite corrigir interpretações sem sobrescrever respostas antigas. Não há plataforma de event sourcing.

Os artifacts incluem prompt, audit, learner state, teaching model, goals, evidence packs e raw conversations. A cadeia auditável é seção/intenção → Goal/Directive/Pattern → evidência → conversa → turnos e suporte. A fonte é reconstruível; o banco é interno.

## Campanha e fluxo demonstrado

A campanha usa a **CLI de produção**, adapter manual, SQLite vazio e embeddings reais. Gold só é lido após ingestão. Cada execução começa com estado vazio e produz snapshots no ponto correto do histórico. Não utiliza respostas futuras para compilar prompts anteriores.

Foram criadas oito conversas, em três históricos: continuidade de arquitetura e produção; casos adversariais e scaffolding; dificuldade recorrente de collocation com um goal técnico independente. Cobrem dificuldades, positivos, self-repair, oportunidade, recast, correção, repetição imediata, self-echo, reutilização posterior espontânea, suporte parcial, explicação antes da tentativa, preferências explícitas, praise local, pedidos de chunking, rejeições de estratégias, perguntas “why?”, teacher-only claims, “repeat” comum/não pedagógico, hipóteses de português e alternativas válidas.

A mesma assistência autorou conversas, gold e respostas semânticas. As respostas foram fornecidas ao adapter como JSON original, com hashes e contratos reais, e consumidas pela CLI. Não são saídas de um extractor heurístico no runtime nem chamadas pagas. Mas **não são uma amostra independente de extração no produto ChatGPT**: a assistência conhece os casos. Replay mede integração e propriedades desses outputs, não generalização de uma LLM.

A sequência principal está em:

| Entrada | Próximo artifact | Mudança |
|---|---|---|
| [Sessão 1](../examples/session-01.md) | [Prompt 2](continuity/continuity/after-01/teacher-prompt.md) | Explicação de reformulações e correção seletiva persistem; dimensões emergentes são observadas; chunking de uma ocorrência fica fora. |
| [Sessão 2](../examples/session-02.md) | [Prompt 3](continuity/continuity/after-02/teacher-prompt.md) | Repetição imediata fica controlada; incerteza usada depois sem ajuda pede transferência; duração ainda difícil pede prática. |
| [Sessão 3](../examples/session-03.md) | [Prompt 4](continuity/continuity/after-03/teacher-prompt.md) | Duração melhora sem ajuda e também pede transferência; chunking ganha status inferido; rejeição de aulas de gramática vira diretiva explícita. |

O [audit do prompt 3](continuity/continuity/after-02/teacher-prompt.audit.json) mostra as tentativas controladas e a evidência espontânea separadas. O prompt 3 não contém wording-alvo de incerteza. O [histórico de collocation](continuity/practice/after-02/teacher-prompt.md) preserva o goal de design técnico e pede que a prática de outro assunto só apareça se combinar naturalmente com a agenda.

## Resultados e análise de falhas

Resultados executáveis: [result.json](continuity/result.json). Revisão de qualidade separada: [prompt-review.json](continuity/prompt-review.json), usando a [rubrica](../benchmark/prompt-rubric.md). O manifest de conteúdo executado está em [qualification.json](continuity/qualification.json).

| Medida no conjunto controlado | Resultado |
|---|---:|
| Conversas / turnos / históricos | 8 / 81 / 3 |
| Learner observations | 24: 6 dificuldades, 15 sucessos, 3 incertas |
| Sucessos por modo | 4 espontâneos, 3 guiados, 8 controlados |
| Teaching evidence / goals extraídos | 14 / 2 |
| Interações internas consumidas e auditadas | 68: 8 extrações, 24 reviews, 20 resoluções, 14 teaching reviews, 2 goal reviews |
| Retrieval de recorrência conhecida | 14/14 |
| Pares corretos unidos / false merges / false splits | 27 / 0 / 0 |
| Patterns prematuros / recorrências não promovidas | 0 / 0 |
| Prompts gerados | 8, de 2.509 a 3.540 caracteres; limite 8.000 |
| Preferências sem apoio no prompt | 0/14 itens emitidos = 0% neste conjunto |
| Falhas de continuidade / non-priming detectadas pelo gold | 0 / 0 |
| Testes executados | 45 passaram |

Os 14 itens de diretiva incluem repetições ao longo de prompts e não são amostras independentes. No estado final são sete instruções únicas: seis explícitas e uma hipótese inferida. As afirmações do professor sobre preferência por explicações/lectures não viraram preferências; os pedidos locais de repetição, wording e um único “why?” não viraram regras duráveis. A taxa 0/14 é uma checagem contra gold autoral, **não uma estimativa de hallucination rate de um modelo em conversas reais**.

Nenhum goal ou diretiva sustentada foi omitido por budget nos oito prompts; evidência tentativamente local e learning intentions adicionais foram omitidas por suporte insuficiente/limite de seleção, com audit. A campanha não marcou leak literal nos probes protegidos. A revisão qualitativa marcou relevância do último histórico adversarial como parcial: há várias dimensões e nenhum goal, e a escolha de duas observações ainda é heurística.

A suíte inclui parsing/rejeição, Unicode/CRLF/turnos repetidos, contracts de suporte, teacher-only preference, explícito versus inferido, goals, evidência positiva, prática versus recuperação, obsolescência, seleção por goals, budget, guard literal, imutabilidade, transações, replay pendente, idempotência, embeddings reais, JSON inválido, adapter HTTP simulado, fluxo completo pela CLI e replay do harness duas vezes. `pip check` e `git diff --check` também passaram. Os 68 hashes de respostas consumidas e seus parsed artifacts foram conferidos.

A revisão de prose avalia continuidade, fidelidade, relevância, estratégia, non-priming, liberdade conversacional, compactação e alinhamento a goals. É uma avaliação autoral dos documentos e fontes, não probabilidade objetiva nem observação de aulas reais.

Duas classes de RED foram encontradas durante desenvolvimento. Uma expectativa de teste apontava a linha 15 quando a fonte CRLF indicava a linha 13; corrigir o oracle preservou o locator real. Mais substantivamente, um replay do harness reutilizava o banco final e sobrescrevia snapshots iniciais com estado futuro. Isso causou duas falhas aparentes de continuidade e uma diretiva indevida no prompt anterior à sua evidência. Corrigi o harness para staging vazio em toda execução e acrescentei regressão que roda a campanha duas vezes e compara todos os prompts, além de verificar o primeiro prefixo vazio de patterns. Nenhuma resposta semântica foi reparada para mascarar essa falha.

O stress de budget também revelou que reservar espaço só para headings podia deixar goals longos ocupar o espaço da estratégia. A alocação simples foi ajustada para reservar parcelas para goals, diretivas e learning intentions. O teste mantém goal e prática, omite itens completos e verifica tamanho máximo. Isso mede coerência sob pressão, não otimização perfeita de relevância.

## Validação reutilizada e limites

A evidência anterior de embeddings explica a escolha de representação e top-k; ela não foi relabelada como um novo PASS. Os pesos e o código de pooling/fingerprint foram reutilizados. Os testes locais reais de vetores e semântica foram executados novamente. A antiga campanha IR congelada não foi reexecutada: seu contrato de report e outputs foram removidos; a campanha atual invalida a qualificação de ingestão e compiler e a substitui por conversas completas. Não houve ensaio externo pago, corpus real nem medição de ganho de aprendizagem.

Limitações: corpus pequeno e autoral; teacher behavior real não observado; forte dependência de interpretação e revisão pela LLM; embeddings estáticos; suporte em reutilização tardia pode ser ambíguo; formatos reais de exportação precisam corresponder ao contrato documentado; custo de várias interações manuais; resolução incremental sem merge/split retrospectivo automático; diretivas duráveis contraditórias não são reconciliadas automaticamente; goals extraídos podem reaparecer ao reprocessar; ranking de alinhamento lexical simples; budget pode omitir item relevante, com razão disponível no audit; guard de non-priming só cobre cópia literal, não todas as pistas possíveis; heurísticas temporais não foram calibradas em aprendizagem real.

## Prontidão para piloto pessoal

O produto pode começar um piloto pessoal supervisionado **agora**, com banco vazio e conversas reais no formato canônico. Antes de usar cada novo prompt nas primeiras sessões, revise o audit das observações e preferências, especialmente suporte, hipótese de português e pedidos locais. Cole somente o Markdown no professor externo; não acrescente as conversas antigas.

O piloto deve observar se o professor novo respeita as instruções sem reexplicação, segue goals, cria conversa interessante, não fornece respostas antes de tentativas úteis e deixa dificuldades antigas em recuperação quando surge produção espontânea. Exportar essas novas conversas fornece a próxima fonte. Registre falsas preferências, oportunidades perdidas, priming, prática irrelevante e evidência omitida. São medidas do loop real, ainda não demonstradas pela campanha sintética.

A implementação está pronta para esse experimento; uso sem revisão e promessa de eficácia não estão qualificados.
