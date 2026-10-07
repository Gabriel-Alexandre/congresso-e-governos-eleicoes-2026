"""Deriva tabelas leves e padronizadas a partir dos zips do TSE (dados/brutos/tse).

Saidas em dados/derivados/ (fora do git; reproduziveis rodando este script):
  votos_cand.parquet     voto nominal valido por candidato e municipio, 1o turno, cargos 1, 3, 5 e 6
  votos_partido.parquet  voto de legenda por partido e municipio (deputado federal)
  detalhe.parquet        aptos, comparecimento, abstencao, branco, nulo e validos por municipio e cargo
  candidatos_2026.parquet registro de candidatura de 2026 (consulta_cand)

Uso: python ferramentas/derivar-votos.py
"""
from __future__ import annotations

import io
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
TSE = RAIZ / "dados" / "brutos" / "tse"
SAIDA = RAIZ / "dados" / "derivados"
ANOS = (2006, 2010, 2014, 2018, 2022, 2026)
CARGOS = {"1", "3", "5", "6"}


def _ler(z: zipfile.ZipFile, nome: str, usecols):
    with z.open(nome) as fh:
        yield from pd.read_csv(
            fh, sep=";", encoding="latin-1", dtype=str, usecols=lambda c: c in usecols, chunksize=400_000
        )


def _arquivos(z: zipfile.ZipFile, ano: int, prefixo: str):
    for i in z.infolist():
        n = i.filename
        if n.startswith(prefixo) and n.endswith(".csv") and not n.endswith(("_BRASIL.csv",)):
            yield n


def cand(ano: int):
    z = zipfile.ZipFile(TSE / f"votacao_candidato_munzona_{ano}.zip")
    cols = {
        "ANO_ELEICAO", "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "CD_CARGO", "SQ_CANDIDATO", "NR_CANDIDATO",
        "NM_URNA_CANDIDATO", "SG_PARTIDO", "SG_FEDERACAO", "DS_SIT_TOT_TURNO", "QT_VOTOS_NOMINAIS",
        "QT_VOTOS_NOMINAIS_VALIDOS",
    }
    partes = []
    for nome in _arquivos(z, ano, "votacao_candidato_munzona"):
        for ch in _ler(z, nome, cols):
            ch = ch[(ch["NR_TURNO"] == "1") & (ch["CD_CARGO"].isin(CARGOS))]
            if ch.empty:
                continue
            v = ch["QT_VOTOS_NOMINAIS_VALIDOS"] if "QT_VOTOS_NOMINAIS_VALIDOS" in ch else ch["QT_VOTOS_NOMINAIS"]
            ch = ch.assign(votos=pd.to_numeric(v, errors="coerce").fillna(0).astype("int64"))
            if "SG_FEDERACAO" not in ch:
                ch["SG_FEDERACAO"] = "#NULO"
            partes.append(ch)
    d = pd.concat(partes, ignore_index=True)
    d = d.rename(
        columns={
            "ANO_ELEICAO": "ano", "SG_UF": "uf", "CD_MUNICIPIO": "mun", "CD_CARGO": "cargo", "SQ_CANDIDATO": "sq",
            "NR_CANDIDATO": "nr", "NM_URNA_CANDIDATO": "nome", "SG_PARTIDO": "partido", "SG_FEDERACAO": "fed",
            "DS_SIT_TOT_TURNO": "sit",
        }
    )
    g = d.groupby(["ano", "uf", "mun", "cargo", "sq", "nr", "nome", "partido", "fed", "sit"], as_index=False, dropna=False)["votos"].sum()
    return g


def partido(ano: int):
    z = zipfile.ZipFile(TSE / f"votacao_partido_munzona_{ano}.zip")
    cols = {
        "ANO_ELEICAO", "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "CD_CARGO", "NR_PARTIDO", "SG_PARTIDO", "SG_FEDERACAO",
        "QT_VOTOS_LEGENDA_VALIDOS", "QT_VOTOS_LEGENDA", "QT_VOTOS_NOM_CONVR_LEG_VALIDOS",
    }
    partes = []
    for nome in _arquivos(z, ano, "votacao_partido_munzona"):
        for ch in _ler(z, nome, cols):
            ch = ch[(ch["NR_TURNO"] == "1") & (ch["CD_CARGO"].isin(CARGOS))]
            if ch.empty:
                continue
            leg = ch["QT_VOTOS_LEGENDA_VALIDOS"] if "QT_VOTOS_LEGENDA_VALIDOS" in ch else ch["QT_VOTOS_LEGENDA"]
            conv = ch["QT_VOTOS_NOM_CONVR_LEG_VALIDOS"] if "QT_VOTOS_NOM_CONVR_LEG_VALIDOS" in ch else pd.Series("0", index=ch.index)
            ch = ch.assign(
                leg=pd.to_numeric(leg, errors="coerce").fillna(0).astype("int64"),
                conv=pd.to_numeric(conv, errors="coerce").fillna(0).astype("int64"),
            )
            if "SG_FEDERACAO" not in ch:
                ch["SG_FEDERACAO"] = "#NULO"
            partes.append(ch)
    d = pd.concat(partes, ignore_index=True).rename(
        columns={"ANO_ELEICAO": "ano", "SG_UF": "uf", "CD_MUNICIPIO": "mun", "CD_CARGO": "cargo", "NR_PARTIDO": "nr_partido", "SG_PARTIDO": "partido", "SG_FEDERACAO": "fed"}
    )
    return d.groupby(["ano", "uf", "mun", "cargo", "nr_partido", "partido", "fed"], as_index=False)[["leg", "conv"]].sum()


def detalhe(ano: int):
    z = zipfile.ZipFile(TSE / f"detalhe_votacao_munzona_{ano}.zip")
    num = [
        "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS_BRANCOS", "QT_TOTAL_VOTOS_NULOS",
        "QT_TOTAL_VOTOS_VALIDOS", "QT_VOTOS_NOMINAIS_VALIDOS", "QT_TOTAL_VOTOS_LEG_VALIDOS",
    ]
    cols = {"ANO_ELEICAO", "NR_TURNO", "SG_UF", "CD_MUNICIPIO", "CD_CARGO", *num}
    partes = []
    for nome in _arquivos(z, ano, "detalhe_votacao_munzona"):
        for ch in _ler(z, nome, cols):
            ch = ch[(ch["NR_TURNO"] == "1") & (ch["CD_CARGO"].isin(CARGOS))]
            if ch.empty:
                continue
            for c in num:
                ch[c] = pd.to_numeric(ch[c], errors="coerce").fillna(0).astype("int64") if c in ch else 0
            partes.append(ch)
    d = pd.concat(partes, ignore_index=True).rename(
        columns={
            "ANO_ELEICAO": "ano", "SG_UF": "uf", "CD_MUNICIPIO": "mun", "CD_CARGO": "cargo", "QT_APTOS": "aptos",
            "QT_COMPARECIMENTO": "comparecimento", "QT_ABSTENCOES": "abstencoes", "QT_VOTOS_BRANCOS": "brancos",
            "QT_TOTAL_VOTOS_NULOS": "nulos", "QT_TOTAL_VOTOS_VALIDOS": "validos",
        }
    )
    return d.groupby(["ano", "uf", "mun", "cargo"], as_index=False)[["aptos", "comparecimento", "abstencoes", "brancos", "nulos", "validos"]].sum()


def tarefa(args):
    tipo, ano = args
    f = {"cand": cand, "partido": partido, "detalhe": detalhe}[tipo]
    r = f(ano)
    print(tipo, ano, len(r), flush=True)
    return tipo, r


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    tarefas = [(t, a) for a in ANOS for t in ("cand", "partido", "detalhe")]
    tarefas.sort(key=lambda x: (x[0] != "cand", -x[1]))
    saidas = {"cand": [], "partido": [], "detalhe": []}
    with ProcessPoolExecutor(max_workers=6) as ex:
        for tipo, r in ex.map(tarefa, tarefas):
            saidas[tipo].append(r)
    nomes = {"cand": "votos_cand", "partido": "votos_partido", "detalhe": "detalhe"}
    for tipo, lst in saidas.items():
        df = pd.concat(lst, ignore_index=True)
        for c in ("ano", "mun", "cargo"):
            df[c] = df[c].astype(int)
        df.to_parquet(SAIDA / f"{nomes[tipo]}.parquet", index=False)
        print(nomes[tipo], df.shape, flush=True)

    # candidatos 2026
    z = zipfile.ZipFile(TSE / "consulta_cand_2026.zip")
    partes = []
    for nome in _arquivos(z, 2026, "consulta_cand"):
        with z.open(nome) as fh:
            partes.append(pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str))
    pd.concat(partes, ignore_index=True).to_parquet(SAIDA / "candidatos_2026.parquet", index=False)
    print("candidatos_2026 ok", flush=True)


if __name__ == "__main__":
    main()
