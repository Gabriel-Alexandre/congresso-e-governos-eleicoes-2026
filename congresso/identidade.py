"""Identidade de pessoa entre eleicoes e entre TSE e Camara.

Uma pessoa e o mesmo registro quando tem a MESMA data de nascimento e pelo menos um nome igual depois de normalizado:
nome civil, nome de urna ou nome social (TSE), nome civil ou nome parlamentar (Camara). Isso cobre quem mudou de nome
civil entre uma eleicao e outra (correcao de 07/out, docs/CORRECOES.md). Os registros se juntam por uniao de chaves.
"""
from __future__ import annotations

import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
TSE = RAIZ / "dados" / "brutos" / "tse"


def nome_norm(s) -> str:
    if s is None or (isinstance(s, float) and s != s):
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    s = re.sub(r"[^A-Z ]", "", s)
    return re.sub(r"\s+", " ", s).strip()


class _Uniao:
    def __init__(self):
        self.pai = {}

    def achar(self, x):
        self.pai.setdefault(x, x)
        while self.pai[x] != x:
            self.pai[x] = self.pai[self.pai[x]]
            x = self.pai[x]
        return x

    def unir(self, a, b):
        ra, rb = self.achar(a), self.achar(b)
        if ra != rb:
            self.pai[rb] = ra


def _candidatos(ano: int) -> pd.DataFrame:
    z = zipfile.ZipFile(TSE / f"consulta_cand_{ano}.zip")
    partes = []
    for i in z.infolist():
        n = i.filename
        if n.endswith(".csv") and "_BRASIL" not in n and not n.endswith("_BR.csv"):
            with z.open(n) as fh:
                d = pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str, usecols=lambda c: c in {"SQ_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "NM_SOCIAL_CANDIDATO", "DT_NASCIMENTO", "SG_UF", "CD_CARGO"})
            partes.append(d[d["CD_CARGO"] == "6"])
    d = pd.concat(partes, ignore_index=True).drop_duplicates("SQ_CANDIDATO")
    d["nasc"] = pd.to_datetime(d["DT_NASCIMENTO"], format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m-%d")
    d["ano"] = ano
    return d


def resolver(anos=(2018, 2022, 2026), camara: pd.DataFrame | None = None):
    """Devolve (sq_por_ano -> pessoa, id_camara -> pessoa).

    camara: DataFrame com colunas id, nomeCivil, nome, dataNascimento (opcional).
    """
    u = _Uniao()
    regs = []
    for ano in anos:
        d = _candidatos(ano)
        for r in d.itertuples():
            if not isinstance(r.nasc, str):
                continue
            no = f"T|{ano}|{r.SQ_CANDIDATO}"
            u.achar(no)
            for nm in (r.NM_CANDIDATO, r.NM_URNA_CANDIDATO, r.NM_SOCIAL_CANDIDATO):
                k = nome_norm(nm)
                if k and k not in ("NULO", "NE"):
                    u.unir(no, f"K|{k}|{r.nasc}")
            regs.append((ano, r.SQ_CANDIDATO, no))
    regs_c = []
    if camara is not None:
        for r in camara.itertuples():
            if not isinstance(r.dataNascimento, str):
                continue
            no = f"C|{r.id}"
            u.achar(no)
            for nm in (r.nomeCivil, r.nome):
                k = nome_norm(nm)
                if k:
                    u.unir(no, f"K|{k}|{r.dataNascimento}")
            regs_c.append((r.id, no))
    sq = {(ano, s): u.achar(no) for ano, s, no in regs}
    cm = {i: u.achar(no) for i, no in regs_c}
    return sq, cm
