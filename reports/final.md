# Thoth — entrega e avaliação do learner model aberto

**Recomendação: iniciar um piloto pessoal supervisionado e exploratório.** O loop funciona e passou pelos critérios previamente congelados do experimento sintético. Isso autoriza experimentar com revisão humana de observations e memberships; não demonstra precisão em conversas reais, domínio linguístico ou ganho de aprendizado. Não recomendo uso sem revisão.

## Mudança entregue

A implementação atual foi substituída diretamente. Foram removidos a taxonomia de oito constructions, aliases/canonicalização, agregação por skills fechadas, adapters de texto/offline orientados à taxonomia, testes e benchmarks anteriores, mecanismos de qualificação/versionamento anteriores, documentação anterior e bancos/artifacts locais derivados. O Git guarda o código anterior. Não há migration, caminhos alternativos de comportamento, feature flags ou compatibilidade entre gerações.

O runtime tem 12 módulos Python pequenos: contratos, prompts, LLM, provenance, embeddings, SQLite, pipeline, estado, artifacts, CLI e avaliação. Não há ontologia de inglês nem IDs globais de habilidade. Os exemplos linguísticos específicos ficam exclusivamente em fixtures e relatórios experimentais. ManualChatGPT e OpenAI são providers para o mesmo loop e contrato, não caminhos conceituais distintos.

## Modelo conceitual e vertical slice

Uma `Observation` contém a produção atribuída ao aluno, trecho da fonte e localização nesse relatório, intenção comunicativa, descrição livre da dimensão de produção e comportamento naquela ocorrência. Também registra modo de produção, performance, tipo de evidência, sugestões e uma hipótese opcional. O tipo de evidência distingue uso, correção, self-correction e oportunidade. O schema rejeita campos adicionais e exige que oportunidades/self-repairs tenham performance incerta.

O extractor escolhe evidências úteis para speaking, incluindo sucessos. Ignora ortografia, pontuação, STT, fillers e preferências estilísticas sem valor pedagógico. Um reviewer separado confronta cada proposta com o contexto. Uma rejeição fica no audit da sessão; incerteza permanece evidência isolada. Sugestões da LLM são explicitamente distintas de correções feitas na aula.

Os trechos são localizáveis no relatório, tolerando diferenças de whitespace. Não há reconstrução de áudio. A fala precisa aparecer no trecho atribuído ao aluno; uma alternativa pedagógica sugerida não precisa ter sido pronunciada. O relatório é uma fonte já interpretada, com seus próprios limites.

O pipeline só faz commit quando todas as interações da sessão terminam. Pendência/JSON inválido não grava meia sessão. Reingestão do mesmo relatório/data é idempotente; a ordem deve ser cronológica. Sources e observations são imutáveis. Requests, respostas consumidas, hashes SHA-256, parsed JSON, candidatos e justificativas ficam auditáveis.

Além do benchmark de agrupamento, executei a **CLI de ingestão completa sobre três relatórios**, começando com SQLite vazio. Foram 3 extrações, 6 revisões e 5 decisões semânticas realmente respondidas por este agente. Depois da primeira aula: 2 observations e nenhum Pattern. Depois da segunda: 2 patterns emergentes. Depois da terceira: 6 observations em 2 patterns, incluindo um sucesso espontâneo no mesmo grupo das dificuldades. O brief foi gerado a partir desses memberships.

Arquivos desse exercício: [sessões de entrada](../examples/), [learner state](ingest-demo/artifacts/learner-state.md), [lesson brief](ingest-demo/artifacts/next-lesson.md) e [intercâmbios](ingest-demo/exchange/). São relatórios sintéticos e artifacts realmente gerados pelo software, não dados de um aluno real.

## Embeddings e armazenamento

Escolha: **spaCy `en_core_web_md` 3.8.0**, vetores locais de palavras de 300 dimensões, média de tokens conhecidos não pontuados, normalização L2. Hash dos pesos: `1686d0286e854fd2274b7c8d86adb7f60905d5b089de02446045df941e05bcd5`.

A representação embutida é `learning_dimension + communicative_intent`. A dimensão é normalizada, sem nomes, datas, diagnóstico ou assunto incidental. O comportamento e a performance ficam fora do embedding para que dificuldade e sucesso da mesma capacidade possam se recuperar mutuamente. A frase bruta só é usada na ablação experimental. Há um único vetor por observation.

Inicialmente tentei um pequeno encoder contextual BGE. Os hosts dos pesos estavam inacessíveis nesta rede; o modelo oficial spaCy pôde ser instalado pelo GitHub e reproduzido em um ambiente limpo. Escolhi essa implementação simples e mensurável, em vez de introduzir um serviço remoto. **Ela não tem a expressividade contextual de um sentence transformer.** Os resultados abaixo mostram que a separação das similaridades é imperfeita.

SQLite contém apenas `sessions`, `observations` e `patterns`. A observation guarda seu vetor como BLOB float32 little-endian, texto pedagógico, modelo dos pesos, root de membership e resolução. Não há necessidade de tabelas separadas para embedding ou evidence: o membership está na própria linha da observation. Patterns guardam label, descrição e contextos conversacionais sintetizados.

A busca usa NumPy para comparar exatamente os poucos vetores. Não usei sqlite-vec porque, nessa escala, ele adicionaria uma dependência/extensão sem mudar a hipótese testada. Banco e intercâmbios são copiáveis; artifacts são regeneráveis. Embeddings são calculados sem rede após a instalação. Os pesos e dependências são fixados na instalação.

## Retrieval e resolução

A busca considera grupos provisórios e Patterns já promovidos. Ordena cada grupo por seu exemplar mais próximo e recupera até **3 grupos**. O resolver recebe as evidências de todos os membros desses candidatos, não só a frase mais próxima.

As decisões são:

- `same_pattern`: mesma capacidade de produção; associa a exatamente um candidato;
- `related_but_different`: relação relevante, mas capacidade distinta; mantém um root separado;
- `new_pattern`: nenhuma associação adequada; mantém observation/root separado;
- `insufficient_evidence`: informação insuficiente; mantém evidência isolada.

`new_pattern` não materializa automaticamente um Pattern. O código valida que o ID escolhido veio dos candidatos e que a associação aponta para evidência existente. Não há merge automático de dois grupos, nem uso de cosine como probability. Não há corte de distância no runtime: o experimento mostrou sobreposição real, e cortar candidatos poderia esconder a associação correta.

Uma comparação pode agrupar várias ocorrências no mesmo dia sem gerar Pattern. A política materializa um Pattern com evidência revisada em **pelo menos duas datas independentes** e uma associação semântica que forneça sua síntese. Esse requisito reduz repetição artificial concentrada em uma aula. Datas são uma aproximação conservadora de independência; não garantem independência estatística.

## Learner state e próxima aula

O estado deriva das observations e memberships, por Pattern. O sistema calcula contagens por modo/performance, sessões, datas, oportunidades, self-repairs e IDs de evidência. O modelo escreve a descrição linguística; não inventa números nem prioridade.

Política escolhida na calibração:

- **Coletar:** padrão emergente ou pouco observado; inclui oportunidades e sucesso apenas guiado.
- **Praticar:** ao menos 3 datas de evidência e dificuldade espontânea em ao menos 2 das 3 últimas datas com tentativas espontâneas, salvo recuperação recente.
- **Recuperação/força recente:** sucessos espontâneos nas 2 últimas datas com tentativas, sem dificuldade nessas duas datas. Dificuldades históricas continuam no pack.

O horizonte recente é por datas de tentativas, não por dias do calendário. Não calculamos mastery, probabilidade de acerto ou score de proficiência. A política temporal foi escolhida contra uma rubrica conservadora autoral; não foi validada por um estudo de eficácia educacional. Duas datas bastam para um padrão emergente, mas não para uma prioridade automática.

O brief seleciona até duas prioridades por bloco e usa contextos conversacionais sintetizados para elicitar o propósito naturalmente. Por exemplo, pedir ajuda a um colega desconhecido, discutir detalhes ainda incertos de um plano ou explicar uma rotina. Não prescreve a expressão que o aluno deve produzir. Formas sugeridas ficam nos evidence packs para feedback posterior. Patterns fora desse limite continuam visíveis no estado completo.

## Composição e limites do benchmark

| Conjunto | Sessões | Observations | Papel |
|---|---:|---:|---|
| Development | 4 | 25 | Exercitar implementação e corrigir classes de falha |
| Calibration | 4 | 27 | Parafrasear descrições, escolher retrieval e política temporal |
| Holdout | 4 | 31 | Verificar implementação congelada, com realizações e capacidades adicionais |
| Review adversarial | — | 12 propostas | Medir utilidade do verifier contra erros de interpretação |
| Ingestão completa adicional | 3 | 6 aceitas | Exercitar o loop real da CLI desde relatório e banco vazio |

O gold de grupos fica em arquivos separados. Nenhum grupo gold, label gold ou resposta esperada é enviado ao resolver. O benchmark principal usa **IR pedagógica sintética já revisada**, para separar problemas de retrieval/resolução dos problemas de extração. Portanto, seus resultados não qualificam a precisão do extractor sobre texto real. O exercício de ingestão completa mostra funcionamento, com cobertura pequena e sem métrica independente de extração.

Development/calibration incluem incerteza, collocations de reuniões e decisões, duração de estados, registro, oportunidades de arrependimento, sucesso controlado, acordo isolado, contexto ambíguo e alternativas regionais legítimas. Há também criação física de um modelo, com palavras parecidas mas dimensão distinta, e self-repair relacionado à incerteza.

O holdout inclui collocations de ingestão de medicamentos, collocations de erros, preço alto com possível influência portuguesa, tom de pedidos a pares desconhecidos, duração de casamento/posse, sucesso espontâneo, alternativas válidas de arrependimento, evidência controlada, um grupo concentrado em um dia, self-repair, transporte físico com `take` e uso causal legítimo de `since`. Não se limita à gramática. As descrições foram parafraseadas para reduzir matching de frases idênticas; o grupo concentrado em um dia conserva descrições iguais e é deliberadamente um caso fácil de grouping, mas um teste de não promoção.

**A mesma pessoa/modelo autorou os casos, o gold e as respostas semânticas.** Eu respondi os prompts efetivamente produzidos pelo adapter, sem regra automatizada que substituísse a decisão linguística e sem chamadas pagas. Não houve cegamento independente: o autor conhece os casos. Os outputs foram JSON estruturado produzido por este agente, não uma amostra independente de conversas copy/paste no produto ChatGPT. A robustez contra JSON inválido está nos testes, não numa estimativa de taxa de erro de formatação do modelo.

A identidade declarada é `Codex / modelo desta conversa`; o nome exato do modelo não foi identificado automaticamente. O código não assegura que outro modelo disponível na assinatura ou na API tenha o mesmo comportamento.

## Development, correções e calibração

No development, a decisão semântica agrupou os 25 pares positivos esperados, sem false merge/split. Houve correções gerais de implementação: serialização de IDs, replay de benchmark a partir de estado limpo para evitar retrieval de evidência futura, validação de candidatos/membership, conservação de hashes das respostas e contagens separadas de oportunidades/modos. O holdout foi aberto apenas depois dessas mudanças, da calibração e do teste de ingestão completo.

Uma calibração inicial com descrições muito semelhantes pareceu fácil demais. Antes do freeze, substituí as descrições principais da calibration por paráfrases e acrescentei capacidades/realizações novas ao conjunto reservado. Na calibração final:

| Retrieval sequencial por exemplares | @1 | @2 | @3 | Primeiro k com todos os 15 acertos |
|---|---:|---:|---:|---:|
| Representação pedagógica | 12/15 | 14/15 | 15/15 | 3 |
| Frase bruta | 13/15 | 14/15 | 14/15 | 6 |

A representação pedagógica não ganhou em @1 na calibration. Ela encontrou todos os casos com menor conjunto de candidatos. Isso sustenta um uso limitado de k=3, não uma superioridade universal do fingerprint.

Distribuições de cosine na calibration:

| Pares | N | Mínimo | Mediana | Máximo |
|---|---:|---:|---:|---:|
| Mesmo grupo | 25 | 0,853 | 0,933 | 1,000 |
| Grupos diferentes | 300 | 0,696 | 0,835 | 0,918 |

Há sobreposição: alguns pares diferentes são mais próximos que pares iguais. Distribuições completas e percentis estão em [calibration.json](calibration.json). Nenhum threshold de similarity foi instalado no runtime.

Nos ensaios temporais, exigir 2 datas para promoção cobriu a recorrência gold sem promoção prematura; exigir 3 perdeu o grupo com duas datas. A prioridade em 3 datas teve 0 discrepâncias contra a rubrica temporal autoral; 2 e 4 datas tiveram 8 cada. Isso justifica a política inicial como heurística conservadora; o gold não é evidência de ganho real de aprendizagem.

O resolver da calibration, com k=3, acertou 27/27 decisões do pipeline, das quais 25 foram chamadas efetivas à LLM. Selecionou corretamente o grupo de todos os 18 candidatos escolhidos para associação/relação. Houve 25 pares corretamente unidos, zero merges/splits incorretos e 6 Patterns.

## Holdout congelado

O registro [freeze.json](../benchmark/freeze.json) guarda hashes de todos os módulos runtime, política, dependências, datasets e resultado de calibração, mais pesos e identidade declarada da LLM. Os critérios fixados antes da abertura foram zero false merges, zero promoção prematura, zero recorrência perdida, retrieval >=95% e pairwise recall >=90%. **Não alterei o runtime, parâmetros, casos ou respostas depois de abrir o holdout.** Os gates primários passaram.

| Medida primária | Resultado do holdout |
|---|---:|
| Recorrência correta entre candidatos recuperados | 17/17 = 100% |
| Pares do mesmo grupo corretamente unidos | 28 |
| False merge pairs | 0 |
| False split pairs | 0 |
| Pairwise precision / recall | 100% / 100% |
| Patterns prematuros | 0 |
| Recorrências gold não promovidas | 0 |
| Decisões de resolução corretas, pipeline completo | 29/31 = 93,5% |
| Patterns materializados | 7 |

Pairwise precision pergunta se o agrupamento contaminou habilidades diferentes: `pares corretos unidos / todos os pares unidos`. Pairwise recall pergunta se manifestações da mesma habilidade foram separadas: `pares corretos unidos / todos os pares gold iguais`. Singletons não ajudam a elevar recall. Promover ruído é medido separadamente, porque um singleton não cria pares. Recorrência perdida significa um grupo gold presente em várias datas sem Pattern promovido correspondente.

Os pares não são observações estatisticamente independentes; percentuais perfeitos nesse conjunto pequeno não permitem inferir uma taxa de erro populacional próxima de zero.

As duas discrepâncias foram:

- `I did a mistake...`: o gold previa relação com outro grupo de collocation; ele não estava entre os três candidatos, e o resolver escolheu `new_pattern`.
- `Take that chair...`: o gold previa relação com o uso de `take` em medicamentos; esse grupo também não foi recuperado, e o resolver escolheu `new_pattern`.

Ambos permaneceram separados; nenhum contaminou memberships. **Retrieval de relações foi apenas 1/3**, embora retrieval de mesmo padrão tenha sido 17/17. A política atual é boa neste conjunto para reencontrar recorrências; não é um detector confiável de toda relação linguística. Não aumentei k em resposta ao holdout.

O [diagnóstico posterior](holdout/diagnostics.json) separa esses casos sem alterar a métrica primária: houve 29 chamadas efetivas ao resolver. Nas 27 com o candidato gold necessário disponível, as 27 categorias foram corretas; os 18 candidatos selecionados para associação/relação pertenciam ao grupo gold correspondente. Isso é análise condicional posterior, não um substituto para os 29/31 primários. O campo `conditional` do resultado original condiciona só a disponibilidade de mesmo grupo; o diagnóstico explicita também a disponibilidade das relações.

A ablação posterior da representação no holdout, sem mudar k congelado, encontrou 17/17 com fingerprint pedagógico e 16/17 com frase bruta em @3. Em @1: 17/17 contra 13/17. São exemplares sequenciais; o runtime completo usa um candidato por grupo. A ablação não constitui uma avaliação com clusters formados por dois runtimes alternativos.

## Embedding sozinho: ablação que falhou

Antes do freeze, escolhi para a baseline experimental o menor corte acima de todos os pares diferentes da calibration: cosine `0,9183867573738099`. Ele não é probability. Foi uma classificação independente de pares, sem transitividade, para testar se similaridade seria suficiente.

| Baseline somente cosine | Pares corretos | False merges | False splits | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Calibration | 18 | 0 | 7 | 100% | 72,0% |
| Holdout, mesmo corte | 19 | 7 | 9 | 73,1% | 67,9% |

O corte perdeu recorrências na calibration e não generalizou a separação de grupos no holdout. No holdout, pares diferentes chegaram a 0,935. Esse resultado justifica manter a decisão semântica e não converter distância em membership. A baseline existe apenas na avaliação, sem caminho alternativo no produto.

## Verifier: ablação e decisão

No conjunto adversarial, 12 propostas foram deliberadamente classificadas como dificuldades antes da revisão. O gold tinha 4 dificuldades sustentadas, 6 rejeições e 2 casos incertos. O reviewer acertou 12/12, reduziu falsas dificuldades de 8 para 0 e não perdeu as 4 válidas.

Os casos cobrem suspeita legítima com `doubts`, pedido natural de café, British English, detalhes de STT, alternativa apenas estilística, atribuição desconhecida, registro inadequado em contexto explícito e diagnóstico indevido de tradução mental/avoidance. [Respostas e resultado](review/review-ablation.json).

Decisão: manter uma única revisão por proposta. Ela mostrou valor nessa tarefa controlada e protege precisamente as interpretações que preocupam o produto. O resultado tem forte viés autoral, casos pequenos e alguns fáceis. **Não prova melhora independente do reviewer em conversas reais**, que precisa ser medida no piloto. Não há reviewer adicional do resolver nem loops automáticos de reparo.

## Ruído, positivos e packs inspecionados

O erro isolado `I am agree...` não virou Pattern nem prioridade. Três ocorrências de `suggested me to...` no mesmo dia foram agrupadas provisoriamente, mas não promovidas. O caso ambíguo com `doubt`, alternativas regionais, transporte físico, self-repair e `since` causal não foram juntados a dificuldades apenas pela sobreposição de palavras.

Inspecionei manualmente os packs de incerteza, collocations de erros, preço alto e arrependimento, incluindo justificativas, fontes, membership e status. Exemplos efetivamente gerados:

1. [Natural expression of personal uncertainty](holdout/artifacts/patterns/PAT-978494d19600.md): **4 observations em 4 sessões; 2 dificuldades e 2 sucessos espontâneos; recovery**. A descrição diz que a formulação é compatível com construções portuguesas, sem afirmar acesso ao processo mental.
2. [Conventional verb combinations for mistakes](holdout/artifacts/patterns/PAT-99a09f69e93e.md): **2 observations em 2 sessões; collect**. Não foi fundido ao grupo de medicamentos nem virou prioridade por apenas duas ocorrências.
3. [Spontaneous expression of past regret](holdout/artifacts/patterns/PAT-b2ff8bdfd9de.md): **2 oportunidades incertas e 1 sucesso controlado em 3 sessões; collect**. Nenhuma falha espontânea inventada. As paráfrases legítimas não são chamadas de erros, e non-use não prova avoidance.
4. [Natural emphasis of high prices](holdout/artifacts/patterns/PAT-d11cbbe7f8d5.md): **2 dificuldades e 1 sucesso espontâneo em 3 sessões; practice**. `Extremely expensive` conta como sucesso; não há exigência de idiom. A hipótese portuguesa é cautelosa. Uma única melhora ainda não satisfaz o critério de recuperação.
5. [Pack do loop completo de ingestão](ingest-demo/artifacts/patterns/PAT-d11f3afe31ab.md): a evidência foi extraída e revisada através do adapter, com report source, sugestões e razões de agrupamento. Não depende da IR pronta do benchmark.

O [brief do holdout](holdout/artifacts/next-lesson.md) prioriza medicamentos e pedidos a colegas; coleta collocations de erros e expressão de arrependimento; observa recuperação de duração e incerteza. Preços continuam em practice no estado completo, mas ficam fora das duas prioridades do brief. O relatório da sessão e o audit preservam as evidências omitidas do resumo curto.

## Verificação e limites práticos

- **21 testes passaram**, incluindo embeddings locais reais, schema aberto/estrito, provenance Unicode, transações, imutabilidade, import manual, preservação de JSON inválido, não promoção em uma data, evidência positiva e recovery, validação de IDs e isolamento do holdout antes do freeze.
- Uma instalação separada, criada do zero com `scripts/setup.sh`, passou pelos mesmos 21 testes e por `pip check`.
- O adapter OpenAI teve apenas teste de contrato com HTTP simulado; não foi qualificado contra API paga.
- Respostas e hashes do holdout e da calibration foram auditados; nenhuma resposta foi reparada semanticamente para melhorar o score.
- O banco pessoal não contém fixtures nem perfis: começa com 0 sessões/observations/patterns. Os bancos de experimento são locais e excluídos do Git; inputs, respostas e packs são entregues para reprodução.

Limitações observadas: retrieval de relações incompleto; embedding estático com grande sobreposição entre habilidades; gold IR mais limpa que relatórios reais; casos pequenos, compartilhamento de autoria e pouca diversidade; ausência de qualificação quantitativa de extração; dependência de contexto/intenção fornecidos no relatório; consumo manual de várias interações por sessão; grupos anteriores só recebem novas evidências, sem mecanismo automático de merge/split retrospectivo; não há comando de edição de uma associação já persistida. Um erro confirmado exige reconstrução de um banco separado a partir das fontes.

## Como iniciar o piloto

Comece com banco vazio e seus relatórios reais. Nas primeiras sessões, revise cada observação e associação antes de aceitar o learner model como orientação. Use o brief para criar oportunidades naturais e registre também usos corretos. Observe se os patterns são específicos, recorrentes e acionáveis; se as aulas ficam mais úteis; e se o mesmo propósito passa a ser produzido naturalmente em contextos novos.

Registre associações inadequadas, padrões fragmentados, falsas dificuldades e evidências que o extractor perdeu. São essas medidas em dados reais que decidirão os próximos ajustes. Um resultado ruim exige corrigir a classe de problema, avaliar em development/calibration e preparar novos casos reservados. Estes resultados não justificam tuning por caso nem promessa de benefício adaptativo já comprovado.

**Conclusão operacional:** o Thoth entregue pode começar esse piloto supervisionado. A hipótese de descobrir um learner model aberto passou pelo teste técnico controlado, com separação conservadora e positive evidence. A precisão em conversas reais e o ganho de aprendizado continuam em aberto.
