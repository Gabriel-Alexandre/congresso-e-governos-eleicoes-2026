"""Bloco C, contra 2022 e 2018 (emenda 23): o erro das pesquisas de governador tem direcao?

O pre-registro (secao 9) previa comparar o erro de 2026 com o de 2022 pelo mesmo calculo, e isso nao tinha sido feito.
Aqui entram 2022 e 2018, com as mesmas medidas de `analise-4-pesquisas.py`:

- pesquisa: a ultima de cada instituto com campo terminado na semana antes do 1o turno (2018: 29/set a 06/out;
  2022: 24/set a 01/out; 2026: 26/set a 03/out, o c2), estimulada, 1o turno de governador;
- institutos: os nacionais de cada ano no principal (2018 Datafolha e Ibope; 2022 Datafolha, Quaest e Ipec, o antigo
  Ibope; 2026 Datafolha e Quaest, o que o projeto ja tinha); todos os institutos e so o Datafolha como conferencia;
- votos validos: o percentual de cada candidato sobre a soma dos candidatos (secao 9 do pre-registro); a pesquisa so
  entra se os candidatos que ela traz somam ao menos 90% do voto valido da urna;
- urna: o voto nominal de 1o turno do TSE; a pesquisa e a urna se ligam pelo NUMERO do candidato, nao pelo nome;
- direcao: nas disputas em que so um dos dois primeiros da urna e de direita (direita + centro-direita, emenda 22),
  quanto a pesquisa subestimou a margem do candidato de direita (positivo = mostrou a direita mais fraca que a urna);
  media entre institutos por disputa e teste do sinal, como no c4. O mesmo para a esquerda.

Fonte das pesquisas de 2018 e 2022: base do ranking de institutos do Pindograma (`capturar-pesquisas-historicas.py`).
"""
from __future__ import annotations

import sys
from datetime import date
from math import comb
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.comum import RAIZ, RES, votos_cand  # noqa: E402
from congresso.saida import registrar, tabela  # noqa: E402

CAP = RAIZ / "dados" / "brutos" / "capturas"
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
JANELA = {2018: (date(2018, 9, 29), date(2018, 10, 6)), 2022: (date(2022, 9, 24), date(2022, 10, 1))}
PRINCIPAL = {2018: {"Datafolha", "Ibope"}, 2022: {"Datafolha", "Quaest", "Ipec (antigo Ibope)"}, 2026: {"Datafolha", "Quaest"}}


def grupo(sigla: str) -> str:
    s = campos.sigla(sigla)
    s = HERDEIRO.get(s, s)
    return AUTO.get(s, "sem partido")


def tres(sigla: str) -> str:
    return {"direita": "direita", "centro-direita": "direita", "centro": "centro", "centro-esquerda": "esquerda", "esquerda": "esquerda"}.get(grupo(sigla), "sem partido")


def urna(ano: int) -> pd.DataFrame:
    v = votos_cand()
    v = v[(v.ano == ano) & (v.cargo == 3)]
    g = v.groupby(["uf", "nr", "nome", "partido"], as_index=False)["votos"].sum()
    g["pct_urna"] = 100 * g["votos"] / g.groupby("uf")["votos"].transform("sum")
    g["nr"] = g["nr"].astype(int)
    return g


def pesquisas(ano: int, ur: pd.DataFrame) -> pd.DataFrame:
    arq = CAP / ("pindograma-late-polls-2012-2018.csv" if ano == 2018 else "pindograma-late-polls-2022.csv")
    if not arq.exists():  # a captura nao vai para o git; a tabela extraida (fatos) vai e da o mesmo resultado
        e = pd.read_csv(RES / "c5_pesquisas_governador_2018_2022_extraidas.csv")
        return e[e.ano == ano].copy()
    d = pd.read_csv(arq, low_memory=False)
    d = d[(d.year == ano) & (d.CD_CARGO == 3) & (d.turno == 1) & (d.estimulada == 1)].copy()
    d["fim"] = pd.to_datetime(d.DT_FIM_PESQUISA).dt.date
    ini, fim = JANELA[ano]
    d = d[(d.fim >= ini) & (d.fim <= fim)]
    d["uf"] = d.polled_UE
    d["nr"] = pd.to_numeric(d.NUMERO_CANDIDATO, errors="coerce")
    d = d.dropna(subset=["nr", "result"])
    d["nr"] = d["nr"].astype(int)
    # votos validos da pesquisa: a soma de TODOS os candidatos que ela apresentou, antes de cruzar com a urna
    # (candidato com registro indeferido some do voto nominal do TSE, mas estava na pesquisa; ex.: Witzel, RJ 2022)
    d["soma_pesquisa"] = d.groupby(["NR_IDENTIFICACAO_PESQUISA", "scenario_id"])["result"].transform("sum")
    d = d.merge(ur[["uf", "nr", "nome", "partido", "votos", "pct_urna"]], on=["uf", "nr"], how="inner")
    # cenario: o que cobre mais voto da urna; pesquisa so entra se cobre ao menos 90% do voto valido
    cob = d.groupby(["NR_IDENTIFICACAO_PESQUISA", "scenario_id", "uf", "pretty_name", "fim"], as_index=False).agg(pct_urna_coberto=("pct_urna", "sum"), soma=("soma_pesquisa", "first"), n=("nr", "size"))
    cob = cob[cob.pct_urna_coberto >= 90].sort_values(["pct_urna_coberto", "n"], ascending=False)
    cob = cob.drop_duplicates(["NR_IDENTIFICACAO_PESQUISA"])
    # a ultima de cada instituto em cada UF
    cob = cob.sort_values(["pretty_name", "uf", "fim"], ascending=[True, True, False]).drop_duplicates(["pretty_name", "uf"])
    d = d.merge(cob[["NR_IDENTIFICACAO_PESQUISA", "scenario_id", "soma", "pct_urna_coberto"]], on=["NR_IDENTIFICACAO_PESQUISA", "scenario_id"])
    d["pct_valido"] = (100 * d["result"] / d["soma"]).round(2)
    d["ano"] = ano
    return d.rename(columns={"pretty_name": "instituto", "NR_IDENTIFICACAO_PESQUISA": "registro_tse"})


def sinal(lado1, lado2, alvo, M):
    if lado1 == alvo and lado2 != alvo:
        return -M
    if lado2 == alvo and lado1 != alvo:
        return M
    return None


def medir(ano: int, pol: pd.DataFrame, ur: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (inst, uf), g in pol.groupby(["instituto", "uf"]):
        u = ur[ur.uf == uf].sort_values("votos", ascending=False)
        t1, t2 = u.iloc[0], u.iloc[1]
        p = dict(zip(g.nr, g.pct_valido))
        if t1.nr not in p or t2.nr not in p:
            out.append({"ano": ano, "instituto": inst, "uf": uf, "status": "top2 da urna fora da pesquisa"})
            continue
        mp, mu = p[t1.nr] - p[t2.nr], t1.pct_urna - t2.pct_urna
        M = mp - mu
        l1, l2 = tres(t1.partido), tres(t2.partido)
        sd, se = sinal(l1, l2, "direita", M), sinal(l1, l2, "esquerda", M)
        out.append({"ano": ano, "instituto": inst, "uf": uf, "status": "ok", "registro_tse": g.registro_tse.iloc[0], "fim_campo": str(g.fim.iloc[0]),
                    "vencedor_urna": t1.nome, "partido_1": t1.partido, "lado_1": l1, "segundo_urna": t2.nome, "partido_2": t2.partido, "lado_2": l2,
                    "pct_urna_1": round(t1.pct_urna, 2), "pct_poll_1": p[t1.nr], "erro_vencedor_pp": round(p[t1.nr] - t1.pct_urna, 2),
                    "margem_poll": round(mp, 2), "margem_urna": round(mu, 2),
                    "subestimou_direita_pp": None if sd is None else round(sd, 2), "subestimou_esquerda_pp": None if se is None else round(se, 2),
                    "vencedor_certo": bool(p[t1.nr] > p[t2.nr])})
    return pd.DataFrame(out)


def p_sinal(n: int, k: int) -> float:
    if n == 0:
        return 1.0
    a = sum(comb(n, i) for i in range(k, n + 1)) if k >= n / 2 else sum(comb(n, i) for i in range(0, k + 1))
    return round(min(1.0, 2 * a / 2**n), 4)


def resumo(ano: int, ok: pd.DataFrame) -> dict:
    r = {"ano": ano, "pesquisas": int(len(ok)), "disputas": int(ok.uf.nunique()),
         "vencedor_abaixo_da_urna": int((ok.erro_vencedor_pp < 0).sum()),
         "pct_vencedor_abaixo": round(100 * float((ok.erro_vencedor_pp < 0).mean()), 1) if len(ok) else None,
         "erro_medio_vencedor_pp": round(float(ok.erro_vencedor_pp.mean()), 2) if len(ok) else None,
         "erro_medio_abs_vencedor_pp": round(float(ok.erro_vencedor_pp.abs().mean()), 2) if len(ok) else None,
         "vencedor_certo": int(ok.vencedor_certo.sum())}
    for lado in ("direita", "esquerda"):
        col = f"subestimou_{lado}_pp"
        d = ok.dropna(subset=[col]).groupby("uf")[col].mean()
        n, k = int(len(d)), int((d > 0).sum())
        r[f"{lado}_disputas"] = n
        r[f"{lado}_subestimada_em"] = k
        r[f"{lado}_media_pp"] = round(float(d.mean()), 2) if n else None
        r[f"{lado}_mediana_pp"] = round(float(d.median()), 2) if n else None
        r[f"{lado}_p_sinal"] = p_sinal(n, k)
    return r


def limpo(r: dict) -> dict:
    return {k: (v.item() if hasattr(v, "item") else v) for k, v in r.items() if k != "ano"}


# segunda fonte: os votos validos que a imprensa publicou na vespera, contra o que este script extraiu
CONFERENCIA = [
    (2022, "SP", "Datafolha", {"HADDAD": 39, "TARCÍSIO": 31, "GARCIA": 23}, "cnnbrasil.com.br/politica/resultados-das-urnas-divergem-das-pesquisas-eleitorais-em-21-estados-e-no-df"),
    (2022, "RJ", "Datafolha", {"CASTRO": 44, "FREIXO": 35}, "idem"),
    (2022, "BA", "Datafolha", {"NETO": 51, "JERÔNIMO": 38}, "idem"),
    (2022, "BA", "Ipec (antigo Ibope)", {"NETO": 51, "JERÔNIMO": 40}, "idem"),
    (2022, "RS", "Ipec (antigo Ibope)", {"LEITE": 40, "LORENZONI": 30}, "idem"),
    (2018, "MG", "Datafolha", {"ANASTASIA": 40, "PIMENTEL": 29, "ZEMA": 24}, "jb.com.br/pais/eleicoes_2018/2018/10/944723 (registro MG-08940/2018)"),
    (2018, "RJ", "Datafolha", {"PAES": 27, "ROMÁRIO": 17, "WITZEL": 17}, "exame.com/brasil/datafolha-paes-tem-27-de-votos-validos-no-rj-romario-e-witzel-empatam"),
    (2018, "RJ", "Ibope", {"PAES": 32, "ROMÁRIO": 20, "WITZEL": 12}, "istoe.com.br/ibope-paes-tem-32-romario-20-indio-e-witzel-12"),
]


def conferencia(ext: pd.DataFrame) -> None:
    linhas = []
    for ano, uf, inst, pub, fonte in CONFERENCIA:
        g = ext[(ext.ano == ano) & (ext.uf == uf) & (ext.instituto == inst)]
        for sobrenome, v in pub.items():
            x = g[g.nome.str.upper().str.contains(sobrenome)]
            ext_v = float(x.pct_valido.iloc[0]) if len(x) else None
            linhas.append({"ano": ano, "uf": uf, "instituto": inst, "candidato": sobrenome, "publicado": v, "extraido": ext_v,
                           "diferenca": None if ext_v is None else round(ext_v - v, 1), "fonte": fonte})
    c = pd.DataFrame(linhas)
    tabela("c5_conferencia_segunda_fonte", c)
    registrar("c5.conferencia", {"numeros": int(len(c)), "maior_diferenca_pp": float(c.diferenca.abs().max()), "ate_1_ponto": int((c.diferenca.abs() <= 1).sum())})


def grafico(res: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 22, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white"})
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(top=0.80, bottom=0.14, left=0.08, right=0.97)
    fig.text(0.05, 0.93, "Governador: quem as pesquisas mostraram mais fraco do que a urna", fontsize=30, fontweight="bold")
    fig.text(0.05, 0.875, "% das disputas em que a última pesquisa mostrou o lado mais fraco do que a urna (média dos institutos, margem entre os dois primeiros)", fontsize=19, color="#444")
    anos = [2018, 2022, 2026]
    w = 0.36
    for j, (lado, cor) in enumerate((("direita", "#1F44AE"), ("esquerda", "#D32F2F"))):
        v = [100 * res.loc[res.ano == a, f"{lado}_subestimada_em"].iloc[0] / res.loc[res.ano == a, f"{lado}_disputas"].iloc[0] for a in anos]
        n = [(int(res.loc[res.ano == a, f"{lado}_subestimada_em"].iloc[0]), int(res.loc[res.ano == a, f"{lado}_disputas"].iloc[0])) for a in anos]
        xs = [i + (j - 0.5) * w for i in range(3)]
        ax.bar(xs, v, w, color=cor, label=f"{lado} mais fraca do que a urna")
        for x, y, (k, m) in zip(xs, v, n):
            ax.text(x, y + 1.5, f"{y:.0f}%", ha="center", fontsize=26, fontweight="bold")
            ax.text(x, y - 6, f"{k} de {m}", ha="center", fontsize=17, color="white")
    ax.axhline(50, color="#777", ls="--", lw=1.5)
    ax.text(-0.55, 51.5, "metade", fontsize=16, color="#555", ha="left")
    ax.set_xticks(range(3)); ax.set_xticklabels([str(a) for a in anos], fontsize=26); ax.set_ylim(0, 100); ax.set_yticks([])
    ax.legend(frameon=False, fontsize=20, loc="upper right")
    fig.text(0.05, 0.035, "Fonte: TSE; pesquisas de 2018 e 2022: base do ranking de institutos do Pindograma (registro no TSE). 2018: Datafolha e Ibope; 2022: Datafolha, Quaest e Ipec;\n"
             "2026: Datafolha e Quaest. Direita inclui a centro-direita; esquerda inclui a centro-esquerda. Só disputas em que um dos dois primeiros é do lado e o outro não.", fontsize=13, color="#555")
    fig.savefig(RES / "figuras" / "video" / "28_pesquisas_quem_saiu_mais_fraco_2018_2022_2026.png")
    plt.close(fig)


def main() -> None:
    ext, med = [], []
    for ano in (2018, 2022):
        ur = urna(ano)
        pol = pesquisas(ano, ur)
        ext.append(pol)
        med.append(medir(ano, pol, ur))
    ext = pd.concat(ext, ignore_index=True)
    tabela("c5_pesquisas_governador_2018_2022_extraidas", ext[["ano", "uf", "instituto", "registro_tse", "fim", "nr", "nome", "partido", "result", "soma", "pct_valido", "pct_urna", "pct_urna_coberto"]].sort_values(["ano", "uf", "instituto", "pct_valido"], ascending=[True, True, True, False]))

    # 2026, pelo mesmo calculo, a partir do c2 (Datafolha e Quaest)
    c2 = pd.read_csv(RES / "c2_erro_por_pesquisa.csv")
    c2 = c2[c2.status == "ok"].copy()
    c2["lado_1"], c2["lado_2"] = c2.partido_1.map(tres), c2.partido_2.map(tres)
    M = c2.margem_poll - c2.margem_urna
    c2["subestimou_direita_pp"] = [sinal(a, b, "direita", m) for a, b, m in zip(c2.lado_1, c2.lado_2, M)]
    c2["subestimou_esquerda_pp"] = [sinal(a, b, "esquerda", m) for a, b, m in zip(c2.lado_1, c2.lado_2, M)]
    c2["ano"] = 2026
    cols = ["ano", "instituto", "uf", "status", "vencedor_urna", "partido_1", "lado_1", "segundo_urna", "partido_2", "lado_2", "pct_urna_1", "pct_poll_1",
            "erro_vencedor_pp", "margem_poll", "margem_urna", "subestimou_direita_pp", "subestimou_esquerda_pp", "vencedor_certo"]
    tudo = pd.concat(med + [c2[cols]], ignore_index=True)
    tudo["principal"] = [i in PRINCIPAL[a] for a, i in zip(tudo.ano, tudo.instituto)]
    tabela("c5_erro_por_pesquisa_2018_2022_2026", tudo)
    ok = tudo[tudo.status == "ok"].copy()
    for c in ("subestimou_direita_pp", "subestimou_esquerda_pp", "erro_vencedor_pp"):
        ok[c] = pd.to_numeric(ok[c], errors="coerce")
    registrar("c5.fonte", {"2018_2022": "Pindograma, ranking de institutos (commit c04d197), pesquisas com registro no TSE", "2026": "c1/c2 do projeto"})
    registrar("c5.institutos_principais", {a: sorted(v) for a, v in PRINCIPAL.items()})
    registrar("c5.fora_da_analise", int((tudo.status != "ok").sum()))
    saidas = {}
    for nome, filtro in (("principal", ok.principal), ("todos_os_institutos", ok.principal | True), ("so_datafolha", ok.instituto == "Datafolha")):
        res = pd.DataFrame([resumo(a, ok[filtro & (ok.ano == a)]) for a in (2018, 2022, 2026)])
        tabela(f"c5_resumo_por_ano_{nome}", res)
        registrar(f"c5.{nome}", {int(r["ano"]): limpo(r) for r in res.to_dict("records")})
        saidas[nome] = res
    conferencia(ext)
    grafico(saidas["principal"])
    dd = ok[ok.principal].dropna(subset=["subestimou_direita_pp"]).groupby(["ano", "uf"]).agg(subestimou_direita_pp=("subestimou_direita_pp", "mean"), institutos=("instituto", "size")).round(2).reset_index()
    tabela("c5_direita_por_disputa", dd)
    for k, v in saidas.items():
        print("==", k)
        print(v[["ano", "pesquisas", "disputas", "pct_vencedor_abaixo", "erro_medio_vencedor_pp", "direita_disputas", "direita_subestimada_em", "direita_media_pp", "direita_mediana_pp", "direita_p_sinal", "esquerda_disputas", "esquerda_subestimada_em", "esquerda_media_pp", "esquerda_p_sinal"]].to_string())


if __name__ == "__main__":
    main()
