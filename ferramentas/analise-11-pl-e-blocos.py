"""Bloco E: o PL no centro da analise, com os campos pela AUTODECLARACAO dos partidos (emenda de 07/out, a pedido do autor).

Parametro principal desta rodada (docs/PRE_REGISTRO.md secao 15, emenda E1, depois de ver os resultados):
cada partido no grupo em que ele mesmo se declara (Valor Economico, ago/2026, capturado em dados/brutos/capturas):
  direita            PL ("direita conservadora"), Novo ("direita"), Missao ("direita tecno-otimista")
  centro-direita     PP, Republicanos, Uniao Brasil, PRD
  centro             MDB, PSD, Solidariedade, Avante, Mobiliza, Democrata, PSDB e Cidadania ("centro-democratico"),
                     Agir ("centro-progressista"), e os que nao se declaram no eixo: Podemos, DC, PRTB
  centro-esquerda    PSB, PDT, Rede
  esquerda           PT, PCdoB, PV, PSOL, PCB, PSTU, UP, PCO
Sigla antiga entra no grupo do partido que a herdou (PSL e DEM -> Uniao; PTB e Patriota -> PRD; PR -> PL; PSC -> Podemos ...).

Saidas: resultados/e*_*.csv e chaves e1..e7 em RESUMO.json.
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
from congresso import campos  # noqa: E402
from congresso.comum import DER, RAIZ, RES, eleito, votos_cand  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

TSE = RAIZ / "dados" / "brutos" / "tse"

GRUPOS = ["direita", "centro-direita", "centro", "centro-esquerda", "esquerda"]
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
FONTE_AUTO = "Valor Economico, ago/2026 (como cada partido se define), capturado em dados/brutos/capturas/outroladodahistoria-autodeclaracao.html"


def grupo(sigla: str) -> str:
    s = campos.sigla(sigla)
    s = HERDEIRO.get(s, s)
    return AUTO.get(s, "sem partido")


def tres(g: str) -> str:
    """O agrupamento em 3 que o autor pediu: direita = quem se declara de direita; esquerda = esquerda + centro-esquerda; centro = o resto."""
    return {"direita": "direita", "centro-direita": "centro", "centro": "centro", "centro-esquerda": "esquerda", "esquerda": "esquerda"}.get(g, "centro")


def nome_norm(s) -> str:
    if s is None or (isinstance(s, float) and s != s):
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z ]", "", s)).strip()


def candidaturas(ano: int) -> pd.DataFrame:
    """Todas as candidaturas do ano (todos os cargos) com nomes e nascimento, para ligar a mesma pessoa entre cargos."""
    z = zipfile.ZipFile(TSE / f"consulta_cand_{ano}.zip")
    cols = {"SQ_CANDIDATO", "NM_CANDIDATO", "NM_URNA_CANDIDATO", "NM_SOCIAL_CANDIDATO", "DT_NASCIMENTO", "SG_UF", "CD_CARGO", "DS_CARGO", "SG_PARTIDO", "DS_SIT_TOT_TURNO", "NR_TURNO"}
    partes = []
    for i in z.infolist():
        n = i.filename
        if n.endswith(".csv") and "_BRASIL" not in n and not n.endswith("_BR.csv"):
            with z.open(n) as fh:
                partes.append(pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str, usecols=lambda c: c in cols))
    d = pd.concat(partes, ignore_index=True)
    d = d.sort_values("NR_TURNO").drop_duplicates("SQ_CANDIDATO", keep="last")
    d["nasc"] = pd.to_datetime(d["DT_NASCIMENTO"], format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m-%d")
    return d


def indice_pessoas(cand: pd.DataFrame) -> dict:
    """(nascimento, nome normalizado) -> lista de linhas de candidatura."""
    idx: dict = {}
    for r in cand.itertuples():
        if not isinstance(r.nasc, str):
            continue
        for nm in (r.NM_CANDIDATO, r.NM_URNA_CANDIDATO, r.NM_SOCIAL_CANDIDATO):
            k = nome_norm(nm)
            if k and k not in ("NULO", "NE"):
                idx.setdefault((r.nasc, k), []).append(r)
    return idx


def achar(idx: dict, nasc, nomes) -> list:
    vistos, out = set(), []
    for nm in nomes:
        for r in idx.get((nasc, nome_norm(nm)), []):
            if r.SQ_CANDIDATO not in vistos:
                vistos.add(r.SQ_CANDIDATO)
                out.append(r)
    return out


LIMIARES_CAMARA = [
    ("1/3: abrir CPI (art. 58 §3º)", 171),
    ("bloquear uma PEC (mais de 2/5)", 206),
    ("maioria absoluta: lei complementar, cassação, derrubar veto com o Senado (arts. 69, 55 §2º, 66 §4º)", 257),
    ("3/5: aprovar PEC (art. 60 §2º)", 308),
    ("2/3: autorizar processo contra o Presidente (art. 51, I)", 342),
]
LIMIARES_SENADO = [
    ("1/3: abrir CPI (art. 58 §3º)", 27),
    ("bloquear uma PEC (mais de 2/5)", 33),
    ("maioria absoluta: lei complementar, derrubar veto com a Câmara, aprovar autoridade com quórum qualificado", 41),
    ("3/5: aprovar PEC (art. 60 §2º)", 49),
    ("2/3: condenar no impeachment, de Presidente ou de ministro do STF (art. 52, parágrafo único)", 54),
]


def escada(cont: dict, limiares) -> pd.DataFrame:
    d = cont.get("direita", 0)
    dc = d + cont.get("centro-direita", 0)
    dcc = dc + cont.get("centro", 0)
    esq = cont.get("esquerda", 0) + cont.get("centro-esquerda", 0)
    linhas = []
    for nome, n in limiares:
        linhas.append({
            "limiar": nome, "votos_necessarios": n,
            "direita_sozinha": d, "falta_a_direita": max(n - d, 0),
            "direita_mais_centro_direita": dc, "falta_com_centro_direita": max(n - dc, 0),
            "direita_centro_direita_e_centro": dcc,
            "esquerda_e_centro_esquerda": esq, "falta_a_esquerda": max(n - esq, 0),
        })
    return pd.DataFrame(linhas)


def main() -> None:
    registrar("e0.parametro", {"nome": "autodeclaracao do partido", "fonte": FONTE_AUTO, "grupos": {g: sorted(k for k, v in AUTO.items() if v == g) for g in GRUPOS},
                               "herdeiros": HERDEIRO})
    tabela("e0_grupos_por_autodeclaracao", pd.DataFrame([{"partido": k, "grupo": v, "agrupamento_em_3": tres(v)} for k, v in AUTO.items()]))

    # ---------------- E1: Camara por grupo, 2018 / 2022 / 2026 ----------------
    cad = pd.read_csv(RES / "a1_cadeiras_por_partido_e_ano.csv").set_index("sig")
    pv = pd.read_csv(RES / "a1_votos_pct_por_partido_e_ano.csv").set_index("sig")
    linhas, por_ano = [], {}
    for ano in ("2018", "2022", "2026"):
        g = cad[ano].groupby(cad.index.map(grupo)).sum()
        v = pv[ano].groupby(pv.index.map(grupo)).sum() * 100
        por_ano[int(ano)] = {k: int(g.get(k, 0)) for k in GRUPOS}
        for k in GRUPOS:
            linhas.append({"ano": int(ano), "grupo": k, "cadeiras": int(g.get(k, 0)), "pct_votos": round(float(v.get(k, 0)), 2)})
        assert int(g.sum()) == 513, (ano, g.sum())
    e1 = pd.DataFrame(linhas)
    tabela("e1_camara_por_grupo", e1)
    registrar("e1.camara_cadeiras", por_ano)
    registrar("e1.camara_pct_votos", {int(a): dict(zip(x.grupo, x.pct_votos)) for a, x in e1.groupby("ano")})
    registrar("e1.camara_em_3", {a: {t: sum(n for g_, n in c.items() if tres(g_) == t) for t in ("direita", "centro", "esquerda")} for a, c in por_ano.items()})
    # o partido de Bolsonaro em cada eleicao (PSL em 2018, PL em 2022 e 2026)
    registrar("e1.partido_de_bolsonaro", {"2018 (PSL)": int(cad.loc["PSL", "2018"]), "2022 (PL)": int(cad.loc["PL", "2022"]), "2026 (PL)": int(cad.loc["PL", "2026"])})

    # ---------------- E2: o que cada grupo alcança na Camara ----------------
    for ano in (2022, 2026):
        t = escada(por_ano[ano], LIMIARES_CAMARA)
        tabela(f"e2_camara_limiares_{ano}", t)
        registrar(f"e2.camara_{ano}", t.to_dict("records"))

    # ---------------- E3: Senado, 2023 e 2027 ----------------
    sen = pd.read_csv(RES / "a2_senadores_eleitos_por_partido.csv").set_index("partido")
    comp27 = pd.read_csv(RES / "a2_composicao_fev2027.csv")
    comp27["grupo"] = comp27["sig"].map(grupo)
    c27 = comp27["grupo"].value_counts().to_dict()
    # 2023 pela legenda com que foram eleitos: 54 de 2018 + 27 de 2022
    c23 = (sen["2018"].groupby(sen.index.map(grupo)).sum() + sen["2022"].groupby(sen.index.map(grupo)).sum()).to_dict()
    # 2027 pela legenda com que foram eleitos (2026 + 2022), para comparar com 2023 na mesma base
    c27_eleicao = (sen["2026"].groupby(sen.index.map(grupo)).sum() + sen["2022"].groupby(sen.index.map(grupo)).sum()).to_dict()
    eleitos = {a: sen[str(a)].groupby(sen.index.map(grupo)).sum().to_dict() for a in (2018, 2022, 2026)}
    registrar("e3.senado_eleitos_por_grupo", {a: {k: int(v.get(k, 0)) for k in GRUPOS} for a, v in eleitos.items()})
    registrar("e3.senado_2023_pela_legenda_eleita", {k: int(c23.get(k, 0)) for k in GRUPOS})
    registrar("e3.senado_2027_pela_legenda_eleita", {k: int(c27_eleicao.get(k, 0)) for k in GRUPOS})
    registrar("e3.senado_2027_partido_atual", {k: int(c27.get(k, 0)) for k in GRUPOS + ["sem partido"]})
    registrar("e3.senado_pl", {"eleitos_2026": int(sen.loc["PL", "2026"]), "fev_2027_partido_atual": int((comp27.sig == "PL").sum())})
    for nome, c in (("2023", c23), ("2027", {**c27})):
        t = escada({k: int(c.get(k, 0)) for k in GRUPOS}, LIMIARES_SENADO)
        tabela(f"e3_senado_limiares_{nome}", t)
        registrar(f"e3.senado_limiares_{nome}", t.to_dict("records"))
    tabela("e3_senado_por_grupo", pd.DataFrame([{"composicao": "fev/2023 (legenda eleita)", **{k: int(c23.get(k, 0)) for k in GRUPOS}},
                                                {"composicao": "fev/2027 (legenda eleita)", **{k: int(c27_eleicao.get(k, 0)) for k in GRUPOS}},
                                                {"composicao": "fev/2027 (partido atual dos 27 que ficam)", **{k: int(c27.get(k, 0)) for k in GRUPOS}}]))

    # ---------------- E3b: o ANTES de verdade, pelo partido de hoje ----------------
    # Senado em exercicio (API do Senado, out/2026), partido atual de cada senador
    import json
    api = json.loads((RAIZ / "dados/brutos/senado/atual.json").read_text(encoding="utf-8"))["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    hoje_s = pd.Series([grupo(p["IdentificacaoParlamentar"].get("SiglaPartidoParlamentar", "")) for p in api]).value_counts().to_dict()
    pl_hoje_s = sum(1 for p in api if campos.sigla(p["IdentificacaoParlamentar"].get("SiglaPartidoParlamentar", "")) == "PL")
    registrar("e3.senado_em_exercicio_out2026", {"total": len(api), "PL": pl_hoje_s, **{k: int(hoje_s.get(k, 0)) for k in GRUPOS + ["sem partido"]}})
    t = escada({k: int(hoje_s.get(k, 0)) for k in GRUPOS}, LIMIARES_SENADO)
    tabela("e3_senado_limiares_em_exercicio_out2026", t)
    # Camara na vespera da eleicao (deputados em exercicio em 30/09/2026), partido da vespera
    plen_v = pd.read_parquet(DER / "plenario_deputados.parquet")
    pv_ = plen_v[plen_v.em_exercicio_30_09]
    hoje_c = pv_["partido_vespera"].map(grupo).value_counts().to_dict()
    registrar("e1.camara_na_vespera_set2026", {"total": int(len(pv_)), "PL": int((pv_["partido_vespera"].map(campos.sigla) == "PL").sum()), **{k: int(hoje_c.get(k, 0)) for k in GRUPOS + ["sem partido"]}})

    # ---------------- E4: governos por grupo e eleitorado governado ----------------
    gov = pd.read_csv(RES / "a3_governos.csv")
    gov["grupo"] = gov["partido"].fillna("").map(lambda p: grupo(p) if p else "em 2o turno")
    gov.loc[gov["situacao"].str.contains("2o turno", na=False) & ~gov["situacao"].str.contains("eleito", na=False), "grupo"] = "em 2o turno"
    aptos = pd.read_csv(RES / "b3_abstencao_governador_por_uf.csv") if False else None  # noqa: F841 (aptos vem do detalhe)
    from congresso.comum import detalhe
    det = detalhe()
    ap = det[(det.ano == 2026) & (det.cargo == 3)].groupby("uf")["aptos"].sum()
    g26 = gov[gov.ano == 2026].copy()
    g26["aptos"] = g26["uf"].map(ap)
    linhas = []
    for ano, g in gov.groupby("ano"):
        cnt = g["grupo"].value_counts()
        linhas.append({"ano": int(ano), **{k: int(cnt.get(k, 0)) for k in GRUPOS + ["em 2o turno"]}})
    e4 = pd.DataFrame(linhas)
    tabela("e4_governos_por_grupo", e4)
    registrar("e4.governos_por_grupo", e4.to_dict("records"))
    share = (g26.groupby("grupo")["aptos"].sum() / g26["aptos"].sum() * 100).round(1).to_dict()
    registrar("e4.pct_eleitorado_governado_2026", share)
    registrar("e4.pl_governos", {"2018": int(((gov.ano == 2018) & (gov.partido.isin(["PL", "PR"]))).sum()), "2022": int(((gov.ano == 2022) & (gov.partido == "PL")).sum()),
                                 "2026": int(((gov.ano == 2026) & (gov.partido == "PL")).sum())})
    apo = pd.read_csv(RAIZ / "dados" / "apoios_declarados.csv")
    apo = apo[apo.ano == 2026][["uf", "apoio"]]
    g26 = g26.merge(apo, on="uf", how="left")
    g26["apoio"] = g26["apoio"].fillna("em 2o turno")
    tot = g26["aptos"].sum()
    registrar("e4.apoio_declarado_2026", {a: {"governos": int(len(x)), "pct_eleitorado": round(100 * x.aptos.sum() / tot, 1)} for a, x in g26.groupby("apoio")})
    tabela("e4_governos_2026_por_uf", g26[["uf", "situacao", "nome", "partido", "grupo", "apoio", "aptos"]])

    # ---------------- E5: anatomia do PL na Camara ----------------
    vc = votos_cand()
    c6 = vc[vc.cargo == 6].groupby(["ano", "uf", "sq", "nome", "partido", "sit"], as_index=False)["votos"].sum()
    c6["eleito"] = eleito(c6["sit"])
    c6["sig"] = c6["partido"].map(lambda p: HERDEIRO.get(campos.sigla(p), campos.sigla(p)))
    k22, k26 = candidaturas(2022), candidaturas(2026)
    i22, i26 = indice_pessoas(k22), indice_pessoas(k26)
    k22i = k22.set_index("SQ_CANDIDATO")
    k26i = k26.set_index("SQ_CANDIDATO")

    def pessoa22(sq):
        r = k22i.loc[sq]
        return r["nasc"], (r["NM_CANDIDATO"], r["NM_URNA_CANDIDATO"], r["NM_SOCIAL_CANDIDATO"])

    def pessoa26(sq):
        r = k26i.loc[sq]
        return r["nasc"], (r["NM_CANDIDATO"], r["NM_URNA_CANDIDATO"], r["NM_SOCIAL_CANDIDATO"])

    d22 = c6[c6.ano == 2022].set_index("sq")
    pl26 = c6[(c6.ano == 2026) & (c6.sig == "PL")]
    el_pl26 = pl26[pl26.eleito]
    # 2022: candidatos a deputado federal de 2022, por pessoa
    dep22 = {sq: r for sq, r in d22.iterrows()}

    def em_2022(sq26):
        nasc, nomes = pessoa26(sq26)
        for r in achar(i22, nasc, nomes):
            if r.CD_CARGO == "6" and r.SQ_CANDIDATO in dep22:
                x = dep22[r.SQ_CANDIDATO]
                return {"sig_2022": x["sig"], "eleito_2022": bool(x["eleito"]), "votos_2022": int(x["votos"])}
        return None

    plen = pd.read_parquet(DER / "plenario_deputados.parquet")
    vesp = plen[plen.em_exercicio_30_09].copy()
    vesp["sig"] = vesp["partido_vespera"].map(lambda p: HERDEIRO.get(campos.sigla(p), campos.sigla(p)))
    vesp_keys = {}
    for r in vesp.itertuples():
        for nm in (r.nomeCivil, r.nome):
            vesp_keys[(r.dataNascimento, nome_norm(nm))] = r.sig

    def na_vespera(sq26):
        nasc, nomes = pessoa26(sq26)
        for nm in nomes:
            s = vesp_keys.get((nasc, nome_norm(nm)))
            if s is not None:
                return s
        return None

    orig = []
    for r in el_pl26.itertuples():
        h = em_2022(r.sq)
        v = na_vespera(r.sq)
        if h and h["eleito_2022"] and h["sig_2022"] == "PL":
            o = "eleito em 2022 pelo PL"
        elif h and h["eleito_2022"]:
            o = "eleito em 2022 por outro partido e foi para o PL"
        elif v is not None:
            o = "assumiu o mandato depois de 2022 (suplente) e se elegeu pelo PL"
        elif h:
            o = "disputou deputado federal em 2022 e não se elegeu"
        else:
            o = "primeira disputa para deputado federal (desde 2022)"
        orig.append({"nome": r.nome, "uf": r.uf, "votos_2026": int(r.votos), "origem": o,
                     "partido_2022": h["sig_2022"] if h else "", "votos_2022": h["votos_2022"] if h else np.nan, "partido_vespera": v or ""})
    o = pd.DataFrame(orig)
    tabela("e5_pl_121_de_onde_veio_cada_um", o.sort_values(["origem", "votos_2026"], ascending=[True, False]))
    resumo_o = o.groupby("origem").agg(cadeiras=("nome", "size"), votos_2026=("votos_2026", "sum")).reset_index()
    tabela("e5_pl_121_resumo", resumo_o)
    registrar("e5.pl_121_origem", dict(zip(resumo_o.origem, resumo_o.cadeiras)))
    mig = o[o.origem == "eleito em 2022 por outro partido e foi para o PL"]
    registrar("e5.migrantes_de_onde", mig["partido_2022"].value_counts().to_dict())
    registrar("e5.migrantes_votos", {"2022_no_partido_antigo": int(mig["votos_2022"].sum()), "2026_pelo_PL": int(mig["votos_2026"].sum())})

    # os 98 do PL na vespera: o que aconteceu com cada um
    destino = []
    ve_pl = vesp[vesp.sig == "PL"]
    for r in ve_pl.itertuples():
        achados = []
        for nm in (r.nomeCivil, r.nome):
            achados += idx_get(i26, r.dataNascimento, nm)
        achados = {a.SQ_CANDIDATO: a for a in achados}.values()
        if not achados:
            dst = "não disputou nenhum cargo em 2026"
            cargo = ""
            ok = ""
        else:
            a = sorted(achados, key=lambda a: a.CD_CARGO)[0]
            cargo = a.DS_CARGO
            ok = str(a.DS_SIT_TOT_TURNO)
            el_ = ok.upper().startswith("ELEITO") or ok.upper() == "MÉDIA"
            seg = "2º TURNO" in ok.upper()
            if a.CD_CARGO == "6":
                dst = ("reeleito deputado" + (" pelo PL" if campos.sigla(a.SG_PARTIDO) == "PL" else f" por outro partido ({a.SG_PARTIDO})")) if el_ else "disputou deputado e não se elegeu"
            else:
                dst = f"disputou {a.DS_CARGO.lower()}" + (": eleito" if el_ else (": 2º turno" if seg else ": não eleito"))
        destino.append({"nome": r.nome, "uf": r.uf, "destino": dst, "cargo_2026": cargo, "situacao": ok})
    dpl = pd.DataFrame(destino)
    tabela("e5_pl_98_da_vespera_destino", dpl.sort_values("destino"))
    registrar("e5.pl_98_destino", dpl["destino"].value_counts().to_dict())

    # votos nominais do PL para deputado: 2022 x 2026, e quanto disso e de quem ja era deputado
    vpl = c6[(c6.sig == "PL")].groupby("ano")["votos"].sum()
    registrar("e5.pl_votos_nominais", {int(k): int(v) for k, v in vpl.items() if k in (2018, 2022, 2026)})
    pux = o.sort_values("votos_2026", ascending=False).head(10)
    registrar("e5.pl_top10_votos_2026", int(pux["votos_2026"].sum()))

    # ---------------- E6: nomes conhecidos da esquerda e da centro-esquerda que ficaram fora ----------------
    el22 = c6[(c6.ano == 2022) & c6.eleito].copy()
    el22["grupo"] = el22["sig"].map(lambda s: AUTO.get(s, "sem partido"))
    linhas = []
    for r in el22.itertuples():
        nasc, nomes = pessoa22(r.sq)
        achados = {a.SQ_CANDIDATO: a for a in achar(i26, nasc, nomes)}.values()
        if not achados:
            dst, sit, cargo, part = "não disputou", "", "", ""
        else:
            a = sorted(achados, key=lambda a: a.CD_CARGO)[-1] if any(x.CD_CARGO == "6" for x in achados) else sorted(achados, key=lambda a: a.CD_CARGO)[0]
            a6 = [x for x in achados if x.CD_CARGO == "6"]
            a = a6[0] if a6 else a
            sit, cargo, part = str(a.DS_SIT_TOT_TURNO), a.DS_CARGO, a.SG_PARTIDO
            el_ = sit.upper().startswith("ELEITO") or sit.upper() == "MÉDIA"
            seg = "2º TURNO" in sit.upper()
            dst = ("eleito" if el_ else ("2º turno" if seg else "não eleito"))
        linhas.append({"nome": r.nome, "uf": r.uf, "partido_2022": r.partido, "grupo_2022": r.grupo, "votos_2022": int(r.votos), "cargo_2026": cargo, "partido_2026": part, "resultado_2026": dst, "situacao": sit})
    e6 = pd.DataFrame(linhas)
    tabela("e6_eleitos_2022_e_o_que_houve_em_2026", e6.sort_values("votos_2022", ascending=False))
    fora = e6[(e6.resultado_2026 == "não eleito") & e6.grupo_2022.isin(["esquerda", "centro-esquerda"])].sort_values("votos_2022", ascending=False)
    tabela("e6_esquerda_que_disputou_e_nao_se_elegeu", fora)
    registrar("e6.resultado_por_grupo_2022", {g: x["resultado_2026"].value_counts().to_dict() for g, x in e6.groupby("grupo_2022")})
    # Senado 2026: candidatos de esquerda e centro-esquerda mais votados que nao se elegeram
    c5 = vc[(vc.cargo == 5) & (vc.ano == 2026)].groupby(["uf", "sq", "nome", "partido", "sit"], as_index=False)["votos"].sum()
    c5["grupo"] = c5["partido"].map(grupo)
    c5["eleito"] = eleito(c5["sit"])
    s_fora = c5[~c5.eleito & c5.grupo.isin(["esquerda", "centro-esquerda"])].sort_values("votos", ascending=False).head(15)
    tabela("e6_senado_esquerda_mais_votados_nao_eleitos", s_fora[["uf", "nome", "partido", "votos"]])
    print("ok E")


def idx_get(idx, nasc, nm):
    return idx.get((nasc, nome_norm(nm)), [])


if __name__ == "__main__":
    main()
