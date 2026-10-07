"""Bloco B pela regra dos tres grupos (emenda 24): o arrasto (B4) e o quanto a UF e o perfil explicam a mudanca (B2).

O bloco B original (`analise-5-geografia.py`) conta "direita" pela escala de especialistas (R1), que poe MDB, PSD,
PSDB e Podemos na direita. O video usa a autodeclaracao somada em tres grupos (emenda 22: direita = direita +
centro-direita; centro = so centro; esquerda = esquerda + centro-esquerda). Este script refaz, com essa regra, as duas
medidas que a fala usa, e deixa as de R1 intactas como comparacao:

- B4: correlacao, municipio a municipio dentro de cada UF, entre o % do candidato do PL/PSL a presidente e o % da
  direita em cada cargo; media das UFs ponderada pelo eleitorado (mesma conta do B4 original);
- B2: R2 de swing da direita para deputado federal (2022 -> 2026) so com a UF e com a UF mais o perfil do municipio
  (mesmas variaveis do B2 original, de `dados/derivados/municipios.parquet`).

Saidas: chaves `b5` em RESUMO.json e `resultados/b5_*.csv`. Rode depois de `analise-5-geografia.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.comum import DER, RES, detalhe, votos_cand, votos_partido  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

AUTO = {
    "PL": "direita", "NOVO": "direita", "MISSAO": "direita",
    "PP": "centro-direita", "REPUBLICANOS": "centro-direita", "UNIAO": "centro-direita", "PRD": "centro-direita",
    "MDB": "centro", "PSD": "centro", "SOLIDARIEDADE": "centro", "AVANTE": "centro", "MOBILIZA": "centro", "DEMOCRATA": "centro",
    "PSDB": "centro", "CIDADANIA": "centro", "AGIR": "centro", "PODE": "centro", "DC": "centro", "PRTB": "centro",
    "PSB": "centro-esquerda", "PDT": "centro-esquerda", "REDE": "centro-esquerda",
    "PT": "esquerda", "PCDOB": "esquerda", "PV": "esquerda", "PSOL": "esquerda", "PCB": "esquerda", "PSTU": "esquerda", "UP": "esquerda", "PCO": "esquerda",
}
HERDEIRO = {
    "DEM": "UNIAO", "PSL": "UNIAO", "PFL": "UNIAO", "PTB": "PRD", "PATRIOTA": "PRD", "PATRI": "PRD", "PEN": "PRD", "PRP": "PRD", "PAN": "PRD",
    "PR": "PL", "PRONA": "PL", "PRB": "REPUBLICANOS", "PPB": "PP", "PMDB": "MDB", "PROS": "SOLIDARIEDADE", "SD": "SOLIDARIEDADE",
    "PSC": "PODE", "PHS": "PODE", "PTN": "PODE", "PODEMOS": "PODE", "PPL": "PCDOB", "PC DO B": "PCDOB", "PSDC": "DC", "PPS": "CIDADANIA",
    "PMN": "MOBILIZA", "PTC": "AGIR", "PT DO B": "AVANTE",
}
VARS = ["pct_urbana", "pct_pretos_pardos", "pct_60mais", "pct_superior", "pct_evangelicos", "pct_catolicos", "log_pib_pc", "agro_share", "bf_por_100hab"]


def tres(sigla: str) -> str:
    s = campos.sigla(sigla)
    s = HERDEIRO.get(s, s)
    g = AUTO.get(s, "sem partido")
    return {"direita": "direita", "centro-direita": "direita", "centro": "centro", "centro-esquerda": "esquerda", "esquerda": "esquerda"}.get(g, "sem partido")


def shares() -> pd.DataFrame:
    cand, part = votos_cand(), votos_partido()
    linhas = []
    for ano in (2018, 2022, 2026):
        for cargo in (1, 3, 5, 6):
            c = cand[(cand.ano == ano) & (cand.cargo == cargo)].copy()
            if c.empty:
                continue
            c["lado"] = c["partido"].map(tres)
            g = c.groupby(["uf", "mun", "lado"])["votos"].sum().unstack(fill_value=0)
            if cargo == 6:  # deputado: voto de legenda entra, como no B original
                p = part[(part.ano == ano) & (part.cargo == 6)].copy()
                p["lado"] = p["partido"].map(tres)
                g = g.add(p.groupby(["uf", "mun", "lado"])[["leg", "conv"]].sum().sum(axis=1).unstack(fill_value=0), fill_value=0)
            g["total"] = g.sum(axis=1)
            g = g.reset_index()
            g["ano"], g["cargo"] = ano, cargo
            if cargo == 1:
                pl = c[c.partido.isin(["PL", "PSL"])].groupby(["uf", "mun"])["votos"].sum().rename("votos_pl_pres").reset_index()
                g = g.merge(pl, on=["uf", "mun"], how="left")
            linhas.append(g)
    s = pd.concat(linhas, ignore_index=True).fillna(0)
    if "direita" not in s:
        s["direita"] = 0
    s["pct_dir"] = 100 * s["direita"] / s["total"]
    s["pct_pl_pres"] = 100 * s["votos_pl_pres"] / s["total"]
    return s


def main() -> None:
    s = shares()
    ap = detalhe().groupby(["ano", "uf", "mun", "cargo"])[["aptos"]].sum().reset_index()

    # B4 pela regra dos tres grupos
    linhas = []
    for ano in (2018, 2022, 2026):
        pres = s[(s.ano == ano) & (s.cargo == 1)][["uf", "mun", "pct_pl_pres"]]
        for cargo, nome in ((6, "deputado federal"), (3, "governador"), (5, "senador")):
            if cargo == 5 and ano == 2022:
                continue
            c = s[(s.ano == ano) & (s.cargo == cargo)][["uf", "mun", "pct_dir"]].merge(pres, on=["uf", "mun"]).merge(ap[(ap.ano == ano) & (ap.cargo == cargo)][["uf", "mun", "aptos"]], on=["uf", "mun"])
            rs, ws = [], []
            for _, g in c.groupby("uf"):
                if len(g) >= 5 and g.pct_dir.std() > 0 and g.pct_pl_pres.std() > 0:
                    rs.append(np.corrcoef(g.pct_dir, g.pct_pl_pres)[0, 1]); ws.append(g.aptos.sum())
            linhas.append({"ano": ano, "cargo": nome, "ufs": len(rs), "correlacao_media_ponderada_por_uf": round(float(np.average(rs, weights=ws)), 3)})
    b5 = pd.DataFrame(linhas)
    tabela("b5_arrasto_tres_grupos", b5)
    registrar("b5.arrasto_tres_grupos", b5.to_dict("records"))

    # B2 (R2) pela regra dos tres grupos: swing da direita para deputado federal, 2022 -> 2026
    base = pd.read_parquet(DER / "municipios.parquet")
    x0 = s[(s.ano == 2022) & (s.cargo == 6)][["uf", "mun", "pct_dir"]]
    x1 = s[(s.ano == 2026) & (s.cargo == 6)][["uf", "mun", "pct_dir"]]
    j = x0.merge(x1, on=["uf", "mun"], suffixes=("_0", "_1"))
    j["swing_dir"] = j["pct_dir_1"] - j["pct_dir_0"]
    j = j.merge(ap[(ap.ano == 2026) & (ap.cargo == 6)][["uf", "mun", "aptos"]], on=["uf", "mun"]).merge(base[["uf", "mun"] + VARS], on=["uf", "mun"], how="left")
    a = j.dropna(subset=VARS + ["swing_dir", "aptos"])
    a = a[a.aptos > 0]
    m0 = smf.wls("swing_dir ~ C(uf)", data=a, weights=a["aptos"]).fit()
    m1 = smf.wls("swing_dir ~ C(uf) + " + " + ".join(VARS), data=a, weights=a["aptos"]).fit()
    r2 = {"so_uf": round(float(m0.rsquared), 3), "uf_mais_perfil": round(float(m1.rsquared), 3), "ganho_do_perfil": round(float(m1.rsquared - m0.rsquared), 3), "municipios": int(len(a))}
    registrar("b5.r2_modelo_deputado_federal_tres_grupos", r2)
    j[["uf", "mun", "pct_dir_0", "pct_dir_1", "swing_dir", "aptos"]].merge(base[["uf", "mun", "ibge", "nome_ibge"]], on=["uf", "mun"]).to_csv(RES / "b5_swing_municipal_deputado_federal_tres_grupos.csv", index=False)

    # B3 pela regra dos tres grupos: o voto de direita para deputado com o comparecimento de 2022
    a6 = detalhe()
    a6 = a6[a6.cargo == 6].groupby(["ano", "uf", "mun"])[["aptos", "comparecimento"]].sum().reset_index()
    x = s[(s.ano == 2026) & (s.cargo == 6)].merge(a6[a6.ano == 2026], on=["uf", "mun"]).merge(a6[a6.ano == 2022].rename(columns={"aptos": "aptos22", "comparecimento": "comp22"})[["uf", "mun", "aptos22", "comp22"]], on=["uf", "mun"])
    x["fator"] = (x.comp22 / x.aptos22) / (x.comparecimento / x.aptos)
    real = 100 * x.direita.sum() / x.total.sum()
    cf = 100 * (x.direita * x.fator).sum() / (x.total * x.fator).sum()
    # o voto no PL (PSL em 2018) para deputado x o voto no candidato do PL/PSL a presidente, mesma conta do arrasto
    cand, part = votos_cand(), votos_partido()
    pl = []
    for ano in (2018, 2022, 2026):
        partido = "PSL" if ano == 2018 else "PL"
        pres = cand[(cand.ano == ano) & (cand.cargo == 1)]
        pp = 100 * pres[pres.partido.isin(["PL", "PSL"])].groupby(["uf", "mun"]).votos.sum() / pres.groupby(["uf", "mun"]).votos.sum()
        d, lg = cand[(cand.ano == ano) & (cand.cargo == 6)], part[(part.ano == ano) & (part.cargo == 6)]
        tot = d.groupby(["uf", "mun"]).votos.sum()
        tot = tot + lg.groupby(["uf", "mun"])[["leg", "conv"]].sum().sum(axis=1).reindex(tot.index, fill_value=0)
        dp = d[d.partido == partido].groupby(["uf", "mun"]).votos.sum().reindex(tot.index, fill_value=0) + lg[lg.partido == partido].groupby(["uf", "mun"])[["leg", "conv"]].sum().sum(axis=1).reindex(tot.index, fill_value=0)
        jj = pd.concat([pp.rename("pres"), (100 * dp / tot).rename("dep")], axis=1).dropna().reset_index().merge(ap[(ap.ano == ano) & (ap.cargo == 6)][["uf", "mun", "aptos"]], on=["uf", "mun"])
        rs, ws = [], []
        for _, g in jj.groupby("uf"):
            if len(g) >= 5 and g.pres.std() > 0 and g.dep.std() > 0:
                rs.append(np.corrcoef(g.pres, g.dep)[0, 1]); ws.append(g.aptos.sum())
        pl.append({"ano": ano, "partido": partido, "ufs": len(rs), "correlacao_media_ponderada_por_uf": round(float(np.average(rs, weights=ws)), 3)})
    registrar("b5.pl_deputado_x_pl_presidente", pl)
    tabela("b5_pl_deputado_x_pl_presidente", pd.DataFrame(pl))

    registrar("b5.contrafactual_comparecimento_2022_tres_grupos", {"direita_pct_real_2026": round(float(real), 2), "direita_pct_com_comparecimento_de_2022": round(float(cf), 2), "diferenca_pp": round(float(cf - real), 2), "municipios": int(len(x))})
    print(b5.to_string())
    print(r2)


if __name__ == "__main__":
    main()
