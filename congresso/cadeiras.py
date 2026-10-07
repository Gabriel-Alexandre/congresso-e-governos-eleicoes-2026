"""Reproducao da distribuicao de cadeiras da Camara por UF (quociente eleitoral, quociente partidario e sobras).

Regra do Codigo Eleitoral (arts. 106 a 111) com a Lei 14.211/2021. A variante que reproduz o resultado oficial
e a aplicada (docs/PRE_REGISTRO.md, secao 6). Variantes: (frac_lista, frac_cand) = fracao do quociente eleitoral
exigida da lista e do candidato para disputar as sobras.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .comum import chave_lista


@dataclass
class Resultado:
    eleitos: set  # sq dos eleitos
    qe: int
    qp: dict
    sobras: dict


def quociente(validos: int, vagas: int) -> int:
    q = validos / vagas
    return int(q + 0.5) if q - int(q) > 0.5 else int(q)  # fracao igual ou inferior a meio desprezada


def distribuir(listas: dict, vagas: int, frac_lista: float, frac_cand: float, piso_cand_qp: float = 0.10) -> Resultado:
    """listas: chave -> {'votos': total da lista, 'cands': [(sq, votos), ...]}"""
    validos = sum(l["votos"] for l in listas.values())
    qe = quociente(validos, vagas)
    eleitos: set = set()
    qp, sobras = {}, {}
    cand_ord = {k: sorted(l["cands"], key=lambda c: (-c[1], c[0])) for k, l in listas.items()}
    n_eleitos_lista = {k: 0 for k in listas}
    for k, l in listas.items():
        q = l["votos"] // qe if qe else 0
        qp[k] = q
        elegiveis = [c for c in cand_ord[k] if c[1] >= piso_cand_qp * qe]
        for c in elegiveis[:q]:
            eleitos.add(c[0])
            n_eleitos_lista[k] += 1
    restantes = vagas - len(eleitos)
    while restantes > 0:
        def pode(k, rigido: bool) -> bool:
            if (not rigido) or l_ok(k):
                return any(c[0] not in eleitos and (c[1] >= frac_cand * qe if rigido else True) for c in cand_ord[k])
            return False

        def l_ok(k):
            return listas[k]["votos"] >= frac_lista * qe

        cands = [k for k in listas if pode(k, True)]
        if not cands:
            cands = [k for k in listas if pode(k, False)]  # art. 111: ninguem atingiu o minimo
        if not cands:
            break
        melhor = max(cands, key=lambda k: (listas[k]["votos"] / (n_eleitos_lista[k] + 1), listas[k]["votos"]))
        c = next(c for c in cand_ord[melhor] if c[0] not in eleitos)
        eleitos.add(c[0])
        n_eleitos_lista[melhor] += 1
        sobras[melhor] = sobras.get(melhor, 0) + 1
        restantes -= 1
    return Resultado(eleitos, qe, qp, sobras)


def preparar(cand: pd.DataFrame, partido: pd.DataFrame, ano: int):
    """Filtra e agrega uma vez por ano (deputado federal): devolve (candidatos por lista e sq, legenda por lista), por UF."""
    c = cand[(cand.ano == ano) & (cand.cargo == 6)].copy()
    c["lista"] = chave_lista(c["fed"], c["partido"])
    nom = c.groupby(["uf", "lista", "sq"], as_index=False).votos.sum()
    p = partido[(partido.ano == ano) & (partido.cargo == 6)].copy()
    p["lista"] = chave_lista(p["fed"], p["partido"])
    leg = p.groupby(["uf", "lista"], as_index=False)[["leg", "conv"]].sum()
    return {uf: (g, leg[leg.uf == uf].set_index("lista")) for uf, g in nom.groupby("uf")}


def montar_listas(cand=None, partido=None, ano=None, uf=None, prep=None) -> dict:
    if prep is None:
        prep = preparar(cand, partido, ano)
    nom, leg = prep[uf]
    listas = {}
    for lista, g in nom.groupby("lista"):
        extra = int(leg.loc[lista, "leg"] + leg.loc[lista, "conv"]) if lista in leg.index else 0
        listas[lista] = {"votos": int(g.votos.sum()) + extra, "cands": [(r.sq, int(r.votos)) for r in g.itertuples()]}
    for lista in leg.index:
        if lista not in listas:
            listas[lista] = {"votos": int(leg.loc[lista, "leg"] + leg.loc[lista, "conv"]), "cands": []}
    return listas
