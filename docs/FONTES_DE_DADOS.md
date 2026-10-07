# Fontes de dados: endereços, o que existe e o que não existe

**Sondagem:** 07/out/2026, entre 10h40 e 11h20. Cada linha diz se foi conferida (✅), se não existe ainda (❌) ou se fica para a Fase 1 (⬜).

---

## 1. Resultado oficial de 2026 (JSON do TSE)

Base: `https://resultados.tse.jus.br/oficial/ele2026/6259/dados/`

| Caminho | Status | O que traz |
|---|---|---|
| `<uf>/<uf>-c0006-e006259-u.json` | ✅ 27 UFs (SP 275 KB) | **deputado federal** na UF: cada candidato com `vap` (votos), `st` (*Eleito por QP*, *Eleito por média*, *Suplente*, *Não eleito*), `sqcand`, partido, federação (`nfed`), votos de legenda; `qe` (quociente eleitoral) e `nv` (vagas) no bloco do cargo; branco, nulo e válidos em `v` |
| `<uf>/<uf>-c0007-e006259-u.json` | ✅ (SP) | deputado estadual (fora do escopo) |
| `<uf>/<uf>-c0003-e006259-u.json` | ✅ 27 UFs | governador |
| `<uf>/<uf>-c0005-e006259-u.json` | ✅ 27 UFs | senador |
| `<uf>/<uf><mun>-c0006-e006259-u.json` | ✅ (AC 01066, 29 KB) | o mesmo **por município** |

⚠️ O arquivo vem em UTF-8 na maioria e com acento quebrado em alguns leitores: ler os bytes e decodificar explicitamente.

**Conferência da sondagem:** soma dos *Eleito* nas 27 UFs = **513**.

## 2. Dados abertos do TSE (CDN)

Base: `https://cdn.tse.jus.br/estatistica/sead/odsele/`

| Arquivo | Status | Observação |
|---|---|---|
| `votacao_candidato_munzona/votacao_candidato_munzona_2026.zip` | ✅ 316 MB, 05/out/2026 | voto por candidato, município e zona, todos os cargos |
| `votacao_candidato_munzona/votacao_candidato_munzona_2022.zip` | ✅ 642 MB, 04/out/2026 | idem 2022 (e 2018, 2014, … no mesmo padrão, ⬜) |
| `detalhe_votacao_munzona/detalhe_votacao_munzona_2026.zip` | ✅ 2,5 MB, 07/out/2026 | aptos, comparecimento, abstenção, branco, nulo por município e zona |
| `consulta_cand/consulta_cand_2026.zip` | ✅ 3,2 MB, 07/out/2026 | candidatos: partido, coligação, situação, idade, gênero, cor, ocupação |
| `pesquisa_eleitoral/pesquisa_eleitoral_2026.zip` | ✅ 5,9 MB, 06/out/2026 | **registro** das pesquisas (instituto, UF, cargo, amostra, campo, margem, valor). ⚠️ não traz o resultado da pesquisa |
| `pesquisa_eleitoral/pesquisa_contratante_2026.zip` e `pesquisa_pagante_2026.zip` | ✅ | quem contratou e quem pagou |
| `perfil_eleitor_secao/perfil_eleitor_secao_2026_<UF>.zip` | ✅ (AC 9,3 MB, 17/jul/2026) | idade, escolaridade, gênero por seção |
| `perfil_comparecimento_abstencao/perfil_comparecimento_abstencao_2026.zip` | ❌ 404 em 07/out | B3 por faixa vem do perfil por seção cruzado com o comparecimento do boletim |
| `prestacao_de_contas_eleitorais_candidatos_2026` | ⚠️ parcial (22/set) | gasto de campanha fora do escopo (§8 do plano) |
| pesquisas, candidatos e votação de 2018 e 2022 | ⬜ mesmo padrão de nome | |

Portal CKAN: `https://dadosabertos.tse.jus.br/api/3/action/package_search` (em 07/out, 12 conjuntos com "2026").

## 3. Boletins de urna de 2026 (do repositório do vídeo 5)

| Item | Valor |
|---|---|
| Repositório | `github.com/Gabriel-Alexandre/apuracao-eleicoes-2026` (público) · local `Downloads/repositorios/apuracao-eleicoes-2026` |
| Commit fixado | `740fe519140b04199de8668bd3a69591cc71e6f8` |
| sha256 do `dados/MANIFESTO.json` de lá | `af668b8422b96cea876771b2e145e2f1d20abaddc09ae66dc4bf8b48e395a6ec` |
| Bruto | `dados/brutos/<uf>.sqlite` (11 GB, 28 bancos) |
| Derivados prontos | `dados/derivados/uf/<uf>-votos.parquet` (**só cargos 1, 3 e 5**) e `<uf>-secoes.parquet` (aptos, comparecimento, hora) · `dados/derivados/historico/<ano>-<turno>-<uf>-*.parquet` (2018 e 2022) |
| Decodificador | `apuracao/bu.py`: para deputado, zera o número do candidato e agrega por partido. A variante deste projeto guarda o número |

Tudo isso está em `dados/FONTE_APURACAO.json`, e a execução confere o hash antes de ler.

## 4. Câmara dos Deputados

| Endereço | Status | Uso |
|---|---|---|
| `https://dadosabertos.camara.leg.br/arquivos/votacoesVotos/csv/votacoesVotos-<ano>.csv` | ✅ (2025) | voto de cada deputado em cada votação nominal (R2, D3) |
| `https://dadosabertos.camara.leg.br/arquivos/votacoesOrientacoes/csv/votacoesOrientacoes-<ano>.csv` | ✅ (2025) | orientação do Governo e das bancadas (R2) |
| `https://dadosabertos.camara.leg.br/api/v2/deputados` e `/deputados/{id}/historico` | ✅ | bancada na véspera, histórico de partido |

## 5. Senado Federal

| Endereço | Status | Uso |
|---|---|---|
| `https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json` | ✅ | composição atual e mandatos |

## 6. IBGE, MDS e CGU

| Fonte | Status | Uso |
|---|---|---|
| `https://apisidra.ibge.gov.br/values/t/<tabela>/...` | ✅ responde | Censo 2022 (tabelas de renda, escolaridade, religião, cor, idade, situação do domicílio a fixar na Fase 1), PIB municipal |
| Malha municipal do IBGE | ⬜ | mapas |
| Bolsa Família por município (MDS / Portal da Transparência) | ⬜ | B2 |
| `https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO` | ✅ redireciona para o arquivo | D4 (nível condicional) |

## 7. Pesquisas, séries de opinião e linha do tempo (capturas)

Tudo aqui entra em `dados/CAPTURAS.csv` com URL, data, sha256 do corpo e o trecho copiado. ⛔ Número de resumo automático não entra.

| Assunto | Pontos de partida achados na sondagem (07/out) |
|---|---|
| Pesquisas de governador de 2018 e 2022 (emenda 23) | base do ranking de institutos do [Pindograma](https://github.com/pindograma/ranking_de_institutos) (`data/polls/late_polls_2012_2014_2016_2018.csv` e `late_polls_2022.csv`, commit `c04d197`; pesquisas com registro no TSE), capturada em `pindograma-late-polls-2012-2018` e `pindograma-late-polls-2022`. O repositório não declara licença: a cópia bruta fica fora do git e vai a tabela extraída (`resultados/c5_pesquisas_governador_2018_2022_extraidas.csv`). Conferência contra a imprensa da época em `resultados/c5_conferencia_segunda_fonte.csv` |
| Erro de pesquisa em 2026 | [Gazeta do Povo: quais pesquisas acertaram e erraram para governador de SP](https://gazetadopovo.com.br/eleicoes/2026/sao-paulo-2026/quais-pesquisas-acertaram-e-erraram-para-governador-de-sao-paulo) · [O Povo: Datafolha e Quaest para governador](https://www.opovo.com.br/noticias/politica/eleicoes/2026/10/04/resultados-das-pesquisas-datafolha-e-quaest-para-governador.html) · páginas da Gazeta do Povo por pesquisa e UF |
| Aprovação do governo | [Poder360: Quaest, aprovação 48 × 47](https://www.poder360.com.br/poder-eleicoes-2026/governo-lula-e-aprovado-por-48-e-desaprovado-por-47-diz-quaest/) · relatórios da Genial/Quaest e do Datafolha |
| Confiança no STF | [Poder360: desconfiança no STF em 43%, Datafolha](https://www.poder360.com.br/poder-pesquisas/desconfianca-no-stf-atinge-43-maior-nivel-desde-2012/) · [Metrópoles: Quaest, confiança de 50% para 43%](https://www.metropoles.com/brasil/confianca-no-stf-cai-de-50-para-43-em-7-meses-diz-quaest) · Quaest de set/2026 (desconfiança em 56%) |
| Banco Master e STF | [Wikipedia: Banco Master scandal](https://en.wikipedia.org/wiki/Banco_Master_scandal) (só como índice de fontes primárias) · [Gazeta do Povo: Moraes vota sob crise no STF por relação com Vorcaro](https://gazetadopovo.com.br/eleicoes/2026/moraes-vota-em-colegio-de-sao-paulo-sob-crise-no-stf-por-relacao-com-vorcaro) · [Gazeta do Povo: Master, emendas, INSS e STF](https://gazetadopovo.com.br/eleicoes/2026/master-emendas-rio-de-janeiro-inss-stf-dita-ritmo-casos-explosivos-impacto-eleitoral) |
| Condenação de Bolsonaro | [Metrópoles: STF condena Bolsonaro a 27 anos e 3 meses](https://www.metropoles.com/brasil/trama-golpista-stf-condena-bolsonaro-a-27-anos-e-3-meses-de-prisao) · acórdão do STF (⬜) |
| STF na eleição do Senado | [Gazeta do Povo: candidatos ao Senado que defendem impeachment de ministros](https://www.gazetadopovo.com.br/eleicoes/2026/gazeta-do-povo-mapeia-candidatos-senado-impeachment-ministros-stf/) · [ND+: STF vira tema central na eleição para o Senado](https://ndmais.com.br/politica/stf-vira-tema-central-na-eleicao-para-o-senado-em-2026/) |
| Fatos do pedido | [Metrópoles: Janones reeleito com queda de votos](https://www.metropoles.com/minas-gerais/apesar-de-reeleito-janones-perdeu-mais-de-160-mil-votos-em-quatro-anos) · [Poder360: Marina Silva não será candidata a deputada](https://www.poder360.com.br/poder-eleicoes/marina-silva-diz-que-nao-sera-candidata-a-deputada-federal/) |
| Regra das sobras | [CNN Brasil: pedido de aplicar as regras a partir de 2026](https://www.cnnbrasil.com.br/politica/hugo-pede-ao-stf-que-regras-sobre-sobras-eleitorais-valham-a-partir-de-2026/) · [ConJur: Câmara declara perda de mandato de sete deputados](https://www.conjur.com.br/2025-jul-31/camara-declara-perda-de-mandato-de-sete-deputados-e-convoca-substitutos/) · acórdãos das ADIs (⬜) |

⚠️ **As matérias acima são ponto de partida, lidas por resumo de busca.** Nenhum número delas entra no relatório sem o texto bruto capturado.

---

## 8. O que foi coletado de fato (07/out/2026)

A coleta foi feita no mesmo dia: o que foi baixado, com hash, está em `dados/MANIFESTO.json`, `dados/MANIFESTO_IBGE.json` e `dados/CAPTURAS.csv`.

| Grupo | Arquivos | Onde |
|---|---|---|
| TSE, 2006 a 2026 | `votacao_candidato_munzona`, `votacao_partido_munzona`, `detalhe_votacao_munzona`, `consulta_cand` (o de 2014 veio com 1 byte e não foi usado), pesquisas e contratantes (2018, 2022, 2026) | `dados/brutos/tse/` |
| Resultado oficial 2026 | JSON por UF de deputado federal, governador e senador | `dados/brutos/oficial2026/` |
| Câmara | `votacoesVotos`, `votacoesOrientacoes`, `votacoes`, `votacoesObjetos` (2023 a 2026), `deputados.csv` | `dados/brutos/camara/` |
| Senado | `senador/lista/atual` | `dados/brutos/senado/` |
| IBGE | Censo 2022 (tabelas 9923, 9606, 9514, 10061, 10198), PIB municipal 2022 e valor adicionado 2021, malha municipal | `dados/brutos/ibge/` |
| MDS | Novo Bolsa Família, competência 08/2026 | `dados/brutos/mds/` |
| Literatura | Bolognesi, Ribeiro e Codato, *Dados* 66(2), 2023 (PDF fora do git; URL e sha256 no manifesto; as médias usadas estão em `congresso/campos.py` e em `resultados/a1_escala_r1_usada.csv`) | `dados/brutos/literatura/` |
| Imprensa | páginas capturadas (HTML fora do git; sha256 e trecho em `dados/CAPTURAS.csv`; fatos extraídos em `resultados/`) | `dados/brutos/capturas/` |
| Reaproveitado do projeto irmão | `apoios_declarados.csv`, `senado_apoio_flavio.csv` (commit `740fe519`) | `dados/` |

**Ressalvas medidas na coleta:** o `votacao_candidato_munzona_2026.zip` cresceu de 316 MB para 454 MB entre 05 e 07/out (o manifesto guarda o hash da versão usada) · o SIDRA devolve "..." para o valor adicionado setorial de 2022 e 2023 · duas capturas de imprensa (Metrópoles: Janones e pesquisas de presidente) não trouxeram o trecho esperado e não foram usadas.

## Parâmetro principal e conferência externa (emenda 21, 07/out)

| Assunto | Fonte (captura) |
|---|---|
| Como cada partido se declara | Valor Econômico (ago/2026), pela reprodução em [outroladodahistoria.com](https://outroladodahistoria.com/partidos-esquerda-direita-brasil/) (`outroladodahistoria-autodeclaracao`) |
| GPS Partidário | Folha de S.Paulo (07/09/2026), via [Jornal de Brasília](https://jornaldebrasilia.com.br/noticias/politica-e-poder/novo-e-pl-sao-as-siglas-mais-a-direita-pstu-e-up-as-mais-a-esquerda-mostra-gps-partidario-2026/) (`jbr-gps-partidario`) |
| Câmara por campo, lista de partidos | [Poder360, 05/out](https://www.poder360.com.br/poder-eleicoes-2026/partidos-mais-a-direita-terao-276-deputados-na-camara/) (`poder360-276-direita`) |
| Senado por senador | [Poder360, 04/out](https://www.poder360.com.br/poder-eleicoes-2026/senado-sera-dominado-pela-direita-a-partir-de-2027/) (`poder360-senado-dominado-direita`) · [Poder360](https://www.poder360.com.br/poder-eleicoes-2026/49-dos-81-senadores-sao-alinhados-a-partidos-de-direita/) (`poder360-49-senadores-direita`) |
| Composição do Senado em 2027 | [Gazeta do Povo](https://www.gazetadopovo.com.br/eleicoes/2026/como-fica-composicao-senado-a-partir-de-2027-apos-recorde-pl/) (`gazeta-composicao-senado-2027`) |
