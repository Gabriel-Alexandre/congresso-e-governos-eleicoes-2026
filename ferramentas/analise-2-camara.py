"""Bloco A (Camara): A1 cadeiras por partido e campo, A4 renovacao e nomes, A5 puxadores, D5 incumbentes, D6 votos x cadeiras.

Criterios: docs/PRE_REGISTRO.md secoes 1, 2, 5, 6 e 11. Todo numero vai para resultados/RESUMO.json.
"""
from __future__ import annotations

import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos, identidade  # noqa: E402
from congresso.cadeiras import distribuir, montar_listas, preparar  # noqa: E402
from congresso.comum import DER, RAIZ, UFS, eleito, votos_cand, votos_partido  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

TSE = RAIZ / "dados" / "brutos" / "tse"
ANOS = (2006, 2010, 2014, 2018, 2022, 2026)
# renomeacoes simples de partido (a mesma legenda com outro nome), para a volatilidade
SUCESSOR = {"PMDB": "MDB", "PRB": "REPUBLICANOS", "PR": "PL", "PTN": "PODE", "PODEMOS": "PODE", "PT DO B": "AVANTE", "PC DO B": "PCDOB",
            "SD": "SOLIDARIEDADE", "PATRI": "PATRIOTA", "PEN": "PATRIOTA", "PFL": "DEM", "PPB": "PP", "PPS": "CIDADANIA", "PMN": "MOBILIZA", "PTC": "AGIR"}


def nome_norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", "", s).strip()


def sig(p: str) -> str:
    n = campos.sigla(p)
    return SUCESSOR.get(n, n)


_ID = None


def _ids():
    """Identidade de pessoa (congresso/identidade.py): mesma data de nascimento e um nome igual (civil, urna, social ou parlamentar)."""
    global _ID
    if _ID is None:
        plen = pd.read_parquet(DER / "plenario_deputados.parquet")
        _ID = identidade.resolver(camara=plen[["id", "nomeCivil", "nome", "dataNascimento"]])
    return _ID


def consulta(ano: int) -> pd.DataFrame:
    """sq do candidato a deputado federal -> chave de pessoa."""
    sq, _ = _ids()
    return pd.DataFrame([(s, p) for (a, s), p in sq.items() if a == ano], columns=["sq", "chave"])


def chave_camara(ids: pd.Series) -> pd.Series:
    _, cm = _ids()
    return ids.map(cm)


def main() -> None:
    cand = votos_cand()
    part = votos_partido()
    c6 = cand[cand["cargo"] == 6]
    pc = c6.groupby(["ano", "uf", "sq", "nome", "partido", "fed", "sit"], as_index=False)["votos"].sum()
    pc["eleito"] = eleito(pc["sit"])
    pc["sig"] = pc["partido"].map(sig)

    # ---------------- R1 com pesos das fusoes ----------------
    seats = pc[pc.eleito].groupby(["ano", "sig"]).size()
    pesos = {
        "DEM": int(seats.get((2018, "DEM"), 0)), "PSL": int(seats.get((2018, "PSL"), 0)),
        "PTB": int(seats.get((2022, "PTB"), 0)), "Patriota": int(seats.get((2022, "PATRIOTA"), 0)),
    }
    registrar("a1.pesos_fusoes", pesos)

    def nota(p):
        return campos.nota_r1(p, pesos)

    nota_por_sig = {s: nota(s) for s in pc["sig"].unique()}
    pc["nota_r1"] = pc["sig"].map(nota_por_sig)
    tabela("a1_escala_r1_usada", pd.DataFrame({"partido": list(nota_por_sig), "nota_r1": list(nota_por_sig.values())}).sort_values("nota_r1"))

    # ---------------- A1: cadeiras por partido e ano ----------------
    el = pc[pc.eleito]
    cad = el.groupby(["ano", "sig"]).size().unstack(0).fillna(0).astype(int)
    tabela("a1_cadeiras_por_partido_e_ano", cad.reset_index())
    registrar("a1.total_cadeiras_por_ano", el.groupby("ano").size().to_dict())
    for ano in (2018, 2022, 2026):
        registrar(f"a1.cadeiras_{ano}", cad[ano].sort_values(ascending=False).head(12).to_dict())

    # federacao (lista) de 2022 e 2026
    def lista(df):
        return df["fed"].where(~df["fed"].fillna("#NULO").str.startswith("#"), df["partido"])
    for ano in (2022, 2026):
        x = el[el.ano == ano]
        registrar(f"a1.cadeiras_por_lista_{ano}", x.groupby(lista(x)).size().sort_values(ascending=False).head(10).to_dict())

    # votos por partido (nominais + legenda)
    nom = pc.groupby(["ano", "sig"])["votos"].sum()
    p2 = part[part["cargo"] == 6].copy()
    p2["sig"] = p2["partido"].map(sig)
    leg = p2.groupby(["ano", "sig"])[["leg", "conv"]].sum().sum(axis=1)
    vot = nom.add(leg, fill_value=0).unstack(0).fillna(0)
    pct_v = vot / vot.sum()
    pct_c = cad / cad.sum()
    tabela("a1_votos_pct_por_partido_e_ano", pct_v.reset_index())

    # volatilidade de Pedersen e numero efetivo de partidos
    linhas = []
    for a, b in zip(ANOS[:-1], ANOS[1:]):
        vv = (pct_v[a].reindex(pct_v.index.union(pct_v.index)).fillna(0) - pct_v[b].fillna(0)).abs().sum() / 2
        vc = (pct_c[a].fillna(0) - pct_c[b].fillna(0)).abs().sum() / 2
        linhas.append({"de": a, "para": b, "volatilidade_votos": round(vv, 4), "volatilidade_cadeiras": round(vc, 4)})
    vol = pd.DataFrame(linhas)
    tabela("a1_volatilidade", vol)
    registrar("a1.volatilidade", vol.to_dict("records"))
    nep = pd.DataFrame({"ano": list(ANOS), "nep_votos": [round(1 / (pct_v[a] ** 2).sum(), 2) for a in ANOS], "nep_cadeiras": [round(1 / (pct_c[a] ** 2).sum(), 2) for a in ANOS]})
    tabela("a1_nep", nep)
    registrar("a1.nep", nep.to_dict("records"))

    # ---------------- A1: campos por R1 (com sensibilidade) ----------------
    def campo_tab(cortes):
        out = []
        for ano in (2018, 2022, 2026):
            x = el[el.ano == ano]
            camp = x["nota_r1"].map(lambda n: campos.campo_r1(n, cortes))
            vc = camp.value_counts()
            vp = pd.Series({s: pct_v.loc[s, ano] for s in pct_v.index if pct_v.loc[s, ano] > 0}).rename("v")
            vcamp = vp.groupby(vp.index.map(lambda s: campos.campo_r1(nota_por_sig.get(s) if s in nota_por_sig else nota(s), cortes))).sum()
            for k in ("esquerda", "centro", "direita", "sem classificacao"):
                out.append({"ano": ano, "cortes": f"{cortes[0]}-{cortes[1]}", "campo": k, "cadeiras": int(vc.get(k, 0)), "pct_cadeiras": round(100 * vc.get(k, 0) / len(x), 2), "pct_votos": round(100 * vcamp.get(k, 0), 2)})
        return pd.DataFrame(out)
    t1 = pd.concat([campo_tab((4.0, 6.0)), campo_tab((3.5, 5.5)), campo_tab((4.5, 6.5))])
    tabela("a1_campo_r1", t1)
    registrar("a1.campo_r1", t1.to_dict("records"))

    # ---------------- R3: coligacao presidencial formal ----------------
    def r3_partido(ano):
        z = zipfile.ZipFile(TSE / f"consulta_cand_{ano}.zip")
        nm = [i.filename for i in z.infolist() if i.filename.endswith("_BR.csv")][0]
        with z.open(nm) as fh:
            d = pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str)
        d = d[d["CD_CARGO"] == "1"].drop_duplicates("NM_URNA_CANDIDATO")
        mapa = {}
        for r in d.itertuples():
            txt = campos._norm(r.DS_COMPOSICAO_COLIGACAO).replace("PC DO B", "PCDOB")
            toks = {t for t in re.split(r"[^A-Z0-9]+", txt) if t}
            principal = r.NM_URNA_CANDIDATO
            for t in toks:
                mapa.setdefault(t, set()).add(principal)
        return mapa, d
    r3 = {}
    for ano, bols, pt in ((2026, "FLAVIO", "LULA"), (2022, "JAIR", "LULA"), (2018, "JAIR", "FERNANDO")):
        mapa, d = r3_partido(ano)
        r3[ano] = (mapa, bols, pt)

    def classe_r3(ano, partido):
        mapa, bols, pt = r3[ano]
        p = campos._norm(partido)
        p = {"PCDOB": "PCDOB", "PC DO B": "PCDOB"}.get(p, p)
        cs = {c for c in mapa.get(p, set())}
        if any(bols in c for c in cs):
            return "coligacao do candidato do PL/PSL"
        if any(pt in c for c in cs):
            return "coligacao do candidato do PT"
        if cs:
            return "coligacao de outro presidenciavel"
        return "sem candidato presidencial"
    linhas = []
    for ano in (2018, 2022, 2026):
        x = el[el.ano == ano]
        cl = x["partido"].map(lambda p: classe_r3(ano, p))
        for k, n in cl.value_counts().items():
            linhas.append({"ano": ano, "classe_r3": k, "cadeiras": int(n), "pct_cadeiras": round(100 * n / len(x), 2)})
    t3 = pd.DataFrame(linhas)
    tabela("a1_campo_r3", t3)
    registrar("a1.campo_r3", t3.to_dict("records"))

    # ---------------- ligacao com deputados (nome civil + nascimento) ----------------
    ci = {a: consulta(a) for a in (2018, 2022, 2026)}
    plen = pd.read_parquet(DER / "plenario_deputados.parquet")
    plen["chave"] = chave_camara(plen["id"])
    plen_u = plen.drop_duplicates("chave")
    for a in ci:
        ci[a] = ci[a].drop_duplicates("sq")
    el26 = el[el.ano == 2026].merge(ci[2026][["sq", "chave"]], on="sq", how="left")
    el22 = el[el.ano == 2022].merge(ci[2022][["sq", "chave"]], on="sq", how="left")
    el18 = el[el.ano == 2018].merge(ci[2018][["sq", "chave"]], on="sq", how="left")

    # ---------------- R2 nas coortes de 2022 e 2026 ----------------
    base = plen_u.copy()
    em_ex = base[base.em_exercicio_30_09]
    # classe do partido = mediana da taxa dos deputados do partido na vespera
    base["sig_vespera"] = base["partido_vespera"].map(sig)
    med = base[base.n_validos >= 50].groupby("sig_vespera")["taxa"].median()
    classe_part = med.map(lambda t: "governista" if t >= 0.70 else ("oposicao" if t <= 0.40 else "independente"))
    registrar("a1.r2_partidos_classe", classe_part.to_dict())
    registrar("a1.r2_partidos_mediana", med.round(3).to_dict())
    registrar("a1.r2_deputados_exercicio_classe", em_ex.classe_r2.value_counts().to_dict())
    indiv = base.set_index("chave")["classe_r2"].to_dict()

    def r2_coorte(df, ano):
        cls = []
        for r in df.itertuples():
            c = indiv.get(r.chave)
            if c is not None and c != "sem classificacao":
                cls.append(("individual", c))
            elif ano == 2026:
                cp = classe_part.get(r.sig)
                cls.append(("partido", cp if cp is not None else "sem classificacao"))
            else:
                cls.append(("nao ligado", "sem classificacao"))
        return pd.DataFrame(cls, columns=["origem", "classe"])
    linhas = []
    for ano, df in ((2022, el22), (2026, el26)):
        r = r2_coorte(df, ano)
        for (o, k), n in r.groupby(["origem", "classe"]).size().items():
            linhas.append({"coorte": ano, "origem": o, "classe_r2": k, "cadeiras": int(n)})
        tot = r.classe.value_counts()
        registrar(f"a1.r2_coorte_{ano}", tot.to_dict())
    t2 = pd.DataFrame(linhas)
    tabela("a1_campo_r2", t2)

    # ---------------- bancada na vespera x eleita; de onde veio o ganho ----------------
    vesp = em_ex.copy()
    vesp["sig"] = vesp["partido_vespera"].map(sig)
    bv = vesp.groupby("sig").size()
    be = cad[2026]
    comp = pd.DataFrame({"vespera": bv, "eleita_2026": be, "eleita_2022": cad[2022]}).fillna(0).astype(int)
    comp["var_vs_vespera"] = comp["eleita_2026"] - comp["vespera"]
    comp["var_vs_2022"] = comp["eleita_2026"] - comp["eleita_2022"]
    tabela("a1_bancada_vespera_vs_eleita", comp.reset_index().rename(columns={"index": "partido"}).sort_values("eleita_2026", ascending=False))
    registrar("a1.bancada_vespera_soma", int(bv.sum()))
    # origem das cadeiras de 2026: reeleito do mesmo partido, reeleito vindo de outro partido, entrante
    vmap = vesp.set_index("chave")["sig"].to_dict()
    p22 = el22.set_index("chave")["sig"].to_dict()
    orig = []
    for r in el26.itertuples():
        v = vmap.get(r.chave)
        d22 = p22.get(r.chave)
        if v is not None or d22 is not None:
            if v is not None and v == r.sig:
                o = "reeleito, mesmo partido da vespera"
            elif v is not None:
                o = "reeleito, veio de outro partido"
            elif d22 == r.sig:
                o = "ex-titular de 2022, mesmo partido"
            else:
                o = "ex-titular de 2022, veio de outro partido"
        else:
            o = "entrante (nao estava na vespera nem foi eleito em 2022)"
        orig.append({"sig": r.sig, "origem": o})
    og = pd.DataFrame(orig).groupby(["sig", "origem"]).size().unstack(1).fillna(0).astype(int)
    tabela("a1_origem_das_cadeiras_2026", og.reset_index())
    registrar("a1.origem_cadeiras_2026_total", pd.DataFrame(orig).origem.value_counts().to_dict())
    for s in ("PL", "PT", "UNIAO", "PP", "PSD", "REPUBLICANOS", "MDB", "PODE"):
        if s in og.index:
            registrar(f"a1.origem_cadeiras_2026_partido.{s}", og.loc[s].to_dict())

    # ---------------- A4: renovacao ----------------
    ex_set = set(vesp["chave"])
    nova = el26["chave"].map(lambda k: k not in ex_set).mean()
    registrar("a4.pct_eleitos_que_nao_estavam_em_exercicio", round(100 * nova, 2))
    transicoes = {}
    for (a0, a1, df0, df1) in ((2018, 2022, el18, el22), (2022, 2026, el22, el26)):
        cand1 = pc[pc.ano == a1].merge(ci[a1][["sq", "chave"]], on="sq", how="left")
        ran = cand1.groupby("chave").agg(votos=("votos", "sum"), eleito=("eleito", "max"), sig=("sig", "first"))
        base0 = df0[["chave", "sig", "nota_r1", "votos"]].dropna(subset=["chave"])
        j = base0.merge(ran, left_on="chave", right_index=True, how="left", suffixes=("_0", "_1"))
        j["tentou"] = j["eleito"].notna()
        j["reeleito"] = j["eleito"].fillna(False).astype(bool)
        j["campo_0"] = j["nota_r1"].map(campos.campo_r1)
        for camp, g in [("todos", j)] + list(j.groupby("campo_0")):
            transicoes[(a0, a1, camp)] = {
                "eleitos_na_eleicao_anterior": int(len(g)), "tentaram_de_novo": int(g.tentou.sum()), "reeleitos": int(g.reeleito.sum()),
                "pct_tentou": round(100 * g.tentou.mean(), 2) if len(g) else None,
                "pct_reeleito_entre_os_que_tentaram": round(100 * g.reeleito.sum() / max(g.tentou.sum(), 1), 2),
                "pct_reeleito_entre_todos": round(100 * g.reeleito.mean(), 2) if len(g) else None,
            }
        if a1 == 2026:
            j2 = j[j.tentou & j.reeleito].copy()
            j2["razao"] = j2["votos_1"] / j2["votos_0"]
            j2 = j2.merge(el26[["chave", "nome", "uf", "partido"]], on="chave", how="left")
            tabela("a4_reeleitos_maiores_quedas_2022_2026", j2.sort_values("razao").head(25)[["nome", "uf", "partido", "votos_0", "votos_1", "razao"]])
            tabela("a4_reeleitos_maiores_altas_2022_2026", j2.sort_values("razao", ascending=False).head(25)[["nome", "uf", "partido", "votos_0", "votos_1", "razao"]])
            registrar("a4.mediana_razao_votos_reeleitos_2026_sobre_2022", round(float(j2["razao"].median()), 3))
            registrar("a4.pct_reeleitos_com_queda_de_votos", round(100 * float((j2["razao"] < 1).mean()), 2))
    t = pd.DataFrame([{"de": k[0], "para": k[1], "campo_r1_na_eleicao_anterior": k[2], **v} for k, v in transicoes.items()])
    tabela("d5_reeleicao_deputados", t)
    registrar("d5.reeleicao_deputados", t.to_dict("records"))

    # notaveis (c): 30 mais votados de 2022 e de 2018 e o que aconteceu com eles
    for a0, a1 in ((2018, 2022), (2022, 2026)):
        top = pc[pc.ano == a0].merge(ci[a0][["sq", "chave"]], on="sq", how="left").sort_values("votos", ascending=False).head(30)
        cand1 = pc[pc.ano == a1].merge(ci[a1][["sq", "chave"]], on="sq", how="left").groupby("chave").agg(votos1=("votos", "sum"), eleito1=("eleito", "max"), uf1=("uf", "first"), part1=("partido", "first"))
        r = top.merge(cand1, left_on="chave", right_index=True, how="left")
        r["resultado"] = np.where(r.eleito1.isna(), "nao disputou deputado federal", np.where(r.eleito1, "eleito", "nao eleito"))
        tabela(f"a4_trinta_mais_votados_{a0}_e_o_que_houve_em_{a1}", r[["nome", "uf", "partido", "votos", "resultado", "votos1", "part1"]])
        registrar(f"a4.trinta_mais_votados_{a0}.resultado_em_{a1}", r["resultado"].value_counts().to_dict())

    # ---------------- A5: puxadores ----------------
    linhas = []
    for ano in (2026, 2022):
        prep = preparar(cand, part, ano)
        LS = {uf: montar_listas(prep=prep, uf=uf) for uf in UFS}
        vagas = {uf: int(pc[(pc.ano == ano) & (pc.uf == uf) & pc.eleito].shape[0]) for uf in UFS}
        topo = pc[pc.ano == ano].sort_values("votos", ascending=False).head(15)
        base_res = {uf: distribuir(LS[uf], vagas[uf], 0.8, 0.2) for uf in topo.uf.unique()}
        for r in topo.itertuples():
            L = LS[r.uf]
            chave_l = campos and (r.fed if isinstance(r.fed, str) and not r.fed.startswith("#") else r.partido)
            kl = f"FED:{r.fed}" if isinstance(r.fed, str) and not r.fed.startswith("#") else r.partido
            res0 = base_res[r.uf]
            n0 = sum(1 for c in L[kl]["cands"] if c[0] in res0.eleitos)
            qe = res0.qe
            # versao 2: sem o candidato
            L2 = {k: {"votos": v["votos"], "cands": list(v["cands"])} for k, v in L.items()}
            L2[kl]["votos"] -= r.votos
            L2[kl]["cands"] = [c for c in L2[kl]["cands"] if c[0] != r.sq]
            res2 = distribuir(L2, vagas[r.uf], 0.8, 0.2)
            n2 = sum(1 for c in L2[kl]["cands"] if c[0] in res2.eleitos)
            # versao 1: so o quociente eleitoral conta (o excedente sai)
            L1 = {k: {"votos": v["votos"], "cands": list(v["cands"])} for k, v in L.items()}
            exc = max(r.votos - qe, 0)
            L1[kl]["votos"] -= exc
            L1[kl]["cands"] = [(c[0], c[1] - exc) if c[0] == r.sq else c for c in L1[kl]["cands"]]
            res1 = distribuir(L1, vagas[r.uf], 0.8, 0.2)
            n1 = sum(1 for c in L1[kl]["cands"] if c[0] in res1.eleitos)
            lista_votos_nom = sum(c[1] for c in L[kl]["cands"])
            linhas.append({
                "ano": ano, "candidato": r.nome, "uf": r.uf, "partido": r.partido, "votos": int(r.votos),
                "pct_da_lista": round(100 * r.votos / lista_votos_nom, 2), "cadeiras_da_lista": n0,
                "cadeiras_sem_o_excedente": n1, "cadeiras_sem_o_candidato": n2, "cadeiras_a_mais_pelo_candidato": n0 - n2,
                "quociente_eleitoral_uf": int(qe), "votos_em_quocientes": round(r.votos / qe, 2),
            })
    a5 = pd.DataFrame(linhas)
    tabela("a5_puxadores", a5)
    registrar("a5.puxadores", a5.to_dict("records"))

    # sensibilidade a regra de sobras em 2026
    prep = preparar(cand, part, 2026)
    LS = {uf: montar_listas(prep=prep, uf=uf) for uf in UFS}
    oficial = pc[(pc.ano == 2026) & pc.eleito].groupby("uf")["sq"].apply(set)
    variantes = {"lei 14.211 (80% e 20% nas sobras): regra aplicada": (0.8, 0.2), "todos os partidos, candidato com 10%": (0.0, 0.1), "todos os partidos e candidatos": (0.0, 0.0)}
    sq_part = pc[pc.ano == 2026].set_index("sq")["sig"].to_dict()
    resv = {}
    for nome, (fl, fc) in variantes.items():
        eleitos = set()
        for uf in UFS:
            eleitos |= distribuir(LS[uf], len(oficial[uf]), fl, fc).eleitos
        resv[nome] = pd.Series([sq_part[s] for s in eleitos]).value_counts()
    sens = pd.DataFrame(resv).fillna(0).astype(int)
    sens["dif_vs_aplicada_todos_partidos_10pct"] = sens.iloc[:, 1] - sens.iloc[:, 0]
    sens["dif_vs_aplicada_todos_e_todos"] = sens.iloc[:, 2] - sens.iloc[:, 0]
    tabela("a5_sensibilidade_regra_sobras_2026", sens.reset_index().rename(columns={"index": "partido"}).sort_values(sens.columns[0], ascending=False))
    registrar("a5.sobras.cadeiras_que_mudam_de_partido_todos_partidos_10pct", int(sens["dif_vs_aplicada_todos_partidos_10pct"].clip(lower=0).sum()))
    registrar("a5.sobras.cadeiras_que_mudam_de_partido_todos_e_todos", int(sens["dif_vs_aplicada_todos_e_todos"].clip(lower=0).sum()))
    registrar("a5.sobras.ganhadores_perdedores_todos_partidos_10pct", sens["dif_vs_aplicada_todos_partidos_10pct"][sens["dif_vs_aplicada_todos_partidos_10pct"] != 0].to_dict())

    # ---------------- D6: votos x cadeiras por campo (mesma tabela da A1, cortes 4,0-6,0) ----------------
    d6 = t1[t1["cortes"] == "4.0-6.0"][["ano", "campo", "pct_votos", "pct_cadeiras"]].copy()
    d6["cadeiras_menos_votos_pp"] = (d6["pct_cadeiras"] - d6["pct_votos"]).round(2)
    tabela("d6_votos_x_cadeiras_por_campo", d6)
    registrar("d6.por_campo", d6.to_dict("records"))
    linhas = []
    for ano in (2018, 2022, 2026):
        for s_ in cad.index:
            if cad.loc[s_, ano] or pct_v.loc[s_, ano] > 0.001:
                linhas.append({"ano": ano, "partido": s_, "nota_r1": nota_por_sig.get(s_), "pct_votos": round(100 * pct_v.loc[s_, ano], 2), "pct_cadeiras": round(100 * pct_c.loc[s_, ano], 2)})
    tabela("d6_votos_x_cadeiras_por_partido", pd.DataFrame(linhas))
    pl_ = {int(a_): {"pct_votos": round(100 * pct_v.loc["PL", a_], 2), "pct_cadeiras": round(100 * pct_c.loc["PL", a_], 2), "cadeiras": int(cad.loc["PL", a_])} for a_ in (2018, 2022, 2026)}
    registrar("a1.pl_serie", pl_)
    # R2: sensibilidade (65% e 45%)
    sens_r2 = []
    for hi, lo in ((0.70, 0.40), (0.65, 0.45)):
        def cls(t):
            return "governista" if t >= hi else ("oposicao" if t <= lo else "independente")
        cp = med.map(cls)
        for ano, df in ((2022, el22), (2026, el26)):
            ct = {"governista": 0, "independente": 0, "oposicao": 0, "sem classificacao": 0}
            for r in df.itertuples():
                row = base[base.chave == r.chave]
                if len(row) and row.iloc[0].n_validos >= 50:
                    ct[cls(row.iloc[0].taxa)] += 1
                elif ano == 2026 and r.sig in cp.index:
                    ct[cp[r.sig]] += 1
                else:
                    ct["sem classificacao"] += 1
            sens_r2.append({"cortes_governista_oposicao": f"{hi}/{lo}", "coorte": ano, **ct})
    tabela("a1_campo_r2_sensibilidade", pd.DataFrame(sens_r2))
    registrar("a1.r2_sensibilidade", sens_r2)
    print("ok A1/A4/A5/D5/D6")


if __name__ == "__main__":
    main()
