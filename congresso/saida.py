"""Escrita de resultados: tabelas CSV e o RESUMO.json de onde sai todo numero do relatorio."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .comum import RES

RESUMO = RES / "RESUMO.json"


def registrar(chave: str, valor) -> None:
    """Grava valor (dict/list/num/str) em RESUMO.json sob a chave (ex.: 'a1.camara.pl_2026')."""
    dados = json.loads(RESUMO.read_text(encoding="utf-8")) if RESUMO.exists() else {}
    cur = dados
    partes = chave.split(".")
    for p in partes[:-1]:
        cur = cur.setdefault(p, {})
    cur[partes[-1]] = _limpar(valor)
    RESUMO.write_text(json.dumps(dados, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def _limpar(v):
    if isinstance(v, dict):
        return {str(k): _limpar(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_limpar(x) for x in v]
    if hasattr(v, "item"):
        return v.item()
    if isinstance(v, float) and v != v:
        return None
    return v


def tabela(nome: str, df: pd.DataFrame) -> None:
    RES.mkdir(exist_ok=True)
    df.to_csv(RES / f"{nome}.csv", index=False, encoding="utf-8")
