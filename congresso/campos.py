"""As tres reguas de campo do pre-registro (secao 1).

R1: nota do partido na escala de especialistas (Bolognesi, Ribeiro e Codato, Dados 66(2), 2023, Tabela 1), 0 a 10.
R2: comportamento no plenario (calculado em ferramentas/analise-2-plenario.py).
R3: alinhamento por coligacao formal na eleicao de presidente (deputado) ou por apoio declarado (governador, senador).
"""
from __future__ import annotations

import unicodedata

import pandas as pd

# Medias da Tabela 1 do artigo, conferidas no texto extraido do PDF capturado (dados/brutos/literatura/bolognesi2023.pdf).
# PSTU e PCO: o texto do artigo diz "PSTU, com 0,51, e o PCO com 0,61". A ordem da primeira bolha da tabela
# (PSTU, PCO, PCB, PSOL, PCdoB, PT) casa com as seis medias 0,51; 0,61; 0,91; 1,28; 1,92; 2,97.
ESCALA = {
    "PSTU": 0.51, "PCO": 0.61, "PCB": 0.91, "PSOL": 1.28, "PCdoB": 1.92, "PT": 2.97, "PDT": 3.92, "PSB": 4.05,
    "Rede": 4.77, "PPS": 4.92, "PV": 5.29, "PTB": 6.10, "Avante": 6.32, "SDD": 6.50, "PMN": 6.88, "PMB": 6.90,
    "PHS": 6.96, "MDB": 7.01, "PSD": 7.09, "PSDB": 7.11, "Podemos": 7.24, "PPL": 7.27, "PRTB": 7.45, "Pros": 7.47,
    "PRP": 7.59, "PRB": 7.78, "PR": 7.78, "PTC": 7.86, "DC": 8.11, "PSL": 8.11, "Novo": 8.13, "Progressistas": 8.20,
    "PSC": 8.33, "Patriota": 8.55, "DEM": 8.57,
}

# sigla do TSE (normalizada) -> nome na escala. None = sem nota (partido que nao existia na pesquisa e nao e fusao de partidos com nota)
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper().strip()
    return s.replace("�", "")


TSE_PARA_ESCALA = {
    "PT": "PT", "PCDOB": "PCdoB", "PC DO B": "PCdoB", "PV": "PV", "PSOL": "PSOL", "PSB": "PSB", "PDT": "PDT",
    "REDE": "Rede", "CIDADANIA": "PPS", "PPS": "PPS", "PSDB": "PSDB", "MDB": "MDB", "PMDB": "MDB", "PSD": "PSD",
    "PODE": "Podemos", "PODEMOS": "Podemos", "PTN": "Podemos", "PP": "Progressistas", "PL": "PR", "PR": "PR",
    "REPUBLICANOS": "PRB", "PRB": "PRB", "NOVO": "Novo", "AVANTE": "Avante", "PT DO B": "Avante",
    "SOLIDARIEDADE": "SDD", "SD": "SDD", "PMN": "PMN", "MOBILIZA": "PMN", "PMB": "PMB", "PHS": "PHS",
    "PRTB": "PRTB", "PROS": "Pros", "PRP": "PRP", "PTC": "PTC", "AGIR": "PTC", "DC": "DC", "PSL": "PSL",
    "PSC": "PSC", "PATRI": "Patriota", "PATRIOTA": "Patriota", "DEM": "DEM", "PTB": "PTB", "PPL": "PPL",
    "PCB": "PCB", "PCO": "PCO", "PSTU": "PSTU",
}
# fusoes: media das notas pesada pelas cadeiras de 2018 (Uniao = DEM + PSL) e de 2022 (PRD = PTB + Patriota)
FUSOES = {"UNIAO": ("DEM", "PSL", 2018), "PRD": ("PTB", "Patriota", 2022)}


def sigla(p: str) -> str:
    return _norm(p)


def nota_r1(partido: str, pesos: dict | None = None) -> float | None:
    n = _norm(partido)
    if n in FUSOES:
        a, b, _ = FUSOES[n]
        if pesos and (pesos.get(a, 0) + pesos.get(b, 0)) > 0:
            wa, wb = pesos.get(a, 0), pesos.get(b, 0)
            return (ESCALA[a] * wa + ESCALA[b] * wb) / (wa + wb)
        return None
    nome = TSE_PARA_ESCALA.get(n)
    return ESCALA[nome] if nome else None


def campo_r1(nota, cortes=(4.0, 6.0)) -> str:
    if nota is None or pd.isna(nota):
        return "sem classificacao"
    if nota < cortes[0]:
        return "esquerda"
    if nota <= cortes[1]:
        return "centro"
    return "direita"
