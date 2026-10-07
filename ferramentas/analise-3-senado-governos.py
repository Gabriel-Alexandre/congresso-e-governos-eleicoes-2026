"""Bloco A (Senado e governos) e D8: A2, A3, D5 (senadores e governadores) e o tema STF no Senado.

Criterios: docs/PRE_REGISTRO.md secoes 3, 4, 10 e 11.
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.comum import RAIZ, UFS, eleito, votos_cand  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

TSE = RAIZ / "dados" / "brutos" / "tse"


def nn(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", "", s).strip()


def campo_de(partido: str, pesos: dict) -> str:
    return campos.campo_r1(campos.nota_r1(partido, pesos))


def turno2_governador(ano: int) -> pd.DataFrame:
    z = zipfile.ZipFile(TSE / f"votacao_candidato_munzona_{ano}.zip")
    partes = []
    for i in z.infolist():
        if i.filename.endswith(".csv") and "_BRASIL" not in i.filename and not i.filename.endswith("_BR.csv"):
            with z.open(i.filename) as fh:
                for ch in pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str, chunksize=400_000, usecols=["NR_TURNO", "SG_UF", "CD_CARGO", "NM_URNA_CANDIDATO", "SG_PARTIDO", "QT_VOTOS_NOMINAIS_VALIDOS", "DS_SIT_TOT_TURNO"]):
                    ch = ch[(ch["NR_TURNO"] == "2") & (ch["CD_CARGO"] == "3")]
                    if len(ch):
                        partes.append(ch)
    d = pd.concat(partes)
    d["votos"] = pd.to_numeric(d["QT_VOTOS_NOMINAIS_VALIDOS"], errors="coerce").fillna(0)
    return d.groupby(["SG_UF", "NM_URNA_CANDIDATO", "SG_PARTIDO", "DS_SIT_TOT_TURNO"], as_index=False)["votos"].sum().rename(columns={"SG_UF": "uf", "NM_URNA_CANDIDATO": "nome", "SG_PARTIDO": "partido", "DS_SIT_TOT_TURNO": "sit"})


def main() -> None:
    cand = votos_cand()
    pesos_ = json.loads((RAIZ / "resultados" / "RESUMO.json").read_text(encoding="utf-8"))["a1"]["pesos_fusoes"]

    # ---------------- Senado ----------------
    c5 = cand[cand["cargo"] == 5].groupby(["ano", "uf", "sq", "nome", "partido", "fed", "sit"], as_index=False)["votos"].sum()
    c5["eleito"] = eleito(c5["sit"])
    c5["campo_r1"] = c5["partido"].map(lambda p: campo_de(p, pesos_))
    e18 = c5[(c5.ano == 2018) & c5.eleito]
    e26 = c5[(c5.ano == 2026) & c5.eleito].copy()
    e22 = c5[(c5.ano == 2022) & c5.eleito]
    registrar("a2.eleitos_por_ano", c5[c5.eleito].groupby("ano").size().to_dict())

    # R3: candidatos que Flavio declarou apoiar (lista do projeto irmao, ranking.org.br 22/09/2026)
    sf = pd.read_csv(RAIZ / "dados" / "senado_apoio_flavio.csv")
    sf["n"] = sf["candidato"].map(nn)
    c26_all = c5[c5.ano == 2026].copy()
    c26_all["n"] = c26_all["nome"].map(nn)

    def casa(uf, nome_lista):
        x = c26_all[c26_all.uf == uf]
        for r in x.itertuples():
            if r.n == nome_lista or (len(nome_lista) > 5 and (nome_lista in r.n or r.n in nome_lista)):
                return r.sq
        return None
    sf["sq"] = [casa(r.uf, r.n) for r in sf.itertuples()]
    registrar("a2.apoio_flavio_lista", {"candidatos_na_lista": int(len(sf)), "casados_com_candidatos_do_TSE": int(sf.sq.notna().sum())})
    apoio_sq = set(sf.sq.dropna())
    tabela("a2_apoio_flavio_nao_casados", sf[sf.sq.isna()][["uf", "candidato", "partido"]])
    e26["apoio_flavio_lista"] = e26["sq"].isin(apoio_sq)

    por_campo = pd.DataFrame({ano: x.campo_r1.value_counts() for ano, x in (("2018", e18), ("2022", e22), ("2026", e26))}).fillna(0).astype(int)
    tabela("a2_senadores_eleitos_por_campo_r1", por_campo.reset_index())
    registrar("a2.eleitos_por_campo_r1", por_campo.to_dict())
    pp = pd.DataFrame({ano: x.partido.map(campos.sigla).value_counts() for ano, x in (("2018", e18), ("2022", e22), ("2026", e26))}).fillna(0).astype(int).sort_values("2026", ascending=False)
    tabela("a2_senadores_eleitos_por_partido", pp.reset_index())
    registrar("a2.eleitos_por_partido_2026", pp["2026"].to_dict())
    registrar("a2.eleitos_2026_na_lista_de_apoio_a_Flavio", int(e26.apoio_flavio_lista.sum()))
    registrar("a2.eleitos_2026_PL", int((e26.partido.map(campos.sigla) == "PL").sum()))

    # troca de campo por UF (cada UF elege 2 em 2018 e 2 em 2026)
    linhas = []
    for uf in UFS:
        a = e18[e18.uf == uf].campo_r1.value_counts().to_dict()
        b = e26[e26.uf == uf].campo_r1.value_counts().to_dict()
        linhas.append({"uf": uf, "2018_esq": a.get("esquerda", 0), "2018_cen": a.get("centro", 0), "2018_dir": a.get("direita", 0), "2026_esq": b.get("esquerda", 0), "2026_cen": b.get("centro", 0), "2026_dir": b.get("direita", 0)})
    tr = pd.DataFrame(linhas)
    tr["dif_esq"] = tr["2026_esq"] - tr["2018_esq"]
    tr["dif_dir"] = tr["2026_dir"] - tr["2018_dir"]
    tabela("a2_troca_de_campo_por_uf", tr)
    registrar("a2.vagas_esquerda_2018_para_2026", {"2018": int(tr["2018_esq"].sum()), "2026": int(tr["2026_esq"].sum())})
    registrar("a2.ufs_onde_a_esquerda_perdeu_vaga", tr[tr.dif_esq < 0].uf.tolist())
    registrar("a2.ufs_onde_a_esquerda_ganhou_vaga", tr[tr.dif_esq > 0].uf.tolist())

    # composicao a partir de fev/2027: 54 eleitos + 27 com mandato ate 2031 (partido atual na API do Senado)
    api = json.loads((RAIZ / "dados/brutos/senado/atual.json").read_text(encoding="utf-8"))["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    restantes = []
    for p in api:
        seg = p["Mandato"].get("SegundaLegislaturaDoMandato", {})
        if seg.get("DataFim") == "2031-01-31" and p["Mandato"].get("PrimeiraLegislaturaDoMandato", {}).get("DataFim") == "2027-01-31":
            restantes.append({"nome": p["IdentificacaoParlamentar"]["NomeParlamentar"], "uf": p["IdentificacaoParlamentar"]["UfParlamentar"], "partido": p["IdentificacaoParlamentar"]["SiglaPartidoParlamentar"]})
    rest = pd.DataFrame(restantes)
    registrar("a2.mandato_ate_2031_na_api", int(len(rest)))
    rest["campo_r1"] = rest["partido"].map(lambda p: campo_de(p, pesos_))
    tabela("a2_senadores_com_mandato_ate_2031", rest)
    comp = pd.concat([e26[["uf", "nome", "partido", "campo_r1"]].assign(origem="eleito em 2026"), rest.assign(origem="mandato ate 2031")])
    comp["sig"] = comp.partido.map(campos.sigla)
    tabela("a2_composicao_fev2027", comp)
    reg_comp = {"total": int(len(comp)), "por_campo_r1": comp.campo_r1.value_counts().to_dict(), "por_partido": comp.sig.value_counts().to_dict()}
    registrar("a2.composicao_fev2027", reg_comp)
    n_dir = int((comp.campo_r1 == "direita").sum())
    n_esq = int((comp.campo_r1 == "esquerda").sum())
    n_pl = int((comp.sig == "PL").sum())
    registrar("a2.limiares", {"maioria_absoluta_41": 41, "tres_quintos_49": 49, "dois_tercos_54": 54, "direita_r1": n_dir, "esquerda_r1": n_esq, "PL": n_pl, "direita_alcanca_41": n_dir >= 41, "direita_alcanca_49": n_dir >= 49, "direita_alcanca_54": n_dir >= 54})

    # ---------------- D5 senadores ----------------
    linhas = []
    for a0, a1 in ((2010, 2018), (2014, 2022), (2018, 2026)):
        x0 = c5[(c5.ano == a0) & c5.eleito]
        x1 = c5[c5.ano == a1]
        x1 = x1.assign(n=x1.nome.map(nn))
        r = []
        for q in x0.itertuples():
            m = x1[(x1.uf == q.uf) & (x1.n == nn(q.nome))]
            r.append({"campo": q.campo_r1, "tentou": len(m) > 0, "reeleito": bool(m.eleito.any()) if len(m) else False})
        r = pd.DataFrame(r)
        for k, g in [("todos", r)] + list(r.groupby("campo")):
            linhas.append({"de": a0, "para": a1, "campo_r1_da_eleicao_anterior": k, "eleitos_na_eleicao_anterior": len(g), "tentaram": int(g.tentou.sum()), "reeleitos": int(g.reeleito.sum()), "pct_reeleito_entre_os_que_tentaram": round(100 * g.reeleito.sum() / max(g.tentou.sum(), 1), 1)})
    d5s = pd.DataFrame(linhas)
    tabela("d5_reeleicao_senadores", d5s)
    registrar("d5.reeleicao_senadores", d5s.to_dict("records"))

    # ---------------- Governos ----------------
    g3 = cand[(cand["cargo"] == 3)].groupby(["ano", "uf", "sq", "nome", "partido", "sit"], as_index=False)["votos"].sum()
    out = []
    for ano in (2018, 2022, 2026):
        t1 = g3[g3.ano == ano]
        for uf in UFS:
            x = t1[t1.uf == uf]
            ven = x[x.sit.str.upper().str.startswith("ELEITO")]
            if len(ven):
                out.append({"ano": ano, "uf": uf, "situacao": "eleito no 1o turno", "nome": ven.iloc[0].nome, "partido": ven.iloc[0].partido, "finalistas": ""})
                continue
            if ano == 2026:
                f = x[x.sit.str.contains("2", na=False)]
                out.append({"ano": ano, "uf": uf, "situacao": "2o turno em disputa", "nome": "", "partido": "", "finalistas": " x ".join(f"{r.nome} ({r.partido})" for r in f.itertuples())})
            else:
                t2 = TURNO2[ano]
                y = t2[t2.uf == uf].sort_values("votos", ascending=False)
                out.append({"ano": ano, "uf": uf, "situacao": "eleito no 2o turno", "nome": y.iloc[0].nome, "partido": y.iloc[0].partido, "finalistas": ""})
    gov = pd.DataFrame(out)
    gov["campo_r1"] = gov["partido"].map(lambda p: campo_de(p, pesos_) if p else "")
    tabela("a3_governos", gov)
    ap = pd.read_csv(RAIZ / "dados" / "apoios_declarados.csv")
    res = []
    for ano in (2018, 2022, 2026):
        g = gov[(gov.ano == ano)]
        dec = g[g.situacao != "2o turno em disputa"]
        r = {"ano": ano, "decididos": int(len(dec)), "em_disputa": int((g.situacao == "2o turno em disputa").sum())}
        r.update({f"decididos_{k}": int(v) for k, v in dec.campo_r1.value_counts().items()})
        r["partido_do_governador_PL"] = int((dec.partido == "PL").sum())
        res.append(r)
    resg = pd.DataFrame(res).fillna(0)
    tabela("a3_governos_por_campo_r1", resg)
    registrar("a3.governos_por_campo_r1", resg.to_dict("records"))
    # R3: apoio declarado para os 20 decididos em 2026
    a26 = ap[ap.ano == 2026][["uf", "governador", "partido", "apoio"]]
    registrar("a3.apoio_declarado_2026", a26.apoio.value_counts().to_dict())
    # troca de campo 2022 -> 2026 (R1) entre os decididos em 2026
    g22 = gov[gov.ano == 2022].set_index("uf")
    g26 = gov[(gov.ano == 2026) & (gov.situacao != "2o turno em disputa")]
    tc = g26.set_index("uf")[["nome", "partido", "campo_r1"]].join(g22[["nome", "partido", "campo_r1"]], rsuffix="_2022")
    tc["trocou_de_campo_r1"] = tc["campo_r1"] != tc["campo_r1_2022"]
    tc["mesmo_governador"] = tc["nome"].map(nn) == tc["nome_2022"].map(nn)
    tabela("a3_troca_2022_2026_decididos", tc.reset_index())
    registrar("a3.decididos_2026_trocaram_de_campo_r1", int(tc.trocou_de_campo_r1.sum()))
    registrar("a3.decididos_2026_com_o_mesmo_governador_de_2022", int(tc.mesmo_governador.sum()))
    # D5 governadores: eleitos em 2022 que tentaram o cargo em 2026 (mesmo UF, mesmo nome de urna)
    linhas = []
    for a0, a1 in ((2014, 2018), (2018, 2022), (2022, 2026)):
        g0 = g3[(g3.ano == a0)]
        w0 = gov[gov.ano == a0] if a0 in (2018, 2022) else None
        if w0 is None:
            continue
        t = g3[g3.ano == a1].assign(n=lambda d: d.nome.map(nn))
        for r in w0.itertuples():
            m = t[(t.uf == r.uf) & (t.n == nn(r.nome))]
            linhas.append({"de": a0, "para": a1, "uf": r.uf, "governador": r.nome, "campo_r1": r.campo_r1, "tentou_o_cargo": len(m) > 0, "venceu_ou_foi_ao_2o_turno": bool(m.sit.str.upper().str.startswith(("ELEITO", "2")).any()) if len(m) else False})
    dg = pd.DataFrame(linhas)
    tabela("d5_governadores_que_tentaram_continuar", dg)
    registrar("d5.governadores", dg.groupby(["de", "para"]).agg(eleitos=("uf", "size"), tentaram=("tentou_o_cargo", "sum"), venceram_ou_2o_turno=("venceu_ou_foi_ao_2o_turno", "sum")).reset_index().to_dict("records"))

    # ---------------- D8: o tema STF no Senado ----------------
    _h = RAIZ / "dados/brutos/capturas/gazeta-impeachment-senado.html"
    if not _h.exists():  # a captura da imprensa nao vai para o git; a tabela extraida (fatos) vai
        pos = pd.read_csv(RAIZ / "resultados/d8_lista_gazeta_posicoes.csv")
        _h = None
    else:
        t = _h.read_text(encoding="utf-8", errors="replace")
        t = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", "\n", t)
        t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
        estados = {"Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"}
        uf_atual = None
        pos = []
        ini = t.find("A posição de cada candidato ao Senado")
        for linha in t[ini:].splitlines():
            s = linha.strip()
            if s in estados:
                uf_atual = estados[s]
                continue
            m = re.match(r"^(.{3,60}?) \(([A-Za-zÀ-ÿ ]+)\): (.+)$", s)
            if m and uf_atual:
                pos.append({"uf": uf_atual, "nome": m.group(1), "partido": m.group(2), "posicao": m.group(3).strip().lower()})
        pos = pd.DataFrame(pos)
    if _h is not None:
        pos.to_csv(RAIZ / "resultados/d8_lista_gazeta_posicoes.csv", index=False)
    registrar("d8.candidatos_na_lista_da_gazeta", int(len(pos)))
    def classe(p):
        if p.startswith("a favor"):
            return "a favor"
        if p.startswith("contra") or "contr" in p.split(":")[0]:
            return "contra"
        if "não se posicionou" in p or "não foi localizado" in p:
            return "sem posicao"
        return "outra (neutro, reforma ou outra)"
    pos["classe"] = pos["posicao"].map(classe)
    registrar("d8.lista_gazeta_por_classe", pos.classe.value_counts().to_dict())
    c26_all["n"] = c26_all["nome"].map(nn)
    pos["n"] = pos["nome"].map(nn)

    def casa2(r):
        x = c26_all[c26_all.uf == r.uf]
        for q in x.itertuples():
            if q.n == r.n or (len(r.n) > 5 and (r.n in q.n or q.n in r.n)):
                return q.sq
        return None
    pos["sq"] = [casa2(r) for r in pos.itertuples()]
    registrar("d8.lista_casada_com_candidatos_do_TSE", int(pos.sq.notna().sum()))
    tabela("d8_posicoes_nao_casadas", pos[pos.sq.isna()][["uf", "nome", "partido", "posicao"]])
    j = c26_all.merge(pos[["sq", "classe"]].dropna(), on="sq", how="left")
    j["classe"] = j["classe"].fillna("fora da lista da Gazeta")
    tot_uf = j.groupby("uf")["votos"].transform("sum")
    j["pct_votos_senado_na_uf"] = 100 * j["votos"] / tot_uf
    eleitos = j[j.eleito]
    e_tab = eleitos.groupby("classe").size()
    tabela("d8_eleitos_por_posicao_declarada", e_tab.reset_index(name="eleitos"))
    registrar("d8.eleitos_por_posicao", e_tab.to_dict())
    registrar("d8.eleitos_a_favor_por_campo_r1", eleitos[eleitos.classe == "a favor"].campo_r1.value_counts().to_dict())
    comp_j = j[j.classe != "fora da lista da Gazeta"].groupby(["classe", "campo_r1"]).agg(candidatos=("sq", "size"), eleitos=("eleito", "sum"), media_pct_votos=("pct_votos_senado_na_uf", "mean")).round(2).reset_index()
    tabela("d8_posicao_x_campo_x_desempenho", comp_j)
    # eleitos a favor + mandato ate 2031 sem posicao conhecida -> so contamos o que a fonte cobre
    n_fav = int(e_tab.get("a favor", 0))
    registrar("d8.conta_contra_limiares", {"eleitos_2026_a_favor": n_fav, "observacao": "a lista cobre candidatos de partidos com representacao; senadores com mandato ate 2031 nao entram"})
    print("ok A2/A3/D5/D8")


if __name__ == "__main__":
    TURNO2 = {a: turno2_governador(a) for a in (2018, 2022)}
    main()
