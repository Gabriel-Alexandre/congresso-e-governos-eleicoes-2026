# Congresso e governos: o que o 1º turno de 2026 mudou, e por quê

Análise aberta do resultado do 1º turno das eleições brasileiras de 2026 na **Câmara dos Deputados**, no **Senado** e nos **governos estaduais**, comparado com 2018 e 2022, com dado público do TSE, da Câmara, do Senado, do IBGE e dos registros de pesquisas eleitorais.

O projeto mede o que mudou, testa explicações concorrentes contra o dado, mede onde as pesquisas erraram e se o erro teve direção, e registra a leitura de uma IA sobre cada resultado, **marcada como opinião**. Os critérios foram gravados em commit antes das análises.

## Como ler os resultados (do mais curto ao mais completo)

1. [`RESUMO_SIMPLES.md`](RESUMO_SIMPLES.md): uma página.
2. [`resultados/figuras/video/`](resultados/figuras/video): 14 gráficos 1920×1080 (cadeiras por campo, ganhos e perdas, origem das cadeiras, puxadores, Senado, governos, mapa, perfil do município, pesquisas, reeleição, correlação com o candidato do PL, abstenção e o placar das hipóteses).
3. [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md): a leitura e o veredito da IA, arena por arena, com o grau de confiança.
4. [`RELATORIO.md`](RELATORIO.md): tudo, com o que o projeto **não** consegue dizer no topo.
5. [`resultados/RESUMO.json`](resultados/RESUMO.json) e os CSV de [`resultados/`](resultados): todo número do relatório.

## Como o método foi controlado

- [`docs/PLANO.md`](docs/PLANO.md): perguntas, hipóteses concorrentes e escopo. [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md): os critérios, **em commit antes de qualquer análise** (`e372efb`), com as emendas depois, cada uma dizendo se foi antes ou depois de ver o resultado.
- [`docs/REVISAO_ADVERSARIAL.md`](docs/REVISAO_ADVERSARIAL.md): três passadas (uma pelo olhar de cada lado e uma de método e linguagem) e 15 checagens independentes. [`docs/CORRECOES.md`](docs/CORRECOES.md): erros achados no caminho.
- [`docs/FONTES_DE_DADOS.md`](docs/FONTES_DE_DADOS.md) e `dados/MANIFESTO*.json`: de onde vem cada arquivo e o sha256 dele.
- [`docs/REPLICAR.md`](docs/REPLICAR.md): como refazer tudo.

## O que o projeto não faz

Não diz em quem cada pessoa votou, não afirma causa a partir de dado agregado, não julga intenção de ninguém e não faz previsão do 2º turno. "Direita", "centro" e "esquerda" são definições (três réguas, com sensibilidade), não fatos.

Os boletins de urna de 2026 estão no projeto irmão [`apuracao-eleicoes-2026`](https://github.com/Gabriel-Alexandre/apuracao-eleicoes-2026); esta rodada não os usou.

## Licença

Ainda sem licença (decisão do autor).
