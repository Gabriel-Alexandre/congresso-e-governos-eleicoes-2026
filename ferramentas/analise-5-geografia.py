"""Bloco B: geografia, perfil do municipio (Censo 2022, PIB, Bolsa Familia), abstencao e arrasto.

Criterios: docs/PRE_REGISTRO.md secao 12. Unidade: municipio, ponderado pelo eleitorado (aptos).
Saidas: dados/derivados/municipios.parquet, resultados/b*_*.csv e chaves b1..b4 em RESUMO.json.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.comum import DER, RAIZ, UFS, detalhe, votos_cand, votos_partido  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

TSE = RAIZ / "dados/brutos/tse"
IBGE = RAIZ / "dados/brutos/ibge"


def nn(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9 ]", "", s).strip()


def ler_sidra(tab: str) -> pd.DataFrame:
    linhas = []
    for f in sorted(IBGE.glob(f"{tab}-*.json")):
        raw = f.read_bytes()
        try:
            d = json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError:
            d = json.loads(raw.decode("latin-1"))
        linhas += d[1:]
    return pd.DataFrame(linhas)


def num(s):
    return pd.to_numeric(s.replace({"-": np.nan, "...": np.nan, "..": np.nan, "X": np.nan}), errors="coerce")


# ----------------------------------------------------------------------------------------------
def tabela_municipios() -> pd.DataFrame:
    """TSE (uf, cd) -> IBGE (7 digitos), por nome normalizado dentro da UF; resto por semelhanca."""
    z = zipfile.ZipFile(TSE / "detalhe_votacao_munzona_2026.zip")
    partes = []
    for n in z.namelist():
        if n.endswith(".csv") and "_BR" not in n:
            with z.open(n) as fh:
                partes.append(pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str, usecols=["SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO"]))
    t = pd.concat(partes).drop_duplicates()
    t = t[t.SG_UF != "ZZ"].rename(columns={"SG_UF": "uf", "CD_MUNICIPIO": "mun", "NM_MUNICIPIO": "nome_tse"})
    t["mun"] = t["mun"].astype(int)
    t["n"] = t["nome_tse"].map(nn)
    b = ler_sidra("9923")
    b = b[b["D4C"] == "6795"].copy()
    b["ibge"] = b["D1C"].astype(str)
    b["uf"] = b["D1N"].str.extract(r"(?:\(|- )([A-Z]{2})\)?$")[0]
    b["nome_ibge"] = b["D1N"].str.replace(r"\s*(?:\(|- )[A-Z]{2}\)?$", "", regex=True)
    b["n"] = b["nome_ibge"].map(nn)
    b["pop"] = num(b["V"])
    b = b[["ibge", "uf", "nome_ibge", "n", "pop"]]
    m = t.merge(b, on=["uf", "n"], how="left")
    sem = m[m.ibge.isna()]
    # correcoes por semelhanca dentro da UF, apenas as sem par (listadas em tabela)
    achou = {}
    for r in sem.itertuples():
        cand = b[(b.uf == r.uf) & ~b.ibge.isin(m.ibge.dropna())]
        alvo = difflib.get_close_matches(r.n, list(cand.n), n=1, cutoff=0.85)
        if alvo:
            achou[(r.uf, r.mun)] = cand[cand.n == alvo[0]].iloc[0]
    for (uf, mun), row in achou.items():
        i = m[(m.uf == uf) & (m.mun == mun)].index[0]
        for c in ("ibge", "nome_ibge", "pop"):
            m.loc[i, c] = row[c]
    tabela("b0_municipios_sem_par_ibge", m[m.ibge.isna()][["uf", "mun", "nome_tse"]])
    registrar("b0.municipios_tse", int(len(t)))
    registrar("b0.casados_exato_ou_por_semelhanca", int(m.ibge.notna().sum()))
    registrar("b0.casados_por_semelhanca", int(len(achou)))
    registrar("b0.sem_par", int(m.ibge.isna().sum()))
    return m.dropna(subset=["ibge"]).drop_duplicates(["uf", "mun"])


def perfil_ibge(m: pd.DataFrame) -> pd.DataFrame:
    out = m[["ibge", "uf", "mun", "pop"]].copy()
    # situacao do domicilio
    t = ler_sidra("9923")
    t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    u = t.pivot_table(index="ibge", columns="D4C", values="v")
    out = out.merge((100 * u["1"] / u["6795"]).rename("pct_urbana").reset_index(), on="ibge", how="left")
    # cor ou raca
    t = ler_sidra("9606"); t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    c = t.pivot_table(index="ibge", columns="D4C", values="v")
    out = out.merge((100 * (c["2777"] + c["2779"]) / c["95251"]).rename("pct_pretos_pardos").reset_index(), on="ibge", how="left")
    # idade
    t = ler_sidra("9514"); t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    a = t.pivot_table(index="ibge", columns="D6C", values="v")
    s60 = a[["93095", "93096", "93097", "93098", "49108", "49109", "60040", "60041", "6653"]].sum(axis=1)
    out = out.merge((100 * s60 / a["100362"]).rename("pct_60mais").reset_index(), on="ibge", how="left")
    # instrucao (18+): superior completo
    t = ler_sidra("10061"); t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    e = t.pivot_table(index="ibge", columns="D4C", values="v")
    out = out.merge((100 * e["99713"] / e["120704"]).rename("pct_superior").reset_index(), on="ibge", how="left")
    # religiao (15+)
    t = ler_sidra("10198"); t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    r = t.pivot_table(index="ibge", columns="D4C", values="v")
    tot = r["95278"]
    out = out.merge(pd.DataFrame({"pct_evangelicos": 100 * r["95277"] / tot, "pct_catolicos": 100 * r["95263"] / tot, "pct_sem_religiao": 100 * r["2836"] / tot}).reset_index(), on="ibge", how="left")
    # PIB e agropecuaria (2023)
    t = ler_sidra("5938"); t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    out = out.merge(t.pivot_table(index="ibge", columns="D2C", values="v")["37"].rename("pib_mil_reais").reset_index(), on="ibge", how="left")
    t = ler_sidra("5938v"); t["ibge"] = t["D1C"].astype(str); t["v"] = num(t["V"])
    p = t.pivot_table(index="ibge", columns="D2C", values="v")
    out = out.merge((100 * p["513"] / p["498"]).rename("agro_share").reset_index(), on="ibge", how="left")
    out["pib_pc"] = out["pib_mil_reais"] * 1000 / out["pop"]
    out["log_pib_pc"] = np.log(out["pib_pc"])
    return out


def bolsa_familia(m: pd.DataFrame) -> pd.DataFrame:
    dest = DER / "bolsa_familia_202608.parquet"
    if not dest.exists():
        z = zipfile.ZipFile(RAIZ / "dados/brutos/mds/202608_NovoBolsaFamilia.zip")
        acum = {}
        with z.open(z.namelist()[0]) as fh:
            for ch in pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str, chunksize=1_000_000, usecols=[0, 1, 2, 4, 6]):
                ch.columns = ["comp", "ref", "uf", "mun", "nis"]
                ch = ch[ch.ref == "202608"]
                ch["k"] = ch.uf + "|" + ch.mun.map(nn)
                for k, g in ch.groupby("k"):
                    acum.setdefault(k, set()).update(g.nis.unique())
        pd.DataFrame({"k": list(acum), "beneficiarios": [len(v) for v in acum.values()]}).to_parquet(dest, index=False)
    bf = pd.read_parquet(dest)
    m = m.copy()
    m["k"] = m["uf"] + "|" + m["n"]
    m = m.merge(bf, on="k", how="left")
    return m[["ibge", "beneficiarios"]]


# ----------------------------------------------------------------------------------------------
def shares(m: pd.DataFrame, pesos: dict) -> pd.DataFrame:
    cand = votos_cand()
    part = votos_partido()
    campo_cache: dict[str, str] = {}

    def campo(p):
        if p not in campo_cache:
            campo_cache[p] = campos.campo_r1(campos.nota_r1(p, pesos))
        return campo_cache[p]
    linhas = []
    mm = m[["uf", "mun", "ibge"]]
    for ano in (2010, 2018, 2022, 2026):
        for cargo in (1, 3, 5, 6):
            c = cand[(cand.ano == ano) & (cand.cargo == cargo)].copy()
            if c.empty:
                continue
            c["campo"] = c["partido"].map(campo)
            g = c.groupby(["uf", "mun", "campo"])["votos"].sum().unstack(fill_value=0)
            if cargo == 6:
                p = part[(part.ano == ano) & (part.cargo == 6)].copy()
                p["campo"] = p["partido"].map(campo)
                lg = p.groupby(["uf", "mun", "campo"])[["leg", "conv"]].sum().sum(axis=1).unstack(fill_value=0)
                g = g.add(lg, fill_value=0)
            g["total"] = g.sum(axis=1)
            g = g.reset_index()
            g["ano"], g["cargo"] = ano, cargo
            if cargo == 1:
                pl = c[c.partido.isin(["PL", "PSL"])].groupby(["uf", "mun"])["votos"].sum().rename("votos_pl_pres").reset_index()
                g = g.merge(pl, on=["uf", "mun"], how="left")
            linhas.append(g)
    s = pd.concat(linhas, ignore_index=True).fillna(0)
    for k in ("direita", "esquerda", "centro", "sem classificacao"):
        if k not in s:
            s[k] = 0
    s["pct_dir"] = 100 * s["direita"] / s["total"]
    s["pct_esq"] = 100 * s["esquerda"] / s["total"]
    if "votos_pl_pres" in s:
        s["pct_pl_pres"] = 100 * s["votos_pl_pres"] / s["total"]
    return s.merge(mm, on=["uf", "mun"], how="inner")


def main() -> None:
    pesos = json.loads((RAIZ / "resultados/RESUMO.json").read_text(encoding="utf-8"))["a1"]["pesos_fusoes"]
    m = tabela_municipios()
    perfil = perfil_ibge(m)
    bf = bolsa_familia(m)
    base = m[["ibge", "uf", "mun", "nome_ibge", "pop"]].merge(perfil.drop(columns=["uf", "mun", "pop"]), on="ibge", how="left").merge(bf, on="ibge", how="left")
    base["bf_por_100hab"] = 100 * base["beneficiarios"] / base["pop"]
    # eleitorado e comparecimento
    dt = detalhe()
    ap = dt.groupby(["ano", "uf", "mun", "cargo"])[["aptos", "comparecimento", "abstencoes"]].sum().reset_index()
    s = shares(m, pesos)
    base.to_parquet(DER / "municipios.parquet", index=False)
    registrar("b0.cobertura_perfil", {c: int(base[c].notna().sum()) for c in ["pct_urbana", "pct_pretos_pardos", "pct_60mais", "pct_superior", "pct_evangelicos", "log_pib_pc", "agro_share", "bf_por_100hab"]})

    # ---------------- swing ----------------
    def swing(cargo, a0, a1):
        x0 = s[(s.ano == a0) & (s.cargo == cargo)][["uf", "mun", "ibge", "pct_dir", "pct_esq", "total"]]
        x1 = s[(s.ano == a1) & (s.cargo == cargo)][["uf", "mun", "ibge", "pct_dir", "pct_esq", "total"]]
        j = x0.merge(x1, on=["uf", "mun", "ibge"], suffixes=("_0", "_1"))
        j["swing_dir"] = j["pct_dir_1"] - j["pct_dir_0"]
        j["swing_esq"] = j["pct_esq_1"] - j["pct_esq_0"]
        j = j.merge(ap[(ap.ano == a1) & (ap.cargo == cargo)][["uf", "mun", "aptos"]], on=["uf", "mun"], how="left")
        return j
    sw = {}
    for cargo, nome in ((6, "deputado federal"), (3, "governador"), (5, "senador")):
        sw[(cargo, "26")] = swing(cargo, 2018 if cargo == 5 else 2022, 2026)
        sw[(cargo, "plac")] = swing(cargo, 2010 if cargo == 5 else 2018, 2018 if cargo == 5 else 2022)
    resumo = []
    for (cargo, tipo), j in sw.items():
        w = j["aptos"].fillna(1)
        wm = np.average(j["swing_dir"], weights=w)
        sd = np.sqrt(np.cov(j["swing_dir"], aweights=w))
        resumo.append({"cargo": cargo, "periodo": ("2018->2026" if cargo == 5 else "2022->2026") if tipo == "26" else ("2010->2018" if cargo == 5 else "2018->2022 (placebo de estabilidade)"), "municipios": len(j), "swing_direita_medio_ponderado_pp": round(wm, 2), "desvio_padrao_ponderado_pp": round(float(sd), 2), "pct_municipios_com_swing_positivo": round(100 * float((j.swing_dir > 0).mean()), 1), "pct_eleitorado_em_municipios_com_swing_positivo": round(100 * float(w[j.swing_dir > 0].sum() / w.sum()), 1)})
    r = pd.DataFrame(resumo)
    tabela("b1_swing_direita_resumo", r)
    registrar("b1.swing_direita_resumo", r.to_dict("records"))
    j6 = sw[(6, "26")]
    nacional = []
    for ano in (2018, 2022, 2026):
        x = s[(s.ano == ano) & (s.cargo == 6)]
        nacional.append({"ano": ano, "pct_direita_deputado_federal": round(100 * x.direita.sum() / x.total.sum(), 2), "pct_esquerda": round(100 * x.esquerda.sum() / x.total.sum(), 2), "pct_centro": round(100 * x.centro.sum() / x.total.sum(), 2)})
    registrar("b1.nacional_deputado_federal_municipios_com_perfil", nacional)
    # salva swing por municipio para o mapa
    j6.merge(base[["ibge", "nome_ibge"]], on="ibge")[["ibge", "uf", "nome_ibge", "pct_dir_0", "pct_dir_1", "swing_dir", "aptos"]].to_csv(RAIZ / "resultados/b1_swing_municipal_deputado_federal.csv", index=False)

    # ---------------- B2: o perfil acompanha o swing? ----------------
    vars_ = ["pct_urbana", "pct_pretos_pardos", "pct_60mais", "pct_superior", "pct_evangelicos", "pct_catolicos", "log_pib_pc", "agro_share", "bf_por_100hab"]
    linhas = []
    for cargo, nome in ((6, "deputado federal"), (3, "governador"), (5, "senador")):
        a = sw[(cargo, "26")].merge(base[["ibge"] + vars_], on="ibge", how="left")
        b = sw[(cargo, "plac")].merge(base[["ibge"] + vars_], on="ibge", how="left")
        a["P"], b["P"] = 1, 0
        dfl = pd.concat([a, b], ignore_index=True)
        dfl = dfl.dropna(subset=vars_ + ["swing_dir", "aptos"])
        dfl = dfl[dfl.aptos > 0]
        for v in vars_:
            dfl[v + "_z"] = (dfl[v] - dfl[v].mean()) / dfl[v].std()
        for v in vars_:
            dfl["g"] = dfl["uf"] + "_" + dfl["P"].astype(str)
            f = f"swing_dir ~ {v}_z + {v}_z:P + C(g)"
            mod = smf.wls(f, data=dfl, weights=dfl["aptos"]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(dfl["uf"])[0]})
            b0, b1 = mod.params[f"{v}_z"], mod.params[f"{v}_z:P"]
            ci0, ci1 = mod.conf_int().loc[f"{v}_z"].tolist(), mod.conf_int().loc[f"{v}_z:P"].tolist()
            linhas.append({"cargo": nome, "variavel": v, "coef_placebo_pp_por_desvio_padrao": round(b0, 3), "coef_2026_menos_placebo_pp": round(b1, 3), "ic95_diferenca_baixo": round(ci1[0], 3), "ic95_diferenca_alto": round(ci1[1], 3), "acompanha_mais_que_antes": bool(ci1[0] > 0 or ci1[1] < 0), "municipios": int((dfl.P == 1).sum())})
    b2 = pd.DataFrame(linhas)
    tabela("b2_perfil_x_swing_direita", b2)
    registrar("b2.perfil_x_swing", b2.to_dict("records"))

    # R2 do modelo (quanto do swing o perfil explica, dentro da UF)
    for cargo, nome in ((6, "deputado_federal"),):
        a = sw[(cargo, "26")].merge(base[["ibge"] + vars_], on="ibge", how="left").dropna(subset=vars_ + ["swing_dir", "aptos"])
        a = a[a.aptos > 0]
        m0 = smf.wls("swing_dir ~ C(uf)", data=a, weights=a["aptos"]).fit()
        m1 = smf.wls("swing_dir ~ C(uf) + " + " + ".join(vars_), data=a, weights=a["aptos"]).fit()
        registrar("b2.r2_modelo_deputado_federal", {"so_uf": round(m0.rsquared, 3), "uf_mais_perfil": round(m1.rsquared, 3), "ganho_do_perfil": round(m1.rsquared - m0.rsquared, 3)})

    # ---------------- B3: abstencao ----------------
    a6 = ap[ap.cargo == 6].copy()
    nac = a6.groupby("ano")[["aptos", "comparecimento", "abstencoes"]].sum()
    nac["abstencao_pct"] = (100 * nac["abstencoes"] / nac["aptos"]).round(2)
    nac["comparecimento_pct"] = (100 * nac["comparecimento"] / nac["aptos"]).round(2)
    tabela("b3_abstencao_nacional", nac.reset_index())
    registrar("b3.abstencao_nacional", nac.reset_index().to_dict("records"))
    # contrafactual: votos de 2026 reponderados pelo comparecimento de 2022 (proporcoes de voto mantidas em cada municipio)
    x26 = s[(s.ano == 2026) & (s.cargo == 6)].merge(a6[a6.ano == 2026][["uf", "mun", "aptos", "comparecimento"]], on=["uf", "mun"])
    x22 = a6[a6.ano == 2022][["uf", "mun", "aptos", "comparecimento"]].rename(columns={"aptos": "aptos22", "comparecimento": "comp22"})
    x = x26.merge(x22, on=["uf", "mun"])
    x["taxa26"] = x.comparecimento / x.aptos
    x["taxa22"] = x.comp22 / x.aptos22
    x["fator"] = x["taxa22"] / x["taxa26"]
    real = 100 * x.direita.sum() / x.total.sum()
    cf = 100 * (x.direita * x.fator).sum() / (x.total * x.fator).sum()
    registrar("b3.contrafactual_comparecimento_2022", {"direita_pct_real_2026": round(real, 3), "direita_pct_com_comparecimento_de_2022": round(cf, 3), "diferenca_pp": round(cf - real, 3), "municipios": int(len(x))})
    # abstencao x swing
    a = sw[(6, "26")].merge(a6[a6.ano == 2026][["uf", "mun", "aptos", "abstencoes"]].rename(columns={"aptos": "ap26", "abstencoes": "ab26"}), on=["uf", "mun"]).merge(a6[a6.ano == 2022][["uf", "mun", "aptos", "abstencoes"]].rename(columns={"aptos": "ap22", "abstencoes": "ab22"}), on=["uf", "mun"])
    a["var_abst"] = 100 * (a.ab26 / a.ap26 - a.ab22 / a.ap22)
    mod = smf.wls("swing_dir ~ var_abst + C(uf)", data=a.dropna(), weights=a.dropna()["aptos"]).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(a.dropna()["uf"])[0]})
    registrar("b3.abstencao_x_swing_direita", {"coef_pp_por_pp": round(mod.params["var_abst"], 3), "ic95": [round(v, 3) for v in mod.conf_int().loc["var_abst"].tolist()], "municipios": int(len(a.dropna()))})

    # ---------------- B4: arrasto ----------------
    linhas = []
    for ano in (2018, 2022, 2026):
        pres = s[(s.ano == ano) & (s.cargo == 1)][["uf", "mun", "pct_pl_pres"]]
        for cargo, nome in ((6, "deputado federal"), (3, "governador"), (5, "senador")):
            if cargo == 5 and ano == 2022:
                continue
            c = s[(s.ano == ano) & (s.cargo == cargo)][["uf", "mun", "pct_dir"]].merge(pres, on=["uf", "mun"]).merge(ap[(ap.ano == ano) & (ap.cargo == cargo)][["uf", "mun", "aptos"]], on=["uf", "mun"])
            rs, ws = [], []
            for uf, g in c.groupby("uf"):
                if len(g) >= 5 and g.pct_dir.std() > 0 and g.pct_pl_pres.std() > 0:
                    rs.append(np.corrcoef(g.pct_dir, g.pct_pl_pres)[0, 1]); ws.append(g.aptos.sum())
            linhas.append({"ano": ano, "cargo": nome, "ufs": len(rs), "correlacao_media_ponderada_por_uf": round(float(np.average(rs, weights=ws)), 3)})
    b4 = pd.DataFrame(linhas)
    tabela("b4_arrasto", b4)
    registrar("b4.arrasto", b4.to_dict("records"))
    print("ok B")


if __name__ == "__main__":
    main()
