# Como reproduzir

Requisitos: Python 3.11, `pip install -r requirements.txt`, `curl`, ~7 GB livres (a maior parte é o dado bruto, fora do git).

```bash
# 1. coleta (cada arquivo entra em dados/MANIFESTO.json com sha256; teto de uma requisição por vez)
python ferramentas/coletar.py oficial-2026 senado camara tse-principal tse-partido tse-serie bolsa-familia
python ferramentas/coletar-ibge.py
python ferramentas/capturar.py            # páginas de imprensa, com sha256 e trecho em dados/CAPTURAS.csv

# 2. tabelas derivadas (dados/derivados/, fora do git)
python ferramentas/derivar-votos.py

# 3. análises, na ordem
python ferramentas/analise-1-plenario.py        # R2 e base de deputados em exercício
python ferramentas/analise-2-camara.py          # A1, A4, A5, D5, D6
python ferramentas/analise-3-senado-governos.py # A2, A3, D5, D8
python ferramentas/analise-4-pesquisas.py       # C
python ferramentas/capturar-pesquisas-historicas.py  # pesquisas de 2018 e 2022 (Pindograma, commit fixado)
python ferramentas/analise-12-pesquisas-2018-2022.py # C contra 2018 e 2022 (emenda 23) e grafico 28
python ferramentas/analise-5-geografia.py       # B (demora alguns minutos: lê o Bolsa Família)
python ferramentas/analise-6-plenario-e-eleicao.py  # D3
python ferramentas/analise-11-pl-e-blocos.py     # E: autodeclaração dos partidos, limiares, anatomia do PL (emenda 21)
python ferramentas/analise-8-veredito.py        # placar e docs/LEITURA_DA_IA.md
python ferramentas/analise-7-graficos.py        # resultados/figuras/video
python ferramentas/analise-10-animacao.py       # animações (resultados/animacao) e gráficos 15 a 27
python ferramentas/revisao-adversarial.py       # checagens independentes
python ferramentas/analise-9-relatorio.py       # RELATORIO.md e RESUMO_SIMPLES.md

python -m pytest -q
```

- As páginas de imprensa capturadas (`dados/brutos/capturas/`) **não** vão para o git (são conteúdo de terceiros): ficam o sha256 e o trecho em `dados/CAPTURAS.csv` e as tabelas extraídas (fatos) em `resultados/c1_pesquisas_governador_2026_extraidas.csv` e `resultados/d8_lista_gazeta_posicoes.csv` (e, para 2018 e 2022, `resultados/c5_pesquisas_governador_2018_2022_extraidas.csv`). Sem as capturas, as análises 3, 4 e 12 leem essas tabelas e dão o mesmo `RESUMO.json` (testado: mesmo sha256).
- Os números do relatório vêm todos de `resultados/RESUMO.json` e dos CSV de `resultados/`.
- `dados/FONTE_APURACAO.json` aponta para os boletins de urna do projeto `apuracao-eleicoes-2026` (commit `740fe519`); esta rodada **não** os usou.
- Arquivos do TSE e da Câmara podem ser republicados; compare o `sha256` no manifesto antes de concluir qualquer coisa diferente.
- O arquivo `votacao_candidato_munzona_2026.zip` do TSE cresceu de 316 MB (05/out) para 454 MB (07/out): o manifesto guarda o hash da versão usada.
