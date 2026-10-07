# Relatório: o que o 1º turno de 2026 mudou na Câmara, no Senado e nos governos, e por quê

**Gerado em:** 07/out/2026, a partir de `resultados/RESUMO.json` (nenhum número foi escrito à mão). **Critérios gravados antes das análises:** commit `e372efb` ([`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md)). **Método e escopo:** [`docs/PLANO.md`](docs/PLANO.md). **Leitura e veredito da IA, em separado e marcados como opinião:** [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md). **Resumo curto:** [`RESUMO_SIMPLES.md`](RESUMO_SIMPLES.md).

> ⚠️ **Este documento diz o que os dados fecham. Não diz em quem cada pessoa votou, não afirma causa a partir de dado agregado, não julga intenção de ninguém e não prevê o 2º turno.**

## 0. O que o projeto não consegue dizer (no topo, com o mesmo destaque do resto)

1. **Casos e escândalos.** As séries de opinião capturadas (aprovação do governo, confiança no STF) têm poucos pontos por instituto. O teste pré-registrado de movimento da série perto de cada evento **não pôde ser rodado**. O que se mediu: o voto de cada deputado em duas votações de grande atenção contra o desempenho dele em 2026 (sem relação detectável) e a posição de candidatos ao Senado sobre o impeachment de ministros do STF (descritivo).
2. **Emendas parlamentares e gasto de campanha** não foram analisados (a prestação de contas final não existe).
3. **Pesquisas.** Só Datafolha e Quaest, só governador, só a última da véspera, com os números tirados de uma compilação de imprensa (conferida em SP contra outra fonte) e conferidos no registro do TSE. Não há 2022 para comparar, nem as pesquisas anteriores para separar mudança de última hora de erro. Pesquisas de Senado não foram coletadas.
4. **A régua de campo decide parte das respostas.** R1 põe MDB, PSD, PSDB e Podemos na direita (notas 7,0 a 7,2). R3 não é comparável entre 2022 e 2026: em 2026 o PL concorreu sem coligação.
5. **Falácia ecológica.** Toda relação com religião, renda, cor, idade ou Bolsa Família é entre municípios.
6. **2º turno.** Sete estados estão "em disputa".

## 1. Os resultados em dez linhas

1. **Câmara, 2022 → 2026:** PL 98 → 121 cadeiras (16,6% → 22,7% dos votos). Federação PT/PCdoB/PV 82 → 88.
2. **Campo (R1):** direita 380 → 388 cadeiras; esquerda 105 → 101; em votos, a direita 72,0% → 72,3%.
3. **Bancada de oposição ao governo (R2):** 102 → 131 cadeiras.
4. **Bônus de cadeiras da direita sobre os votos:** −0,1 → +2,1 → +3,3 pontos (2018, 2022, 2026).
5. **Reeleição de deputados:** 54,0% (eleitos de 2018 em 2022) → 56,1% (eleitos de 2022 em 2026).
6. **Senado:** PL 19 das 54 vagas; 28 das 81 cadeiras em 2027.
7. **Governos:** 20 decididos no 1º turno (17 de direita pela R1) e 7 em 2º turno.
8. **Geografia:** o perfil do município soma só 1,4 ponto de R² além da UF (20,1%).
9. **Abstenção:** 20,8% → 20,9%; com o comparecimento de 2022, o voto de direita seria 72,23% (real 72,32%).
10. **Pesquisas de governador:** o vencedor apareceu abaixo da urna em 26 de 32 pesquisas; nenhum teste por campo mostrou direção.

## 2. Dados e validação

| Item | Resultado |
|---|---|
| Resultado oficial 2026 (JSON por UF) | 513 vagas, 513 eleitos, por partido igual à tabela derivada |
| Votos por partido (nominais + legenda) | iguais ao JSON oficial até a segunda casa decimal para PL, PSD, Republicanos, MDB e Podemos |
| **Reprodução das 513 cadeiras** | **0 diferenças** com a regra da lei (80% do quociente para a lista e 20% para o candidato nas sobras); as alternativas deixam 11 a 16 cadeiras em outras mãos |
| Municípios casados TSE × IBGE | 5567 de 5571 (56 por semelhança de nome, listados) |
| Revisão adversarial programática | 15 de 15 checagens ([`docs/REVISAO_ADVERSARIAL.md`](docs/REVISAO_ADVERSARIAL.md)) |

Cada arquivo baixado tem sha256 em `dados/MANIFESTO.json` e `dados/MANIFESTO_IBGE.json`; cada página de imprensa, em `dados/CAPTURAS.csv`. Os boletins de urna de 2026 não foram usados nesta rodada: o resultado por candidato e município do TSE bastou, e o caminho por boletim (variante do decodificador do projeto `apuracao-eleicoes-2026`) ficou como segunda via **não executada** (declarado no PLANO §9).

**Base de 2022:** o arquivo atual do TSE (PL 98). Matérias da época deram PL 99; a reprodução com a regra da lei deixa 6 diferenças em 2022, compatível com a troca de sete mandatos por decisão do STF (fonte `conjur-sete-deputados`), não verificada cadeira a cadeira.

## 3. Câmara dos Deputados

### 3.1 Cadeiras por partido

| partido | 2006 | 2010 | 2014 | 2018 | 2022 | 2026 |
|---|---|---|---|---|---|---|
| PL | 23 | 41 | 34 | 33 | 98 | 121 |
| PT | 83 | 86 | 69 | 56 | 69 | 70 |
| UNIAO | 0 | 0 | 0 | 0 | 57 | 46 |
| PSD | 0 | 0 | 36 | 35 | 42 | 43 |
| REPUBLICANOS | 1 | 8 | 21 | 29 | 40 | 41 |
| PP | 41 | 44 | 38 | 37 | 47 | 41 |
| MDB | 89 | 78 | 65 | 34 | 41 | 36 |
| PODE | 0 | 0 | 4 | 11 | 14 | 27 |
| PSB | 27 | 35 | 34 | 32 | 15 | 15 |
| PSOL | 3 | 3 | 5 | 10 | 13 | 14 |
| PSDB | 66 | 54 | 54 | 30 | 13 | 11 |
| PCDOB | 13 | 15 | 10 | 9 | 7 | 11 |
| NOVO | 0 | 0 | 0 | 8 | 3 | 10 |
| PV | 13 | 13 | 8 | 4 | 6 | 7 |
| PDT | 24 | 27 | 20 | 28 | 16 | 6 |
| AVANTE | 1 | 3 | 1 | 7 | 7 | 5 |

Bancada na véspera da eleição (partido no último voto até 30/09/2026 entre os 520 deputados que votaram entre 1º/07 e 30/09) contra a eleita: [`resultados/a1_bancada_vespera_vs_eleita.csv`](resultados/a1_bancada_vespera_vs_eleita.csv).

### 3.2 Campo, três réguas

**R1 (escala de especialistas, cortes 4,0 e 6,0; sensibilidade ±0,5):**

| cortes | campo | cadeiras 2018 | cadeiras 2022 | cadeiras 2026 | pct_votos 2018 | pct_votos 2022 | pct_votos 2026 |
|---|---|---|---|---|---|---|---|
| 3,5-5,5 | centro | 73 | 44 | 29 | 14,3 | 10,5 | 7,7 |
| 3,5-5,5 | direita | 365 | 380 | 388 | 71,2 | 72,0 | 72,3 |
| 3,5-5,5 | esquerda | 75 | 89 | 95 | 14,5 | 17,4 | 18,8 |
| 4,0-6,0 | centro | 45 | 28 | 23 | 9,6 | 6,9 | 6,1 |
| 4,0-6,0 | direita | 365 | 380 | 388 | 71,2 | 72,0 | 72,3 |
| 4,0-6,0 | esquerda | 103 | 105 | 101 | 19,2 | 21,1 | 20,5 |
| 4,5-6,5 | centro | 43 | 25 | 15 | 10,0 | 7,9 | 4,1 |
| 4,5-6,5 | direita | 335 | 368 | 381 | 65,3 | 67,2 | 69,9 |
| 4,5-6,5 | esquerda | 135 | 120 | 116 | 24,7 | 24,9 | 24,9 |

**R2 (voto no plenário contra a orientação do governo, 2023 a 2026):** coorte eleita em 2022: governista 328, independente 58, oposição 102, sem classificação 25; coorte eleita em 2026: governista 355, independente 27, oposição 131 (deputado novo herda a classe mediana do partido). Com cortes de 65% e 45%: oposição 107 → 134.

**R3 (coligação formal na eleição presidencial):** [`resultados/a1_campo_r3.csv`](resultados/a1_campo_r3.csv). Em 2026 o PL concorreu sem coligação, e 40% das cadeiras ficam em "sem candidato presidencial"; **não é comparável com 2022**.

**Robustez:** o crescimento do PL vale nas três réguas onde ele é mensurável (cadeiras, votos, oposição ao governo). O crescimento do "campo de direita" **depende da régua**: +8 a +13 cadeiras e +0,3 a +2,7 ponto de voto pela R1, dependendo do corte; +29 cadeiras de oposição pela R2.

### 3.3 Votos, cadeiras e eficiência (D6)

| ano | campo | pct_votos | pct_cadeiras | cadeiras − votos (pp) |
|---|---|---|---|---|
| 2018 | esquerda | 19,1 | 20,1 | 0,93 |
| 2018 | centro | 9,6 | 8,8 | -0,84 |
| 2018 | direita | 71,2 | 71,2 | -0,09 |
| 2022 | esquerda | 21,1 | 20,5 | -0,60 |
| 2022 | centro | 6,9 | 5,5 | -1,41 |
| 2022 | direita | 72,0 | 74,1 | 2,06 |
| 2026 | esquerda | 20,5 | 19,7 | -0,79 |
| 2026 | centro | 6,1 | 4,5 | -1,58 |
| 2026 | direita | 72,3 | 75,6 | 3,31 |

Volatilidade (Pedersen) e número efetivo de partidos: [`resultados/a1_volatilidade.csv`](resultados/a1_volatilidade.csv), [`a1_nep.csv`](resultados/a1_nep.csv). A volatilidade de 2018→2022 é inflada pela formação do União Brasil (DEM + PSL), tratada como partido novo.

### 3.4 Puxadores (A5)

| candidato | uf | partido | votos | pct_da_lista | cadeiras_da_lista | cadeiras_sem_o_candidato | cadeiras_a_mais_pelo_candidato | votos_em_quocientes |
|---|---|---|---|---|---|---|---|---|
| Nikolas Ferreira | MG | PL | 3119318 | 68,4 | 21 | 11 | 10 | 14,5 |
| Lucas Pavanato | SP | PL | 3038438 | 48,4 | 19 | 14 | 5 | 9,0 |
| Erika Hilton | SP | PSOL | 1596472 | 53,1 | 6 | 4 | 2 | 4,7 |
| André Fernandes | CE | PL | 684372 | 62,8 | 4 | 2 | 2 | 2,7 |
| Sâmia Bomfim | SP | PSOL | 583107 | 19,4 | 6 | 5 | 1 | 1,7 |
| Julia Zanatta | SC | PL | 560223 | 37,3 | 7 | 5 | 2 | 2,1 |
| Ana Elisa | MG | PT | 524219 | 23,6 | 13 | 10 | 3 | 2,4 |
| Kim Kataguiri | SP | MISSÃO | 520071 | 81,2 | 1 | 0 | 1 | 1,5 |
| Tabata Amaral | SP | PSB | 476383 | 50,7 | 2 | 1 | 1 | 1,4 |
| Jeffrey Chiquini | PR | NOVO | 425399 | 45,9 | 4 | 3 | 1 | 2,0 |

"Cadeiras a mais" = cadeiras da lista com o candidato menos cadeiras da lista sem ele, **incluída a dele**. Sensibilidade à regra de sobras em 2026: [`resultados/a5_sensibilidade_regra_sobras_2026.csv`](resultados/a5_sensibilidade_regra_sobras_2026.csv) (a regra aplicada **não** é a mais favorável ao PL).

### 3.5 Renovação, incumbentes e nomes (A4, D5)

| de | para | campo_r1_na_eleicao_anterior | eleitos_na_eleicao_anterior | tentaram_de_novo | reeleitos | pct_reeleito_entre_os_que_tentaram | pct_reeleito_entre_todos |
|---|---|---|---|---|---|---|---|
| 2018 | 2022 | todos | 513 | 409 | 277 | 67,7 | 54,0 |
| 2018 | 2022 | centro | 45 | 36 | 16 | 44,4 | 35,6 |
| 2018 | 2022 | direita | 365 | 286 | 193 | 67,5 | 52,9 |
| 2018 | 2022 | esquerda | 103 | 87 | 68 | 78,2 | 66,0 |
| 2022 | 2026 | todos | 513 | 401 | 288 | 71,8 | 56,1 |
| 2022 | 2026 | centro | 28 | 22 | 13 | 59,1 | 46,4 |
| 2022 | 2026 | direita | 380 | 294 | 214 | 72,8 | 56,3 |
| 2022 | 2026 | esquerda | 105 | 85 | 61 | 71,8 | 58,1 |

43,5% dos eleitos de 2026 não estavam na Câmara na véspera (inclui ex-deputados que voltam e estreantes; a imprensa fala em 35% de primeiro mandato). Maiores quedas e altas de votos entre reeleitos: [`quedas`](resultados/a4_reeleitos_maiores_quedas_2022_2026.csv), [`altas`](resultados/a4_reeleitos_maiores_altas_2022_2026.csv). Os 30 mais votados de cada eleição e o que houve na seguinte: [`2018→2022`](resultados/a4_trinta_mais_votados_2018_e_o_que_houve_em_2022.csv), [`2022→2026`](resultados/a4_trinta_mais_votados_2022_e_o_que_houve_em_2026.csv).

## 4. Senado e governos

**Senado (A2):** PL 19, MDB 7, PT 6. Por R1: centro 4, direita 43, esquerda 7. Em 2018: centro 9, direita 39, esquerda 6. Composição a partir de fev/2027 (81): centro 5, direita 65, esquerda 10, sem classificação 1; PL 28. Eleitos que constavam na lista de apoio a Flávio (R3): 27 de 54. Limiares: [`resultados/RESUMO.json`](resultados/RESUMO.json) chave `a2.limiares`.

**Governos (A3):** [`resultados/a3_governos_por_campo_r1.csv`](resultados/a3_governos_por_campo_r1.csv) (decididos por campo em 2018, 2022 e 2026). Apoio declarado em 2026 (R3): Caiado 1, Flávio 10, Lula 5, sem apoio 4. Tabela por estado: [`resultados/a3_governos.csv`](resultados/a3_governos.csv).

**D5 (incumbentes além da Câmara):** senadores eleitos e reeleitos [`d5_reeleicao_senadores.csv`](resultados/d5_reeleicao_senadores.csv); governadores [`d5_governadores_que_tentaram_continuar.csv`](resultados/d5_governadores_que_tentaram_continuar.csv).

**D8 (STF no Senado):** eleitos por posição declarada: a favor 28, contra 6, fora da lista da Gazeta 3, outra (neutro, reforma ou outra) 3, sem posição 14 (lista da Gazeta do Povo, fonte única, 213 candidatos lidos, 196 casados com o TSE).

## 5. Geografia e abstenção (bloco B)

| cargo | periodo | municipios | swing_direita_medio_ponderado_pp | desvio_padrao_ponderado_pp | pct_municipios_com_swing_positivo | pct_eleitorado_em_municipios_com_swing_positivo |
|---|---|---|---|---|---|---|
| 6 | 2022->2026 | 5567 | 0,1 | 10,4 | 54,3 | 42,9 |
| 6 | 2018->2022 (placebo de estabilidade) | 5567 | 0,7 | 11,2 | 60,0 | 47,3 |
| 3 | 2022->2026 | 5567 | 3,2 | 22,7 | 54,2 | 48,0 |
| 3 | 2018->2022 (placebo de estabilidade) | 5567 | 7,6 | 20,0 | 67,1 | 57,1 |
| 5 | 2018->2026 | 5567 | 1,7 | 18,2 | 61,5 | 43,3 |
| 5 | 2010->2018 | 5564 | 9,5 | 23,8 | 68,3 | 76,0 |

(cargo 6 = deputado federal, 3 = governador, 5 = senador; swing = variação da % de voto de direita pela R1, média ponderada pelo eleitorado.)

**Perfil do município (deputado federal, dentro da UF):** diferença entre o efeito de 2026 e o de 2018→2022, em pontos por desvio-padrão:

| variavel | coef_placebo_pp_por_desvio_padrao | coef_2026_menos_placebo_pp | ic95_diferenca_baixo | ic95_diferenca_alto | acompanha_mais_que_antes |
|---|---|---|---|---|---|
| pct_urbana | -2,68 | 3,42 | 1,5 | 5,3 | True |
| pct_pretos_pardos | -0,83 | 1,57 | -0,4 | 3,5 | False |
| pct_60mais | 0,44 | -0,14 | -1,8 | 1,6 | False |
| pct_superior | -1,43 | 1,43 | 0,5 | 2,4 | True |
| pct_evangelicos | -0,71 | 1,60 | 0,1 | 3,1 | True |
| pct_catolicos | 2,27 | -3,00 | -4,5 | -1,5 | True |
| log_pib_pc | -2,31 | 2,79 | 1,2 | 4,4 | True |
| agro_share | 2,17 | -1,96 | -4,0 | 0,1 | False |
| bf_por_100hab | 2,42 | -3,56 | -6,1 | -1,0 | True |

A UF explica 20,1% da variação do swing; o perfil acrescenta 1,4 ponto. **Abstenção:**

| ano | abstencao_pct | comparecimento_pct |
|---|---|---|
| 2006 | 16,7 | 83,3 |
| 2010 | 18,1 | 81,9 |
| 2014 | 19,3 | 80,7 |
| 2018 | 20,2 | 79,8 |
| 2022 | 20,8 | 79,2 |
| 2026 | 20,9 | 79,1 |

Contrafactual com o comparecimento de 2022: diferença de −0,09 ponto. Variação de abstenção × swing de direita: +0,30 ponto por ponto, IC95 −0,06 a +0,65.

**Arrasto:**

| ano | cargo | correlacao_media_ponderada_por_uf | ufs |
|---|---|---|---|
| 2018 | deputado federal | 0,25 | 26 |
| 2018 | governador | 0,51 | 26 |
| 2018 | senador | 0,53 | 26 |
| 2022 | deputado federal | 0,31 | 26 |
| 2022 | governador | 0,55 | 26 |
| 2026 | deputado federal | 0,39 | 26 |
| 2026 | governador | 0,60 | 25 |
| 2026 | senador | 0,70 | 26 |

Mapa: [`resultados/figuras/video/08_mapa_variacao_voto_direita_deputado_federal.png`](resultados/figuras/video/08_mapa_variacao_voto_direita_deputado_federal.png).

## 6. As pesquisas (bloco C)

32 pesquisas (Datafolha 6, Quaest 26) em 27 disputas; 30 com registro no TSE na janela de 26/set a 03/out. Erro do vencedor: média com sinal −3,2 ponto; em valor absoluto 4,2; erro da margem em valor absoluto 7,2. Fora da margem declarada (2 pontos quando o plano amostral não informa): proporção 25 de 32, diferença entre os dois primeiros 21 de 32.

| erro_margem_abs | erro_vencedor_abs | erro_vencedor_medio_com_sinal | instituto | n | vencedor_certo |
|---|---|---|---|---|---|
| 7,2 | 5,2 | -3,54 | Datafolha | 6 | 5 |
| 7,2 | 4,0 | -3,17 | Quaest | 26 | 24 |

**Direção do erro:** margem subestimada (corrida mais apertada que a urna) em 23 das 32 pesquisas e na maioria das pesquisas de 20 das 27 disputas (p = 0,02). Por campo: R3 6 disputas, subestimou Flávio em 2 (p = 0,69); R1 7 disputas, em 2 (p = 0,45); exploratório (definido depois de ver o resultado) 13 disputas, em 6 (p = 1,00). Tabelas: [`c2_erro_por_pesquisa.csv`](resultados/c2_erro_por_pesquisa.csv), [`c4_direcao_*.csv`](resultados/).

**Critério do pré-registro para "erro sistemático"** exigia 4 condições; só a primeira (teste do sinal) pôde ser rodada, e **não** foi atendida por campo. Por isso o texto usa "corridas mais apertadas na pesquisa que na urna, para quem ganhou, independente do campo" e não "erro sistemático por campo".

## 7. Por quê: o placar das hipóteses

| id | nome | status | confianca | onde |
|---|---|---|---|---|
| H1 | Virada de opinião para a direita | inconsistente | média | Câmara: voto de direita 72,0% → 72,3%; governo e Senado: subida menor que a anterior |
| H2 | Referendo sobre o governo | não testável | baixa | só há uma aprovação capturada (Quaest, jul/2026, 48 × 47); sem série |
| H3 | Anti-incumbência (cansaço de quem está no cargo) | inconsistente | média | deputados reeleitos: 56,1% contra 54,0% em 2022 |
| H4 | Estrutura e eficiência (listas, federações, puxadores) | consistente | alta | bônus de cadeiras da direita: −0,1 → +2,1 → +3,3 pp; puxadores |
| H5 | Máquina (emendas, fundo, mandato) | não testável | baixa | emendas não foram analisadas nesta rodada |
| H6 | Casos e escândalos (Master, STF, INSS, condenação) | não testável | baixa | voto na PEC da Blindagem sem relação com a eleição (−2,4 pp); séries de opinião insuficientes |
| H7 | Composição do eleitorado (perfil e abstenção) | inconsistente | média | perfil soma 1,4 ponto de R² além da UF; abstenção 20,8% → 20,9% |
| H8 | Arrasto do candidato à Presidência | consistente | alta | correlação com o voto de direita: senador 0,53 → 0,70, deputado 0,31 → 0,39 |

Voto no plenário × desempenho (D3):

| votacao | desfecho | n | grupos | coef_sim | ic95_baixo | ic95_alto | p | p_bh_v1_v4 |
|---|---|---|---|---|---|---|---|---|
| V1 PEC 3/2021 (blindagem), 1o turno, 16/09/2025 | eleito em 2026 | 85 | 23 | -0,02 | -0,15 | 0,10 | 0,70 | 0,70 |
| V1 PEC 3/2021 (blindagem), 1o turno, 16/09/2025 | log(votos 2026 / votos 2022) | 84 | 23 | 0,10 | -0,28 | 0,47 | 0,61 | 0,61 |
| V4 Emendas do Senado ao PLP 177/2023 (numero de deputados), 25/06/2025 | eleito em 2026 | 55 | 15 | 0,20 | -0,04 | 0,44 | 0,09 | 0,19 |
| V4 Emendas do Senado ao PLP 177/2023 (numero de deputados), 25/06/2025 | log(votos 2026 / votos 2022) | 55 | 15 | 0,18 | -0,13 | 0,50 | 0,25 | 0,50 |
| P placebo: 'Mantido o texto', 16/12/2025 (423 x 23) | eleito em 2026 | 13 | 5 |  |  |  |  |  |
| P placebo: 'Mantido o texto', 16/12/2025 (423 x 23) | log(votos 2026 / votos 2022) | 13 | 5 |  |  |  |  |  |

Descrição das votações:

| votacao | votaram_sim_nao | sim | nao | disputaram_dep_federal_2026 | pct_eleitos_entre_os_que_disputaram_sim | pct_eleitos_entre_os_que_disputaram_nao |
|---|---|---|---|---|---|---|
| V1 PEC 3/2021 (blindagem), 1o turno, 16/09/2025 | 487 | 353 | 134 | 398 | 67,8 | 67,0 |
| V4 Emendas do Senado ao PLP 177/2023 (numero de deputados), 25/06/2025 | 397 | 361 | 36 | 324 | 68,3 | 71,0 |
| P placebo: 'Mantido o texto', 16/12/2025 (423 x 23) | 446 | 423 | 23 | 367 | 68,3 | 47,1 |

A leitura da IA arena por arena e o veredito, marcados como opinião: [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md).

## 8. Desvios do pré-registro

Todos estão na §15 do [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md), com data e a declaração de se foram feitos antes ou depois de ver o resultado. Os que mais pesam: (a) D2 e D1 rodaram só como captura de dados, sem o teste de movimento da série; (b) C ficou em Datafolha e Quaest para governador, com fonte única de compilação; (c) o Moran dos resíduos não foi calculado (efeito fixo de UF e erro por UF no lugar); (d) a lista de "notáveis" ficou nos critérios (c), (d) e (e).

## 9. Como reproduzir

[`docs/REPLICAR.md`](docs/REPLICAR.md). Resumo: `python ferramentas/coletar.py ...`, `coletar-ibge.py`, `derivar-votos.py`, depois `analise-1` a `analise-9` e `revisao-adversarial.py`. Commit dos dados de entrada: `dados/MANIFESTO*.json`.
