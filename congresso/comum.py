"""Leitura das tabelas derivadas e definicoes comuns."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DER = RAIZ / "dados" / "derivados"
RES = RAIZ / "resultados"
FIG = RES / "figuras"

UFS = "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split()

ELEITO = ("ELEITO", "ELEITO POR QP", "ELEITO POR MÉDIA", "MÉDIA")


def eleito(sit: pd.Series) -> pd.Series:
    s = sit.fillna("").str.upper()
    return s.isin(ELEITO)


def votos_cand() -> pd.DataFrame:
    return pd.read_parquet(DER / "votos_cand.parquet")


def votos_partido() -> pd.DataFrame:
    return pd.read_parquet(DER / "votos_partido.parquet")


def detalhe() -> pd.DataFrame:
    return pd.read_parquet(DER / "detalhe.parquet")


def chave_lista(fed: pd.Series, partido: pd.Series) -> pd.Series:
    """Federacao conta como uma lista; senao, o partido."""
    f = fed.fillna("#NULO")
    sem = f.str.startswith("#") | (f == "")
    return partido.where(sem, "FED:" + f)


def ler_camara(nome: str, ano: int) -> pd.DataFrame:
    """CSV da Camara: alguns campos de texto passam do limite padrao e tem quebra de linha, entao motor python."""
    import csv
    import sys

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    ruins = []
    d = pd.read_csv(
        RAIZ / "dados" / "brutos" / "camara" / f"{nome}-{ano}.csv", sep=";", dtype=str, engine="python",
        on_bad_lines=lambda l: ruins.append(l) or None,
    )
    d.attrs["linhas_ruins"] = len(ruins)
    return d
