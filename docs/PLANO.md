# Plano e método: o que o 1º turno de 2026 mudou no Congresso e nos governos, e por quê

**Escrito em:** 07/out/2026, manhã. **Estado:** ✅ **executado em 07/out/2026** (ver §15). O resultado está em [`../RELATORIO.md`](../RELATORIO.md).
**Critérios exatos de cada teste:** [`PRE_REGISTRO.md`](PRE_REGISTRO.md). **Endereços e o que existe:** [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md). **Doutrina:** [`.cursor/rules/congresso-fundamentos.mdc`](../.cursor/rules/congresso-fundamentos.mdc).

---

## 0. Em uma frase

Medir o que o 1º turno de 2026 mudou na **Câmara**, no **Senado** e nos **governos estaduais**, contra 2018 e 2022 (e a série desde 2002 onde o dado é leve), explicar **por que** com hipóteses concorrentes testadas contra dado público, medir **onde as pesquisas erraram e se o erro tem direção**, e fechar cada arena com **um veredito da IA**, marcado como opinião e sustentado por comparação. Presidente fica fora, a não ser como variável de controle.

## 1. O pedido e as decisões do autor

Pedido (07/out): *"o grande impacto que as eleições de 2026 teve no Senado e na Câmara dos Deputados. E nos governos"*, *"não vai falar ainda sobre presidência"*, *"colhendo vereditos da inteligência artificial"*, *"analisar o histórico dos últimos anos"*, *"o escândalo no STF, escândalo do Banco Master, escândalo no INSS"*, *"conectar isso com informações geográficas, do IBGE"*, *"onde as pesquisas erraram por muito ou erraram por pouco [...] onde a abstenção justificaria [...] se [...] tem uma indicação de tendenciosismo"*, *"não é um projeto baseado em achismo, é um projeto baseado em fatos"*.

Decisões dele no mesmo dia:

| Decisão | O que ele disse |
|---|---|
| Repositório **novo e público**, como o do vídeo 5; nome escolhido pela IA | *"o repositório ele vai ficar público, o nome você pode decidir"* |
| O caso do STF é o de **ministros como Alexandre de Moraes ligados ao Banco Master**, mais **a condenação de Bolsonaro** e outros temas polêmicos | *"relacionado à ministros como Alexandre de Moraes, entre outros, e está ligados ao Banco Master. E outros temas polêmicos, como a condenação do ex-presidente Bolsonaro"* |
| **O escopo é decisão da IA**, pelo que faz sentido | *"isso eu deixaria ao seu encargo de decidir"* |
| **O vídeo sai hoje**: dado de até 07/out | *"O vídeo vai sair hoje. Então, é com os dados de até hoje"* |
| Comparar principalmente com **2018 e 2022** | *"Principalmente a de 2018 e 2022"* |

## 2. O que a sondagem de 07/out achou (o que muda o projeto)

1. 🔑 **O resultado oficial por UF e por município traz cada candidato a deputado** com votos, situação (*Eleito por QP*, *Eleito por média*, *Suplente*), partido, federação e o **quociente eleitoral** da UF (`resultados.tse.jus.br/oficial/ele2026/6259/dados/...`). As 27 UFs somam **513** eleitos.
2. 🔑 **O TSE já publicou** `votacao_candidato_munzona_2026` (316 MB, 05/out), `detalhe_votacao_munzona_2026` (07/out), `consulta_cand_2026` (07/out), o **registro das pesquisas** de 2026 (06/out) e o **perfil do eleitorado por seção**. ⚠️ **Não publicou ainda** o perfil de comparecimento e abstenção de 2026 (404).
3. ⚠️ **Os derivados do vídeo 5 só têm presidente, governador e senador.** O voto de deputado por seção exige decodificar de novo os boletins brutos (11 GB, já com hash), com a variante que guarda o número do candidato.
4. 🔑 **API e arquivos anuais da Câmara** (`votacoesVotos-AAAA.csv`, `votacoesOrientacoes-AAAA.csv`) respondem, e trazem cada voto de cada deputado e a orientação do governo. É a base da régua R2 e do teste D3.
5. 🔑 **Dois fatos do pedido foram corrigidos pelo dado** (§3), e um terceiro mudou de tamanho.

## 3. Fatos de partida, conferidos no resultado oficial em 07/out

Lido no JSON oficial por UF (sondagem, ainda sem script versionado; a Fase 3 refaz):

| Fato | Dado |
|---|---|
| Cadeiras da Câmara | **513** (a ampliação para 531 não valeu para 2027) |
| Maiores bancadas | PL **121** · federação PT/PCdoB/PV **88** (PT 70, PCdoB 11, PV 7) · federação União/PP **87** (União 46, PP 41) · PSD 43 · Republicanos 41 · MDB 36 · Podemos 27 |
| Comparação com a eleição de 2022 (a conferir no arquivo de 2022) | PL **99 → 121** · federação do PT **80 → 88** · PT **68 → 70** |
| Mais votados | Nikolas Ferreira (PL-MG) **3.119.318** · Lucas Pavanato (PL-SP) **3.038.438** · Erika Hilton (PSOL-SP) **1.596.472** |
| Senado (54 vagas) | PL **19** · MDB 7 · PT 6 · PP, PSB, União e Novo 3 cada · Republicanos, PSDB, PSD e Podemos 2 cada · Rede e PDT 1 |
| Governos | **20** eleitos no 1º turno, **7** estados em 2º turno (AC, AM, DF, ES, RJ, RN, TO) |
| Marina Silva | **não disputou a Câmara**; disputou o Senado por SP e não se elegeu (matérias: ~7,86 milhões de votos) |
| André Janones | **reeleito** (matérias: ~78.780 votos, contra 238.967 em 2022) |

**O que isso já obriga o método a medir antes de concluir:** se o PL cresceu e a federação do PT também cresceu, o ganho do PL veio de **outros partidos**. A pergunta A1 mede de onde (por partido, por campo nas três réguas e contra a bancada na véspera).

---

## 4. O que o projeto não promete

- ⛔ **Não diz em quem cada pessoa votou.** Tudo que liga perfil a voto é entre municípios ou seções (falácia ecológica, dita em voz alta).
- ⛔ **Não prova causa de dado agregado.** *"O caso X fez o resultado"* não sai daqui. Onde o desenho chega mais perto de causa (D3), o texto diz por quê e diz o limite.
- ⛔ **Não julga intenção** de instituto, de ministro, de candidato ou de eleitor.
- ⛔ **Não prevê o 2º turno.** Governador que foi a 2º turno é *"em disputa"*.
- ⛔ **Não testa um lado só.** Todo teste roda para todos os campos.

## 5. A régua de campo: quem é direita, centro e esquerda

A frase *"a direita ganhou"* depende de onde se põe União, PP, PSD, MDB e Republicanos. O campo se mede de **três formas independentes**, e o critério de cada uma está no pré-registro:

| Régua | O que mede | Fonte | Unidade |
|---|---|---|---|
| **R1 · Ideologia do partido** | posição do partido numa escala de especialistas | levantamento acadêmico publicado, capturado com trecho (candidato principal: Bolognesi, Ribeiro e Codato, *Dados*, 2023) | partido |
| **R2 · Plenário** | % dos votos de cada deputado e de cada partido iguais à orientação do governo, 2023 a 2026 | arquivos anuais da Câmara | deputado e partido |
| **R3 · Apoio declarado** | apoio declarado a candidato a presidente no 1º turno | captura com fonte (base: `dados/apoios.csv` e `senado-apoio-flavio.csv` do vídeo 5) | candidato |

Centro existe como categoria. Resultado **robusto** = vale nas três réguas. Se só vale em uma, o texto diz *"depende de como se conta"*. Partido novo ou sem nota numa régua fica *"sem classificação"* nela, sem chute.

---

## 6. As perguntas

O critério exato de cada uma (o que confirma, o que desmente, o que fica sem resposta) mora no `PRE_REGISTRO.md`.

### Bloco A · O que mudou

| Nº | Pergunta | Dado |
|---|---|---|
| **A1** | Cadeiras por partido, federação e campo (R1, R2, R3) na **Câmara**: contra a eleição de 2022, contra a de 2018, e contra a **bancada na véspera** (depois da janela partidária). A mudança de 2026 é maior ou menor que a de 2018 (a do PSL) e a de 2022? Série de cadeiras 2002 a 2026. Votos contra cadeiras | JSON oficial 2026 · `votacao_candidato_munzona` e `consulta_cand` 2002 a 2022 · histórico de partido da API da Câmara |
| **A2** | **Senado:** quantas das 54 vagas trocaram de campo contra quem ocupava a vaga; a Casa de 81 em fev/2027 por campo; cada campo contra **41** (maioria absoluta), **49** (3/5, PEC) e **54** (2/3) | JSON oficial · API do Senado (mandatos até 2031) |
| **A3** | **Governos:** eleitos no 1º turno, 2º turnos, reeleições, estados que trocaram de campo (R3), contra 2018 e 2022 | JSON oficial · TSE 2018 e 2022 |
| **A4** | **Renovação e nomes:** taxa de reeleição por campo, contra 2018 e 2022; **derrotados notáveis** pelo critério simétrico do pré-registro; reeleitos que perderam muito voto | TSE · fontes de cargo |
| **A5** | **Puxadores:** concentração do voto por partido; quantas cadeiras o voto de cada grande puxador garantiu (redistribuição **sem** ele); Nikolas 2026 contra Nikolas 2022, Eduardo Bolsonaro 2018 e os recordes anteriores | reprodução própria do quociente e das sobras |

### Bloco B · Onde e entre quem

| Nº | Pergunta | Dado |
|---|---|---|
| **B1** | **Variação municipal 2022 → 2026** do voto por campo, cargo a cargo, e 2018 → 2022 como régua de quanto um município costuma mexer. Mapa | TSE por município · malha do IBGE |
| **B2** | A variação acompanha o perfil do município: renda, escolaridade, **religião**, cor ou raça, idade, urbanização (Censo 2022), **Bolsa Família** por habitante, PIB per capita e peso da agropecuária? | IBGE (SIDRA) · MDS · TSE |
| **B3** | **Abstenção:** onde subiu ou caiu contra 2018 e 2022; relação com o voto; estimativa por faixa de idade e escolaridade a partir do perfil do eleitorado por seção | `detalhe_votacao_munzona` · boletins (aptos e comparecimento) · `perfil_eleitor_secao` |
| **B4** | **Arrasto:** o voto em Câmara, Senado e governador acompanha o de presidente, município a município, mais ou menos que em 2018 e 2022 (amplia a P6 do vídeo 5) | TSE e boletins |

### Bloco C · As pesquisas

| Nº | Pergunta | Dado |
|---|---|---|
| **C1** | Coleta das pesquisas de **governador e senador** dos 27 estados divulgadas na última semana (e a anterior do mesmo instituto, para a tendência), em 2026 e em 2022 | registro no TSE (instituto, contratante, pagante, amostra, campo, margem) + resultado do relatório do instituto ou de duas reportagens independentes, com captura |
| **C2** | **Quanto erraram:** erro no vencedor, erro na **margem entre os dois primeiros** e erro médio; por instituto, por método e por contratante; quantos ficaram fora da margem declarada | C1 + resultado oficial |
| **C3** | **Por que erraram:** cada erro dividido em mudança de última hora (tendência do próprio instituto), abstenção (B3), indecisos e voto branco ou nulo, e o que sobra | C1 + B3 |
| **C4** | **O erro tem direção?** O que sobra puxa para o mesmo campo em mais disputas do que o acaso daria, em vários institutos, e mais que em 2022? | C1 a C3 |

**A régua do texto:** *"erro sistemático na mesma direção"*, *"maior que o de 2022"*, *"não explicado por abstenção nem por mudança de última hora"*. ⛔ *"Tendenciosa"*, *"manipulada"*, *"comprada"* não entram como conclusão.

### Bloco D · Por quê: hipóteses concorrentes

Cada explicação diz antes **o que o dado mostraria se ela valesse**. Várias podem valer ao mesmo tempo.

| Hipótese | Se ela vale, o dado mostra… | Testes |
|---|---|---|
| **H1 · Virada de opinião** | variação parecida em municípios de perfis diferentes, em todos os cargos; auto-posicionamento ideológico mudando nas séries de opinião | B1, B2, D1 |
| **H2 · Referendo sobre o governo** | variação acompanhando a aprovação; candidatos ligados ao governo perdendo mais | D1, B4, D5 |
| **H3 · Anti-incumbência** | incumbentes **de todos os campos** perdendo | D5 |
| **H4 · Estrutura e eficiência** | ganho de cadeiras maior que o de votos; peso dos puxadores | A1, A5, D6 |
| **H5 · Máquina** | quem mandou mais emenda a um município ganhou mais voto lá, em todos os campos | D4 (escopo condicional, §8) |
| **H6 · Casos e escândalos** | séries de opinião se mexendo perto dos eventos; quem votou de certo jeito em votações de grande atenção indo pior ou melhor que colegas do mesmo partido e estado; o tema STF aparecendo no Senado | D1, D2, D3, D8 |
| **H7 · Composição** | variação explicada pelo perfil do município e pela abstenção por grupo | B2, B3 |
| **H8 · Arrasto do presidenciável** | Câmara, Senado e governo andando com o presidente, município a município | B4 |

| Nº | Teste | Dado |
|---|---|---|
| **D1** | **Séries de opinião** de 2024 a 2026, mesmo instituto ao longo do tempo: aprovação do governo, **confiança no STF**, e o que mais houver em série (auto-posicionamento, desejo de mudança) | relatórios de Quaest, Datafolha, AtlasIntel, CNT/MDA, capturados |
| **D2** | **Linha do tempo** com fonte primária e duas reportagens independentes, com os eventos dos **dois lados** listados no pré-registro (§7 de lá), entre eles Banco Master e as ligações com ministros do STF, a condenação de Bolsonaro, o INSS, o tarifaço, a PEC da Blindagem e a anistia. Para cada evento, se as séries da D1 se moveram na janela pré-registrada, acima da variação normal da série | capturas · D1 |
| **D3** | **Exposição no plenário:** deputados que tentaram a reeleição, comparados pelo voto em votações nominais de grande atenção, dentro do mesmo partido e estado, controlando o voto de 2022; e uma votação quase unânime como **placebo** | arquivos da Câmara · TSE |
| **D4** | **Emendas** por autor e município contra o voto do autor no município | Portal da Transparência · TSE |
| **D5** | **Incumbentes** de todos os cargos e campos: quem tentou, quem ficou | TSE · API da Câmara e do Senado |
| **D6** | **Votos contra cadeiras** por campo; candidatos por lista; federações | TSE |
| **D8** | **O tema STF no Senado:** posição declarada dos candidatos ao Senado sobre impeachment de ministro do STF (mapeamentos de imprensa, duas fontes), quantos eleitos têm essa posição, e a conta contra os limiares do Senado | capturas · A2 |

### Bloco E · O veredito da IA

Por arena: **Câmara · Senado · Governos · Pesquisas · O que o eleitor sinalizou**. Para cada uma, o placar das hipóteses (*consistente*, *inconsistente*, *não testável*), o veredito em 2 a 4 frases marcado como opinião, o **grau de confiança** (alto, médio, baixo) e a comparação que sustenta. Mora em `docs/LEITURA_DA_IA.md`, gerado depois da revisão adversarial, no formato do vídeo 5.

O veredito de *"o que o eleitor sinalizou"* só sai do que H1, H2 e H3 permitirem dizer **juntas**: se incumbentes de todos os lados caem, é cansaço de quem está no cargo; se só um lado cai, é campo; se o auto-posicionamento não mudou, *"virada ideológica"* não se sustenta.

---

## 7. Estatística: o que usar, o que evitar e por quê

| Técnica | Para quê | Cuidado registrado |
|---|---|---|
| Volatilidade de Pedersen (cadeiras e votos) e número efetivo de partidos | tamanho da mudança em A1, contra 2018 e 2022 | federação conta como uma lista na distribuição, mas o partido é a unidade da série |
| Reprodução do quociente eleitoral, das sobras e da regra de desempenho individual | validação (513 de 513) e contrafactual dos puxadores (A5) | a regra de sobras de 2026 se confirma **pelo dado**: a variante que reproduz 513 de 513 é a aplicada, e a fonte legal é capturada |
| Diferença municipal (*swing*) com efeito fixo de UF | B1, B2 | falácia ecológica; erro padrão por UF; autocorrelação espacial medida (Moran) |
| Regressão de desempenho de incumbente com efeito fixo de partido × UF | D3 | seleção: quem vota de um jeito pode diferir de quem vota de outro; placebo obrigatório; Benjamini-Hochberg entre as votações testadas |
| Teste binomial do sinal do erro e média do erro com sinal por instituto | C4 | disputas não são independentes dentro de um instituto; a unidade de teste é a disputa, e o efeito de instituto é medido à parte |
| Comparação com a margem declarada, com e sem efeito de desenho (1,5) | C2 | a margem declarada vale para proporção, não para diferença entre dois candidatos (a da diferença é ~2×) |
| Faixa de variação normal de uma série de opinião | D2 | o evento só "move" a série se a mudança passa da maior variação entre duas medições seguidas fora das janelas de evento |
| ⛔ Google Trends | | normalizado contra o próprio pico, séries não comparáveis. Fora |
| ⛔ Inferência de causa a partir de correlação de 27 estados | economia | força estatística baixa. Fora do escopo (§8) |

## 8. O escopo, decidido pela IA, e o porquê

O vídeo sai hoje. O vídeo 5 levou **~4 h de execução** (coleta, validação, as 8 perguntas, relatório e revisão, das 23h03 às 02h57) e **~5 h** de segunda validação, gráficos e leitura da IA. Este projeto pergunta mais coisas, mas **não tem a coleta pesada** (os boletins já existem) e o dado de 2026 já saiu pronto em CSV. O escopo foi cortado para caber numa execução do mesmo tamanho, com o que mais muda a história na frente.

| Nível | O que entra | Por quê |
|---|---|---|
| ✅ **Núcleo (obrigatório)** | A1 a A5 · B1, B2, B4 · B3 por município · C1 a C4 (2026 e 2022) · D1 (aprovação e confiança no STF) · D2 · D3 · D5 · D6 · D8 · veredito | é o que responde *"o que mudou"*, *"onde"*, *"as pesquisas"* e *"por quê"* com dado que já existe; D3 é o teste mais forte do bloco D e custa pouco (arquivos anuais da Câmara) |
| 🟡 **Se o núcleo fechar com tempo** | B3 por faixa de idade e escolaridade · C com as pesquisas de 2018 · D4 (emendas) | B3 por grupo e D4 exigem cruzamento pesado (perfil por seção; casamento de nome de autor de emenda com candidato) |
| ⛔ **Fora, e declarado** | assembleias estaduais · presidente como assunto · economia por estado · gasto de campanha · redes sociais | assembleias dobram o volume sem mudar a história; economia em 27 estados não tem força; a **prestação de contas final ainda não existe** (só a parcial); rede social não é reproduzível |

Ordem de execução dentro do núcleo, para que um corte de tempo derrube o menos importante: **A (o que mudou) → C (pesquisas) → B → D → E**.

## 9. Validação cruzada: cada número por dois caminhos

| Número | Caminho 1 | Caminho 2 | Caminho 3 |
|---|---|---|---|
| Quem foi eleito deputado | situação no JSON oficial | **reprodução própria do quociente e das sobras: 513 de 513** | `consulta_cand_2026` |
| Voto por candidato e município, 2026 | `votacao_candidato_munzona_2026` | JSON oficial por município | soma dos boletins (variante do decodificador), nas UFs que couberem no tempo |
| Voto por partido e seção, 2026 | variante do decodificador | Parquet do vídeo 5 (presidente, governador e senador) como prova de que a variante lê igual | |
| Cadeiras de 2018 e 2022 | `consulta_cand` | resultado publicado pela Câmara na posse | |
| Bancada na véspera | histórico de partido na API da Câmara | levantamento de imprensa da janela partidária | |
| Resultado de uma pesquisa | relatório do instituto | registro no TSE (amostra, campo, margem) + reportagem | agregador público |
| Fato da linha do tempo | ato oficial | duas reportagens independentes | |

A reprodução das 513 cadeiras é a porta: **se ela não fecha, o resto não começa.** Duas matérias com o mesmo parágrafo contam como uma fonte. Número de resumo automático de página não é fonte: só o texto bruto capturado.

## 10. Onde a IA entra, e como ela é controlada

| A IA faz | A IA não faz |
|---|---|
| escreve e roda a coleta, a validação e as análises | ⛔ número de memória: todo número sai de script sobre arquivo com hash |
| captura fontes e copia o trecho | ⛔ afirma fato de campanha sem duas fontes |
| redige o relatório a partir das tabelas | ⛔ escreve conclusão que a tabela não sustenta |
| dá a leitura e o veredito **como opinião marcada** | ⛔ muda critério depois de ver o resultado sem a entrada na §9 do pré-registro |
| revisa o próprio trabalho em três passadas adversariais | ⛔ usa adjetivo sem a medida que o justifica |

**As três passadas da revisão adversarial**, separadas e registradas em `docs/REVISAO_ADVERSARIAL.md`: (1) a leitura que mais incomodaria um leitor de direita, procurando furo; (2) a que mais incomodaria um leitor de esquerda; (3) um auditor de método e linguagem (travas, adjetivos, causa sem desenho, **teste do espelho**: *com os lados trocados, a frase seria escrita igual?*). O que sobrevive às três entra.

## 11. As fases

| Fase | Saída | Porta de saída |
|---|---|---|
| **0 · Pré-registro em commit** | `PRE_REGISTRO.md` gravado antes de qualquer análise | o hash do commit entra no relatório |
| **1 · Coleta** | tudo com sha256 em `dados/MANIFESTO.json`; bruto fora do git; capturas em `dados/CAPTURAS.csv` | manifesto completo |
| **2 · Validação** | 513 de 513 · votos por dois caminhos · pesquisas por dois caminhos · réguas R1, R2 e R3 montadas | se 513 não fecha, para e registra |
| **3 · Análise** | A → C → B → D, cada resultado em `resultados/` e no `RESUMO.json` | |
| **4 · Revisão adversarial** | as três passadas | 100% dos achados tratados |
| **5 · Relatório** | `RELATORIO.md` e `RESUMO_SIMPLES.md` gerados do `RESUMO.json` · `LEITURA_DA_IA.md` com os vereditos · gráficos 1920×1080 e mapas em `resultados/figuras/video/` · `CORRECOES.md` | |

## 12. Reprodutibilidade

- **O dado de 2026 por seção vem do repositório do vídeo 5, sem cópia:** `dados/FONTE_APURACAO.json` fixa o caminho, o commit (`740fe519`) e o sha256 do `MANIFESTO.json` de lá (`af668b84…`). A execução confere esse hash antes de ler qualquer boletim.
- Todo arquivo baixado aqui entra no `dados/MANIFESTO.json` com sha256.
- Aleatoriedade com semente fixa e declarada. Versões de biblioteca fixadas em `requirements.txt`.
- Erro achado depois da publicação vai para `docs/CORRECOES.md` com o antes e o depois.

## 13. Travas do assunto

As do projeto de checagem e do vídeo 5 valem aqui: ⛔ nada de contar quantas vezes alguém faltou com a verdade · ⛔ nada de recomendação de voto · ⛔ nada de julgar intenção · ⛔ nada de testar um lado só. E três a mais, porque aqui se explica, não se audita:

1. **Causa só com desenho que separa causa.** A régua: *"coincide com"*, *"consistente com"*, *"os dados não separam"*, *"não explicado por"*.
2. **Investigação não é condenação.** Pessoa citada em investigação aparece como *"citada"*, *"investigada"* ou *"denunciada"*, exatamente como o ato oficial diz, com a resposta dela quando houver. Condenação só com decisão.
3. **Adjetivo só medido** (*histórica*, *onda*, *recorde*), com a série que mostra o tamanho.

## 14. Riscos conhecidos

| Risco | O que o método faz |
|---|---|
| a régua de campo decide a conclusão | três réguas; robusto só se valer nas três |
| o autor e a IA já viram as manchetes | o pré-registro declara o que foi visto e registra antes o que ainda não foi calculado |
| pesquisa sem relatório público acessível | entra com duas reportagens independentes, marcada; sem duas fontes, sai, e a contagem do que saiu vai para o relatório |
| ID de votação nominal da Câmara diferente do esperado | a lista do pré-registro é por tema e data; votação que não existir como nominal sai, registrada |
| tempo | ordem A → C → B → D → E; o que não couber fica marcado como não feito, sem ser citado |
| regra de sobras mal entendida | a variante que reproduz 513 de 513 é a aplicada; a outra entra como contrafactual |

---

## 15. O que foi executado, e o que não foi (07/out/2026)

O pré-registro foi gravado em commit antes de qualquer análise (`e372efb`). Os desvios estão na §15 do [`PRE_REGISTRO.md`](PRE_REGISTRO.md), com a declaração de antes ou depois de ver o resultado.

| Parte | Estado | Observação |
|---|---|---|
| **A1** cadeiras por partido e campo (R1, R2, R3), véspera, volatilidade, NEP | ✅ | série 2006 a 2026 |
| **A2** Senado | ✅ | composição de fev/2027 com a API do Senado |
| **A3** governos | ✅ | 20 decididos, 7 em disputa |
| **A4** renovação e nomes | 🟡 | critérios (c), (d), (e); (a) e (b) não executados |
| **A5** puxadores e regra de sobras | ✅ | |
| **B1, B2, B4** geografia, perfil, arrasto | ✅ | Moran não calculado |
| **B3** abstenção | 🟡 | por município; por idade e escolaridade não executado |
| **C1 a C4** pesquisas | 🟡 | Datafolha e Quaest, governador, 2026; sem 2022, sem Senado, sem decomposição de tendência |
| **D1, D2** séries de opinião e linha do tempo | 🟡 | só captura; teste de movimento **não rodado** |
| **D3** voto no plenário × desempenho | 🟡 | duas votações e um placebo que não pôde ser estimado |
| **D4** emendas e gasto de campanha | ⛔ | fora, declarado |
| **D5, D6** incumbentes e votos × cadeiras | ✅ | |
| **D8** STF no Senado | 🟡 | fonte única |
| **E** veredito | ✅ | [`LEITURA_DA_IA.md`](LEITURA_DA_IA.md), depois das três passadas ([`REVISAO_ADVERSARIAL.md`](REVISAO_ADVERSARIAL.md)) |
| Segunda via pelos boletins de urna | ⛔ | não executada; o JSON oficial e a soma por partido do TSE serviram de segunda via (checagens A2, A5, A7) |
