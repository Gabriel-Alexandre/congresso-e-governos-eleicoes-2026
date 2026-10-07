# ESTADO: onde o trabalho parou

**Atualizado em:** 07/out/2026.

## Em uma frase

A execução de ponta a ponta está feita: coleta com hash, validação (513 de 513 cadeiras reproduzidas), blocos A, B, C e D (com as limitações declaradas), três passadas de revisão adversarial, relatório, resumo, 14 gráficos 1920×1080 e a leitura da IA. O repositório é **público** (decisão do autor). Falta o que é dele: gravar e publicar o vídeo.

## O que está pronto

| Peça | Estado |
|---|---|
| Plano, pré-registro (commit `e372efb`, antes de qualquer análise) e fontes | ✅ `docs/PLANO.md`, `docs/PRE_REGISTRO.md`, `docs/FONTES_DE_DADOS.md` |
| Coleta com sha256 | ✅ `dados/MANIFESTO.json`, `dados/MANIFESTO_IBGE.json`, `dados/CAPTURAS.csv` |
| Validação (porta) | ✅ 513 de 513 cadeiras reproduzidas; votos por partido iguais ao JSON oficial |
| Relatório e resumo | ✅ `RELATORIO.md`, `RESUMO_SIMPLES.md`, gerados de `resultados/RESUMO.json` |
| Leitura e veredito da IA | ✅ `docs/LEITURA_DA_IA.md` |
| Revisão adversarial (3 passadas) | ✅ `docs/REVISAO_ADVERSARIAL.md` (15 de 15 checagens programáticas) |
| Gráficos do vídeo | ✅ `resultados/figuras/video/` (14 arquivos) |
| Testes | ✅ `python -m pytest -q` (8) |
| Erros achados no caminho | ✅ `docs/CORRECOES.md` |

## O que o projeto concluiu, em uma linha

O PL cresceu muito (98 → 121 cadeiras), mas o campo de direita pela escala de especialistas ficou parado em votos (72,0% → 72,3%); a federação do PT também cresceu (82 → 88); o crescimento do PL acompanha concentração de voto, eficiência do sistema e puxadores; os casos (Master, STF, INSS) e as emendas **não foram testados**. Detalhe: [`RESUMO_SIMPLES.md`](RESUMO_SIMPLES.md).

## Limites declarados

Topo do [`RELATORIO.md`](RELATORIO.md) (§0) e §15 do pré-registro.

## O que observar ao retomar

- O 2º turno é em 25/10; os 7 estados "em disputa" estão sem previsão.
- O TSE pode republicar arquivos: compare os hashes do manifesto.
- Quando a prestação de contas final sair, o gasto de campanha pode entrar (bloco D4).
