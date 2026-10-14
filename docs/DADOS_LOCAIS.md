# Dados locais: o que foi apagado e como refazer

**14/out/2026, pedido do autor:** depois do vídeo longo 8 pronto, apagar as bases pesadas baixadas para a pesquisa dos vídeos longos, mantendo tudo documentado. Este projeto é o do **vídeo longo 6** (Congresso e governos).

## O que foi apagado

| Pasta | O que tinha | Tamanho | Como refazer (`docs/REPLICAR.md`, passo 1) |
|---|---|---|---|
| `dados/brutos/tse/` | os zips de votação por município e zona, partido e candidatos do TSE, de 2006 a 2026 | ~2,3 GB | `python ferramentas/coletar.py tse-principal tse-partido tse-serie` |
| `dados/brutos/mds/` | o Novo Bolsa Família de agosto de 2026 (Portal da Transparência) | ~316 MB | `python ferramentas/coletar.py bolsa-familia` |
| `dados/brutos/camara/` | votações, deputados e legislaturas dos dados abertos da Câmara | ~270 MB | `python ferramentas/coletar.py camara` |
| `dados/brutos/ibge/` | as tabelas do IBGE | ~76 MB | `python ferramentas/coletar-ibge.py` |

**Total liberado: ~3,0 GB.** Cada arquivo baixado tem endereço e sha256 em `dados/MANIFESTO.json` e `dados/MANIFESTO_IBGE.json`, no git.

## O que ficou no disco, de propósito

| Pasta | Por quê |
|---|---|
| `dados/brutos/capturas/` (21 MB) e `dados/brutos/literatura/` | páginas de imprensa e textos capturados; página muda ou sai do ar e não volta igual |
| `dados/brutos/oficial2026/` (2,7 MB) e `dados/brutos/senado/` | o resultado oficial da noite e os dados do Senado, leves |
| `dados/derivados/` (~41 MB) | as tabelas que o projeto `presidente-primeiro-turno-2026` (vídeo 7) lê; com elas, as análises rodam sem baixar de novo |

## O que nunca dependeu dos brutos

`resultados/` inteiro, o `RELATORIO.md`, o `RESUMO_SIMPLES.md`, o código e os manifestos: tudo no git.

⚠️ **Risco registrado uma vez:** o TSE já tirou do ar arquivos de eleição anterior (os logs de 2022). Se isso acontecer com os de 2026, o download não volta igual; o `dados/MANIFESTO.json`, que está no git, continua provando o que foi lido (endereço, hora, tamanho e sha256 de cada arquivo).
