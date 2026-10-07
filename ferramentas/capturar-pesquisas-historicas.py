"""Captura das pesquisas de governador de 2018 e 2022 (emenda 23).

Fonte: a base de pesquisas da reta final do Pindograma, usada no ranking de institutos deles, com o numero de registro
de cada pesquisa no TSE, o numero do candidato e o percentual estimulado. Versao fixada no commit abaixo; o
repositorio nao declara licenca, entao a copia bruta fica em dados/brutos (fora do git) e so a tabela extraida vai
para resultados/.

Antes desta fonte foi tentada a pagina de cada eleicao estadual na Wikipedia; em 2022 so 5 das 27 traziam Datafolha
ou Quaest na ultima semana, e a tentativa foi descartada (emenda 23).

Uso: python ferramentas/capturar-pesquisas-historicas.py
"""
from __future__ import annotations

import csv
import hashlib
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "dados" / "brutos" / "capturas"
CSV = RAIZ / "dados" / "CAPTURAS.csv"
COMMIT = "c04d197c4ae9989ff543452aab76a296e6a3baa4"
ARQS = {
    "pindograma-late-polls-2012-2018": "late_polls_2012_2014_2016_2018.csv",
    "pindograma-late-polls-2022": "late_polls_2022.csv",
}


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    with CSV.open(encoding="utf-8") as f:
        ja = {r["id"] for r in csv.DictReader(f)}
    for cid, nome in ARQS.items():
        url = f"https://raw.githubusercontent.com/pindograma/ranking_de_institutos/{COMMIT}/data/polls/{nome}"
        b = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "congresso-eleicoes-2026"}), timeout=120).read()
        (PASTA / f"{cid}.csv").write_bytes(b)
        if cid in ja:
            continue
        linha = {"id": cid, "url": url, "capturado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "bytes": len(b),
                 "sha256": hashlib.sha256(b).hexdigest(), "status": "ok",
                 "assunto": "pesquisas da reta final com registro no TSE, base do ranking de institutos do Pindograma (commit fixado)",
                 "trecho": b.decode("utf-8", "replace").splitlines()[0][:200]}
        with CSV.open("a", encoding="utf-8", newline="") as f:
            csv.DictWriter(f, fieldnames=list(linha)).writerow(linha)
        print(cid, len(b))


if __name__ == "__main__":
    main()
