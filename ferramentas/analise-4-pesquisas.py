"""Bloco C: as pesquisas de governador (Datafolha e Quaest, ultima da vespera) contra o resultado das urnas.

Fonte do resultado das pesquisas: captura `opovo-pesquisas-governador` (dados/CAPTURAS.csv). Em SP ha segunda fonte
(Gazeta do Povo, `gazeta-pesquisas-sp`), que traz os mesmos numeros de Datafolha e Quaest e dois institutos a mais.
Registro das pesquisas no TSE (instituto, UF, datas, amostra) cruzado como segunda via de existencia.
Criterios: docs/PRE_REGISTRO.md secao 9 e emenda 3 da secao 15.
"""
from __future__ import annotations

import html
import re
import sys
import unicodedata
import zipfile
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.comum import RAIZ, UFS, votos_cand, detalhe  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

ESTADOS = {"Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA", "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO", "Maranhão": "MA", "Mato Grosso do Sul": "MS", "Mato Grosso": "MT", "Minas Gerais": "MG", "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI", "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS", "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP", "Sergipe": "SE", "Tocantins": "TO"}
LULA_COLIGACAO = {"PT", "PSB", "PDT", "PCDOB", "PV", "PSOL", "REDE"}


def nn(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", "", s).strip()


def parse_opovo() -> pd.DataFrame:
    html_ = RAIZ / "dados/brutos/capturas/opovo-pesquisas-governador.html"
    if not html_.exists():  # a captura da imprensa nao vai para o git; a tabela extraida (fatos) vai
        return pd.read_csv(RAIZ / "resultados/c1_pesquisas_governador_2026_extraidas.csv")
    h = html_.read_text(encoding="utf-8", errors="replace")
    h = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", h)).replace(" ", " ")
    linhas = [l.strip() for l in t.splitlines() if l.strip()]
    ini = next(i for i, l in enumerate(linhas) if l.startswith("Quaest Acre"))
    fim = next(i for i, l in enumerate(linhas) if l.startswith("Ao vivo"))
    out = []
    i = ini
    while i < fim:
        l = linhas[i]
        m = re.match(r"^(Quaest|Datafolha)\s*(.+?)(?:\s*\([A-Z]{2}\))?$", l)
        if m and "%" not in l and i + 1 < fim:
            inst, nome_uf = m.group(1), m.group(2).strip()
            uf = ESTADOS.get(nome_uf)
            if uf:
                cands = linhas[i + 1]
                for c in re.finditer(r"([^;:()]+?)\s*\(([^)]+)\)\s*:?\s*(\d+)\s*%", cands):
                    out.append({"instituto": inst, "uf": uf, "candidato": c.group(1).strip(" ;"), "partido": c.group(2).strip(), "pct_poll": int(c.group(3))})
                i += 2
                continue
        i += 1
    return pd.DataFrame(out)


def registro_tse() -> pd.DataFrame:
    z = zipfile.ZipFile(RAIZ / "dados/brutos/tse/pesquisa_eleitoral_2026.zip")
    partes = []
    for n in z.namelist():
        if n.endswith(".csv") and "BRASIL" not in n:
            with z.open(n) as fh:
                d = pd.read_csv(fh, sep=";", encoding="latin-1", dtype=str, usecols=["SG_UF", "NM_EMPRESA", "NM_EMPRESA_FANTASIA", "DS_CARGO", "DT_INICIO_PESQUISA", "DT_FIM_PESQUISA", "DT_DIVULGACAO", "QT_ENTREVISTADO", "NR_PROTOCOLO_REGISTRO", "DS_PLANO_AMOSTRAL"])
            partes.append(d)
    return pd.concat(partes, ignore_index=True)


def margem_do_texto(txt: str):
    m = re.search(r"margem de erro[^.]{0,120}?(\d+(?:[.,]\d+)?)\s*(?:pontos|p\.p|pp|%)", str(txt), flags=re.I)
    return float(m.group(1).replace(",", ".")) if m else None


def main() -> None:
    po = parse_opovo()
    registrar("c1.opovo_linhas", int(len(po)))
    registrar("c1.pesquisas_opovo", int(po.groupby(["instituto", "uf"]).ngroups))
    tabela("c1_pesquisas_governador_2026_extraidas", po)

    # segunda fonte em SP (Gazeta do Povo): conferencia
    gz = {"Datafolha": (60.0, 35.0), "Quaest": (60.0, 36.0), "Parana Pesquisas": (60.3, 37.0), "AtlasIntel": (57.4, 41.6)}
    sp = po[po.uf == "SP"].pivot_table(index="instituto", columns="candidato", values="pct_poll")
    conf = []
    for inst in ("Datafolha", "Quaest"):
        a = sp.loc[inst]
        t_o = float([v for k, v in a.items() if "Tarc" in k][0])
        h_o = float([v for k, v in a.items() if "Haddad" in k][0])
        conf.append({"instituto": inst, "tarcisio_opovo": t_o, "tarcisio_gazeta": gz[inst][0], "haddad_opovo": h_o, "haddad_gazeta": gz[inst][1], "iguais": t_o == gz[inst][0] and h_o == gz[inst][1]})
    conf = pd.DataFrame(conf)
    tabela("c1_conferencia_sp_duas_fontes", conf)
    registrar("c1.sp_duas_fontes_iguais", bool(conf.iguais.all()))

    # registro no TSE: a pesquisa existe?
    reg = registro_tse()
    reg = reg[reg.DS_CARGO.str.contains("Governador", na=False)].copy()
    reg["fim"] = pd.to_datetime(reg.DT_FIM_PESQUISA, errors="coerce")
    ult = reg[(reg.fim >= "2026-09-26") & (reg.fim <= "2026-10-03")]
    achados = []
    for (inst, uf), _ in po.groupby(["instituto", "uf"]):
        x = ult[(ult.SG_UF == uf) & (ult.NM_EMPRESA.str.upper().str.contains(inst.upper(), na=False) | ult.NM_EMPRESA_FANTASIA.fillna("").str.upper().str.contains(inst.upper(), na=False))]
        achados.append({"instituto": inst, "uf": uf, "registros_no_TSE_na_janela": len(x), "amostra": int(x.QT_ENTREVISTADO.astype(float).max()) if len(x) else None, "fim_campo": x.fim.max().date().isoformat() if len(x) else None, "protocolo": x.NR_PROTOCOLO_REGISTRO.iloc[0] if len(x) else None, "margem_no_plano": margem_do_texto(x.DS_PLANO_AMOSTRAL.iloc[0]) if len(x) else None})
    ach = pd.DataFrame(achados)
    tabela("c1_pesquisas_x_registro_tse", ach)
    registrar("c1.pesquisas_com_registro_no_tse", {"com_registro": int((ach.registros_no_TSE_na_janela > 0).sum()), "total": int(len(ach))})
    registrar("c1.registro_tse_governador_total_2026", int(len(reg)))
    registrar("c1.registro_tse_governador_na_janela_26set_03out", int(len(ult)))

    # resultado das urnas (governador, 1o turno, % dos votos validos)
    c3 = votos_cand()
    c3 = c3[(c3.ano == 2026) & (c3.cargo == 3)].groupby(["uf", "sq", "nome", "partido", "sit"], as_index=False)["votos"].sum()
    c3["pct_urna"] = 100 * c3["votos"] / c3.groupby("uf")["votos"].transform("sum")
    c3["n"] = c3["nome"].map(nn)
    ap = pd.read_csv(RAIZ / "dados/apoios_declarados.csv")
    apoio26 = {r.uf: r.apoio for r in ap[ap.ano == 2026].itertuples()}

    def alinhamento(uf, partido, nome, venc_declarado):
        p = campos._norm(partido)
        if p == "PL":
            return "Flavio"
        if venc_declarado is not None and venc_declarado in ("Flavio", "Lula"):
            return venc_declarado
        if p in LULA_COLIGACAO:
            return "Lula"
        return "outro_ou_sem_info"

    def casa(uf, nome_poll):
        x = c3[c3.uf == uf]
        n = nn(nome_poll)
        for r in x.itertuples():
            if r.n == n or n in r.n or r.n in n:
                return r
        # sobrenome
        for r in x.itertuples():
            if n.split()[-1] in r.n.split() and len(n.split()[-1]) > 3:
                return r
        return None
    linhas = []
    for (inst, uf), g in po.groupby(["instituto", "uf"]):
        urna = c3[c3.uf == uf].sort_values("votos", ascending=False)
        top = urna.head(2)
        pol = {}
        for r in g.itertuples():
            m = casa(uf, r.candidato)
            if m is not None:
                pol[m.sq] = r.pct_poll
        t1, t2 = top.iloc[0], top.iloc[1]
        if t1.sq not in pol or t2.sq not in pol:
            linhas.append({"instituto": inst, "uf": uf, "status": "top2 da urna nao encontrado na pesquisa"})
            continue
        e1 = pol[t1.sq] - t1.pct_urna
        marg_p = pol[t1.sq] - pol[t2.sq]
        marg_u = t1.pct_urna - t2.pct_urna
        a1 = alinhamento(uf, t1.partido, t1.nome, apoio26.get(uf) if t1.sit.upper().startswith("ELEITO") else None)
        a2 = alinhamento(uf, t2.partido, t2.nome, None)
        n1 = campos.campo_r1(campos.nota_r1(t1.partido)); n2 = campos.campo_r1(campos.nota_r1(t2.partido))
        # M = margem da pesquisa - margem da urna (positivo = a pesquisa superestimou o 1o colocado da urna).
        # "subestimou o alvo" (pp): se o alvo e o 1o, e -M; se o alvo e o 2o, e +M.
        def sinal(c1, c2, alvo):
            M = marg_p - marg_u
            if c1 == alvo and c2 != alvo:
                return -M
            if c2 == alvo and c1 != alvo:
                return M
            return None
        e_r3 = None
        if {a1, a2} == {"Flavio", "Lula"}:
            e_r3 = sinal(a1, a2, "Flavio")
        e_expl = None
        if (a1 == "Flavio") != (a2 == "Flavio"):
            e_expl = sinal("Flavio" if a1 == "Flavio" else "x", "Flavio" if a2 == "Flavio" else "y", "Flavio")
        e_r1 = None
        if {n1, n2} == {"direita", "esquerda"}:
            e_r1 = sinal(n1, n2, "direita")
        linhas.append({
            "instituto": inst, "uf": uf, "status": "ok", "vencedor_urna": t1.nome, "partido_1": t1.partido, "segundo_urna": t2.nome, "partido_2": t2.partido,
            "pct_urna_1": round(t1.pct_urna, 2), "pct_poll_1": pol[t1.sq], "erro_vencedor_pp": round(e1, 2),
            "margem_poll": marg_p, "margem_urna": round(marg_u, 2), "erro_margem_pp_com_sinal_do_vencedor": round(marg_p - marg_u, 2),
            "alinh_1": a1, "alinh_2": a2, "campo_r1_1": n1, "campo_r1_2": n2,
            "subestimou_flavio_pp_r3": None if e_r3 is None else round(e_r3, 2), "subestimou_flavio_pp_exploratoria": None if e_expl is None else round(e_expl, 2), "subestimou_direita_pp_r1": None if e_r1 is None else round(e_r1, 2),
            "vencedor_certo": bool(pol[t1.sq] > pol[t2.sq]),
        })
    res = pd.DataFrame(linhas)
    res = res.merge(ach[["instituto", "uf", "margem_no_plano", "amostra"]], on=["instituto", "uf"], how="left")
    tabela("c2_erro_por_pesquisa", res)
    ok = res[res.status == "ok"].copy()
    registrar("c2.pesquisas_analisadas", int(len(ok)))
    registrar("c2.pesquisas_fora_da_analise", res[res.status != "ok"][["instituto", "uf"]].to_dict("records"))
    registrar("c2.vencedor_certo", {"certo": int(ok.vencedor_certo.sum()), "total": int(len(ok))})
    ok["erro_abs_vencedor"] = ok["erro_vencedor_pp"].abs()
    ok["erro_abs_margem"] = ok["erro_margem_pp_com_sinal_do_vencedor"].abs()
    registrar("c2.erro_medio_abs_vencedor_pp", round(float(ok.erro_abs_vencedor.mean()), 2))
    registrar("c2.erro_medio_abs_margem_pp", round(float(ok.erro_abs_margem.mean()), 2))
    registrar("c2.erro_medio_com_sinal_vencedor_pp", round(float(ok.erro_vencedor_pp.mean()), 2))
    por_inst = ok.groupby("instituto").agg(n=("uf", "size"), erro_vencedor_medio_com_sinal=("erro_vencedor_pp", "mean"), erro_vencedor_abs=("erro_abs_vencedor", "mean"), erro_margem_abs=("erro_abs_margem", "mean"), vencedor_certo=("vencedor_certo", "sum")).round(2).reset_index()
    tabela("c2_erro_por_instituto", por_inst)
    registrar("c2.por_instituto", por_inst.to_dict("records"))
    # fora da margem: |erro na proporcao| > margem declarada (2 pp quando o plano nao traz); |erro na margem| > 2 x margem
    ok["margem_decl"] = ok["margem_no_plano"].fillna(2.0)
    ok["fora_prop"] = ok["erro_abs_vencedor"] > ok["margem_decl"]
    ok["fora_margem"] = ok["erro_abs_margem"] > 2 * ok["margem_decl"]
    registrar("c2.fora_da_margem", {"proporcao": int(ok.fora_prop.sum()), "diferenca": int(ok.fora_margem.sum()), "total": int(len(ok)), "margem_usada_quando_plano_sem_numero_pp": 2.0})
    tabela("c2_pesquisas_fora_da_margem", ok[ok.fora_prop | ok.fora_margem][["instituto", "uf", "vencedor_urna", "pct_urna_1", "pct_poll_1", "erro_vencedor_pp", "erro_margem_pp_com_sinal_do_vencedor", "margem_decl"]])

    # C4: o erro tem direcao? media por disputa (entre institutos) e teste binomial do sinal
    for nome, col in (("r3_flavio", "subestimou_flavio_pp_r3"), ("r1_direita", "subestimou_direita_pp_r1"), ("exploratoria_flavio_contra_qualquer_outro", "subestimou_flavio_pp_exploratoria")):
        d = ok.dropna(subset=[col]).groupby("uf")[col].mean().reset_index()
        n = len(d)
        k = int((d[col] > 0).sum())
        # binomial bicaudal exato, p = 0,5
        pv = min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2**n) if k >= n / 2 else min(1.0, 2 * sum(comb(n, i) for i in range(0, k + 1)) / 2**n)
        por = ok.dropna(subset=[col]).groupby("instituto")[col].agg(["size", "mean"]).round(2)
        registrar(f"c4.{nome}", {"disputas": n, "disputas_em_que_subestimou": k, "p_binomial_bicaudal": round(pv, 4), "media_pp": round(float(d[col].mean()), 2), "mediana_pp": round(float(d[col].median()), 2), "por_instituto": por.reset_index().to_dict("records")})
        tabela(f"c4_direcao_{nome}", d.rename(columns={col: "subestimou_pp_media_entre_institutos"}))

    # a margem do 1o colocado foi subestimada (corrida mais apertada na pesquisa que na urna)?
    ok["margem_apertada_demais"] = ok["margem_poll"] < ok["margem_urna"]
    d = ok.groupby("uf")["margem_apertada_demais"].mean()
    n = len(d)
    k = int((d > 0.5).sum())
    pv2 = min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2**n)
    registrar("c4.margem_subestimada", {"pesquisas": int(len(ok)), "com_margem_menor_que_a_urna": int(ok.margem_apertada_demais.sum()), "disputas": n, "disputas_com_maioria_das_pesquisas_apertadas_demais": k, "p_binomial_bicaudal_disputas": round(pv2, 4), "erro_margem_medio_com_sinal_pp": round(float(ok.erro_margem_pp_com_sinal_do_vencedor.mean()), 2)})
    registrar("c4.vencedor_subestimado", {"pesquisas": int(len(ok)), "com_vencedor_abaixo_da_urna": int((ok.erro_vencedor_pp < 0).sum())})
    # os maiores erros, de qualquer lado
    mais = ok.assign(abs_erro=ok.erro_vencedor_pp.abs()).sort_values("abs_erro", ascending=False).head(8)[["instituto", "uf", "vencedor_urna", "partido_1", "pct_urna_1", "pct_poll_1", "erro_vencedor_pp", "alinh_1", "alinh_2"]]
    tabela("c2_oito_maiores_erros_no_vencedor", mais)
    registrar("c2.oito_maiores_erros", mais.to_dict("records"))

    # abstencao: variacao do comparecimento em relacao a 2022 por UF (descritivo)
    dt = detalhe()
    dt = dt[(dt.cargo == 3)].groupby(["ano", "uf"])[["aptos", "comparecimento", "abstencoes"]].sum().reset_index()
    dt["abst_pct"] = 100 * dt["abstencoes"] / dt["aptos"]
    pv = dt.pivot(index="uf", columns="ano", values="abst_pct")
    pv["var_2022_2026"] = pv[2026] - pv[2022]
    tabela("b3_abstencao_governador_por_uf", pv.reset_index().round(2))
    reg_col = ok.dropna(subset=["subestimou_flavio_pp_r3"]).groupby("uf")["subestimou_flavio_pp_r3"].mean()
    j = pd.concat([reg_col, pv["var_2022_2026"]], axis=1, join="inner").dropna()
    if len(j) >= 5:
        r = float(np.corrcoef(j.iloc[:, 0], j.iloc[:, 1])[0, 1])
        registrar("c3.correlacao_erro_flavio_x_variacao_abstencao", {"r": round(r, 3), "ufs": int(len(j))})
    print("ok C", len(po), "linhas;", len(ok), "pesquisas analisadas")


if __name__ == "__main__":
    main()
