# ESTADO: onde o trabalho parou

**Atualizado em:** 07/out/2026.

## Em uma frase

A execução de ponta a ponta está feita: coleta com hash, validação (513 de 513 cadeiras reproduzidas), blocos A, B, C e D (com as limitações declaradas), três passadas de revisão adversarial, relatório, resumo, 30 gráficos 1920×1080 (mais 7 versões borradas), os dados das animações de cadeira e de mapa e a leitura da IA. 🆕 Emenda 21 (07/out, depois de ver os resultados, a pedido do autor): o parâmetro principal de campo é a autodeclaração dos partidos, com o PL no centro (`ferramentas/analise-11-pl-e-blocos.py`); emenda 22 (07/out, definição do autor): os grupos se somam em três, direita = direita + centro-direita, centro = só centro, esquerda = esquerda + centro-esquerda. O repositório é **público** (decisão do autor). Falta o que é dele: gravar e publicar o vídeo.

## O que está pronto

| Peça | Estado |
|---|---|
| Plano, pré-registro (commit `e372efb`, antes de qualquer análise) e fontes | ✅ `docs/PLANO.md`, `docs/PRE_REGISTRO.md`, `docs/FONTES_DE_DADOS.md` |
| Coleta com sha256 | ✅ `dados/MANIFESTO.json`, `dados/MANIFESTO_IBGE.json`, `dados/CAPTURAS.csv` |
| Validação (porta) | ✅ 513 de 513 cadeiras reproduzidas; votos por partido iguais ao JSON oficial |
| Relatório e resumo | ✅ `RELATORIO.md`, `RESUMO_SIMPLES.md`, gerados de `resultados/RESUMO.json` |
| Leitura e veredito da IA | ✅ `docs/LEITURA_DA_IA.md` |
| Revisão adversarial (3 passadas) | ✅ `docs/REVISAO_ADVERSARIAL.md` (15 de 15 checagens programáticas) |
| Gráficos do vídeo | ✅ `resultados/figuras/video/` (30 gráficos e 7 versões borradas, `ferramentas/analise-7-graficos.py`, `analise-10-animacao.py` e `analise-12-pesquisas-2018-2022.py`) |
| Parâmetro principal (autodeclaração, em três grupos) | ✅ `ferramentas/analise-11-pl-e-blocos.py`, tabelas `resultados/e*_*.csv` (as `_em_3` são a soma em três), chaves `e0` a `e7` |
| Dados das animações | ✅ `resultados/animacao/` (hemiciclo da Câmara 2022 e 2026, Senado 2027, governos 2022 e 2026, Senado por UF), gerados por `ferramentas/analise-10-animacao.py` |
| Pesquisas contra 2018 e 2022 (emenda 23) | ✅ `ferramentas/analise-12-pesquisas-2018-2022.py`, tabelas `resultados/c5_*.csv`, gráfico 28; fonte Pindograma (commit fixado), conferida em 20 números |
| Bloco B pela regra dos três grupos (emenda 24) | ✅ `ferramentas/analise-13-geografia-tres-grupos.py`, chaves `b5`, gráficos 29 e 30 |
| Testes | ✅ `python -m pytest -q` (11) |
| Erros achados no caminho | ✅ `docs/CORRECOES.md` |

## O que o projeto concluiu, em uma linha

Pela autodeclaração em três grupos, a direita foi de 250 para 265 deputados (passa da maioria absoluta, 257) e de 32 para 48 senadores (no limite da PEC, 49), o centro encolheu (135 → 124 e 31 → 17) e a esquerda ficou do mesmo tamanho em votos (26,5% → 26,3%); o PL cresceu muito (98 → 121 cadeiras), enquanto o campo de direita pela escala de especialistas, que já punha o centrão na direita, ficou parado em votos (72,0% → 72,3%); a federação do PT também cresceu (82 → 88); o crescimento do PL acompanha concentração de voto, eficiência do sistema e puxadores; as pesquisas de governador mostraram a direita mais fraca do que a urna na maioria das disputas em 2018 e 2022, e não em 2026; os casos (Master, STF, INSS) e as emendas **não foram testados**. Detalhe: [`RESUMO_SIMPLES.md`](RESUMO_SIMPLES.md).

## Limites declarados

Topo do [`RELATORIO.md`](RELATORIO.md) (§0) e §15 do pré-registro.

## O que observar ao retomar

- O 2º turno é em 25/10; os 7 estados "em disputa" estão sem previsão.
- O TSE pode republicar arquivos: compare os hashes do manifesto.
- Quando a prestação de contas final sair, o gasto de campanha pode entrar (bloco D4).
