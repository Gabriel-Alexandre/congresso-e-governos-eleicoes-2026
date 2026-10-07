"""Aplica no PLANO e nas FONTES o que foi executado (texto fixo, sem numero de resultado).

Rodar uma vez depois das analises. Idempotente: nao duplica a secao se ja existir.
"""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

plano = RAIZ / "docs" / "PLANO.md"
s = plano.read_text(encoding="utf-8")
s = s.replace(
    "**Escrito em:** 07/out/2026, manhã. **Estado:** plano fechado, aguardando a ordem de execução do autor.",
    "**Escrito em:** 07/out/2026, manhã. **Estado:** ✅ **executado em 07/out/2026** (ver §15). O resultado está em [`../RELATORIO.md`](../RELATORIO.md).",
)
if "## 15. O que foi executado" not in s:
    s = s.rstrip("\n") + """

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
"""
plano.write_text(s, encoding="utf-8")

fontes = RAIZ / "docs" / "FONTES_DE_DADOS.md"
f = fontes.read_text(encoding="utf-8")
if "## 8. O que foi coletado de fato" not in f:
    f = f.rstrip("\n") + """

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
| Literatura | Bolognesi, Ribeiro e Codato, *Dados* 66(2), 2023 | `dados/brutos/literatura/` |
| Imprensa | páginas capturadas (HTML, sha256 e trecho em `dados/CAPTURAS.csv`) | `dados/brutos/capturas/` |
| Reaproveitado do projeto irmão | `apoios_declarados.csv`, `senado_apoio_flavio.csv` (commit `740fe519`) | `dados/` |

**Ressalvas medidas na coleta:** o `votacao_candidato_munzona_2026.zip` cresceu de 316 MB para 454 MB entre 05 e 07/out (o manifesto guarda o hash da versão usada) · o SIDRA devolve "..." para o valor adicionado setorial de 2022 e 2023 · duas capturas de imprensa (Metrópoles: Janones e pesquisas de presidente) não trouxeram o trecho esperado e não foram usadas.
"""
fontes.write_text(f, encoding="utf-8")

(RAIZ / ".gitignore").write_text(
    "dados/brutos/*\n!dados/brutos/capturas/\n!dados/brutos/literatura/\ndados/derivados/\ndados/logs/\n__pycache__/\n*.pyc\n.venv/\n.pytest_cache/\n",
    encoding="utf-8",
)
print("ok docs")
