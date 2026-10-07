"""D3: voto em votacoes de grande atencao no plenario x desempenho eleitoral do deputado em 2026.

Criterios: docs/PRE_REGISTRO.md secao 8 e emendas 5 e 6 da secao 15 (votacoes disponiveis e placebo escolhido por regra).
Desenho: deputados que votaram e disputaram deputado federal em 2026, comparados DENTRO do mesmo partido e UF
(efeito fixo partido x UF), controlando o log dos votos de 2022. Erro padrao por UF. Benjamini-Hochberg a 5% entre V1 e V4.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso.comum import DER, RAIZ, eleito, ler_camara, votos_cand  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("a2", Path(__file__).resolve().parent / "analise-2-camara.py")
a2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a2)

VOTACOES = {
    "V1 PEC 3/2021 (blindagem), 1o turno, 16/09/2025": "2270800-135",
    "V4 Emendas do Senado ao PLP 177/2023 (numero de deputados), 25/06/2025": "2383019-91",
    "P placebo: 'Mantido o texto', 16/12/2025 (423 x 23)": "2438459-141",
}


def bh(p):
    p = np.asarray(p, float)
    o = np.argsort(p)
    q = np.empty_like(p)
    n = len(p)
    q[o] = np.minimum.accumulate((p[o] * n / (np.arange(n) + 1))[::-1])[::-1]
    return np.minimum(q, 1)


def main() -> None:
    cand = votos_cand()
    c6 = cand[cand["cargo"] == 6]
    pc = c6.groupby(["ano", "uf", "sq", "nome", "partido", "sit"], as_index=False)["votos"].sum()
    pc["eleito"] = eleito(pc["sit"])
    ci = {a: a2.consulta(a) for a in (2022, 2026)}
    for a in ci:
        ci[a] = ci[a].drop_duplicates("sq")
    p26 = pc[pc.ano == 2026].merge(ci[2026][["sq", "chave"]], on="sq").groupby("chave").agg(uf26=("uf", "first"), partido26=("partido", "first"), votos26=("votos", "sum"), eleito=("eleito", "max")).reset_index()
    p22 = pc[pc.ano == 2022].merge(ci[2022][["sq", "chave"]], on="sq").groupby("chave").agg(votos22=("votos", "sum")).reset_index()
    plen = pd.read_parquet(DER / "plenario_deputados.parquet")
    plen["chave"] = plen["nomeCivil"].map(a2.nome_norm) + "|" + plen["dataNascimento"]
    plen = plen.drop_duplicates("chave")
    d3 = pd.read_parquet(DER / "votos_d3.parquet")
    # a votacao placebo nao esta em votos_d3 (selecionada depois): ler direto
    extra = pd.concat([ler_camara("votacoesVotos", 2025)])
    extra = extra[extra.idVotacao == "2438459-141"].rename(columns={"deputado_id": "id", "deputado_siglaPartido": "partido", "deputado_siglaUf": "uf"})[["idVotacao", "id", "voto", "partido", "uf"]]
    d3 = pd.concat([d3[d3.idVotacao != "2438459-141"], extra], ignore_index=True)

    base = plen[["id", "chave", "classe_r2", "taxa"]].merge(p26, on="chave", how="left").merge(p22, on="chave", how="left")
    registrar("d3.deputados_na_base_plenario", int(len(base)))
    linhas, desc = [], []
    ps = []
    for nome, vid in VOTACOES.items():
        v = d3[d3.idVotacao == vid][["id", "voto"]]
        v = v[v.voto.isin(["Sim", "Não"])].copy()
        v["sim"] = (v.voto == "Sim").astype(int)
        x = v.merge(base, on="id", how="left")
        x["tentou"] = x["votos26"].notna()
        desc.append({"votacao": nome, "votaram_sim_nao": int(len(x)), "sim": int(x.sim.sum()), "nao": int((1 - x.sim).sum()), "disputaram_dep_federal_2026": int(x.tentou.sum()),
                     "pct_eleitos_entre_os_que_disputaram_sim": round(100 * x[x.tentou & (x.sim == 1)].eleito.astype(float).mean(), 1) if (x.tentou & (x.sim == 1)).any() else None,
                     "pct_eleitos_entre_os_que_disputaram_nao": round(100 * x[x.tentou & (x.sim == 0)].eleito.astype(float).mean(), 1) if (x.tentou & (x.sim == 0)).any() else None})
        y = x[x.tentou].copy()
        y["eleito"] = y["eleito"].astype(float)
        y["lv22"] = np.log(y["votos22"].astype(float))
        y["lrazao"] = np.log(y["votos26"].astype(float) / y["votos22"].astype(float))
        y.loc[~np.isfinite(y["lrazao"]), "lrazao"] = np.nan
        y.loc[~np.isfinite(y["lv22"]), "lv22"] = np.nan
        y["grp"] = y["partido26"] + "_" + y["uf26"]
        for desfecho, rotulo in (("eleito", "eleito em 2026"), ("lrazao", "log(votos 2026 / votos 2022)")):
            z = y.dropna(subset=[desfecho] + (["lv22"] if desfecho == "eleito" else []))
            z = z.dropna(subset=["lv22"]) if desfecho == "eleito" else z
            # so entram grupos com 2+ deputados e variacao no voto
            ok = z.groupby("grp").filter(lambda g: len(g) >= 2 and g.sim.nunique() > 1)
            if len(ok) < 30 or ok.sim.nunique() < 2:
                linhas.append({"votacao": nome, "desfecho": rotulo, "n": int(len(ok)), "grupos": int(ok.grp.nunique()), "coef_sim": None, "ic95_baixo": None, "ic95_alto": None, "p": None})
                continue
            f = f"{desfecho} ~ sim + lv22 + C(grp)" if desfecho == "eleito" else f"{desfecho} ~ sim + C(grp)"
            mod = smf.ols(f, data=ok).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(ok["uf26"])[0]})
            ci_ = mod.conf_int().loc["sim"].tolist()
            linhas.append({"votacao": nome, "desfecho": rotulo, "n": int(len(ok)), "grupos": int(ok.grp.nunique()), "coef_sim": round(float(mod.params["sim"]), 4), "ic95_baixo": round(ci_[0], 4), "ic95_alto": round(ci_[1], 4), "p": round(float(mod.pvalues["sim"]), 4)})
    res = pd.DataFrame(linhas)
    comp = res[res.votacao.str.startswith(("V1", "V4"))].dropna(subset=["p"])
    for des, g in comp.groupby("desfecho"):
        res.loc[g.index, "p_bh_v1_v4"] = np.round(bh(g.p.values), 4)
    tabela("d3_voto_x_desempenho", res)
    tabela("d3_descricao_das_votacoes", pd.DataFrame(desc))
    registrar("d3.descricao", desc)
    registrar("d3.modelos", res.to_dict("records"))
    print(res.to_string())


if __name__ == "__main__":
    main()
