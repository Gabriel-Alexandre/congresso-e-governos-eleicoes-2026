"""Dados e quadros de referência para as animações do vídeo (cadeiras da Câmara e do Senado, mapas dos estados)
e os gráficos do parâmetro principal (autodeclaração dos partidos, emenda 21).

A cor é a do GRUPO em que o partido se declara (ferramentas/analise-11-pl-e-blocos.py): vermelho esquerda,
rosa centro-esquerda, cinza centro, azul-claro centro-direita, azul forte direita; o PL tem o azul-escuro próprio.
Saídas: resultados/animacao/*.json, resultados/figuras/video/15 a 26 e as versões borradas para o trailer.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.comum import RAIZ, RES  # noqa: E402

_spec = importlib.util.spec_from_file_location("blocos", Path(__file__).with_name("analise-11-pl-e-blocos.py"))
blocos = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blocos)
grupo = blocos.grupo
GRUPOS = blocos.GRUPOS

OUT = RES / "figuras" / "video"
ANI = RES / "animacao"
ANI.mkdir(parents=True, exist_ok=True)
R = json.loads((RES / "RESUMO.json").read_text(encoding="utf-8"))
FONTE = "Fonte: TSE e Senado (07/out/2026). Grupo = como o partido se declara (Valor Econômico, ago/2026). PL em azul-escuro."
plt.rcParams.update({"font.size": 22, "figure.facecolor": "white"})

PL_COR = "#0B2C6B"
COR_GRUPO = {"esquerda": "#D32F2F", "centro-esquerda": "#F06292", "centro": "#9E9E9E", "centro-direita": "#64B5F6", "direita": "#1E40AF", "sem partido": "#CFCFCF"}
TONS = {
    "esquerda": ["#B71C1C", "#D32F2F", "#E53935", "#EF5350", "#E57373"],
    "centro-esquerda": ["#EC407A", "#F06292", "#F48FB1"],
    "centro": ["#616161", "#757575", "#8D8D8D", "#9E9E9E", "#B0B0B0", "#C2C2C2", "#D5D5D5"],
    "centro-direita": ["#42A5F5", "#64B5F6", "#90CAF9", "#4FC3F7"],
    "direita": ["#3949AB", "#5C6BC0"],
    "sem partido": ["#CFCFCF"],
}
ORDEM_GRUPO = {g: i for i, g in enumerate(["esquerda", "centro-esquerda", "centro", "centro-direita", "direita", "sem partido"])}
NOME_GRUPO = {"direita": "direita (PL, Novo, Missão)", "centro-direita": "centro-direita (PP, Republicanos, União, PRD)", "centro": "centro (MDB, PSD, Podemos, PSDB...)",
              "centro-esquerda": "centro-esquerda (PSB, PDT, Rede)", "esquerda": "esquerda (PT, PCdoB, PV, PSOL)"}


def chave_ordem(p):
    """esquerda -> direita por grupo; dentro do grupo, pela nota R1 (PL por último, na ponta direita)."""
    s = campos.sigla(p)
    n = campos.nota_r1(p, R["a1"]["pesos_fusoes"])
    return (ORDEM_GRUPO.get(grupo(p), 9), 1 if s == "PL" else 0, n if n is not None else 99, s)


def paleta(partidos):
    cor, usados = {}, {k: 0 for k in TONS}
    for p in sorted(partidos, key=chave_ordem):
        if campos.sigla(p) == "PL":
            cor[p] = PL_COR
            continue
        g = grupo(p)
        lista = TONS.get(g, TONS["sem partido"])
        cor[p] = lista[usados.get(g, 0) % len(lista)]
        usados[g] = usados.get(g, 0) + 1
    return cor


def hemiciclo(n, linhas=None):
    linhas = linhas or max(4, int(round(math.sqrt(n / 2.2))))
    raios = np.linspace(1.0, 2.2, linhas)
    comp = raios / raios.sum()
    por = np.floor(comp * n).astype(int)
    por[-1] += n - por.sum()
    pts = []
    for r, k in zip(raios, por):
        ang = np.linspace(math.pi, 0, k)
        pts += [(r * math.cos(a), r * math.sin(a), a) for a in ang]
    pts.sort(key=lambda t: (-t[2], t[0]))
    return [(x, y) for x, y, _ in pts]


def desenhar_hemiciclo(assentos, titulo, sub, nome, total_txt, legenda, nota_rodape=None):
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.85, bottom=0.18)
    fig.suptitle(titulo, x=0.05, y=0.97, ha="left", fontsize=30, fontweight="bold")
    fig.text(0.05, 0.895, sub, fontsize=20, color="#444")
    xy = hemiciclo(len(assentos))
    tam = 260 if len(assentos) < 100 else 34
    ax.scatter([p[0] for p in xy], [p[1] for p in xy], s=tam, c=[a["cor"] for a in assentos], edgecolors="white", linewidths=0.3)
    ax.text(0, 0.25, total_txt, ha="center", va="center", fontsize=34, fontweight="bold")
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-2.4, 2.4); ax.set_ylim(-0.1, 2.35)
    x = 0.05
    for rot, cor in legenda:
        fig.text(x, 0.09, "●", color=cor, fontsize=30, va="center")
        fig.text(x + 0.022, 0.09, rot, fontsize=19, va="center")
        x += 0.022 + 0.0085 * len(rot) + 0.02
    fig.text(0.05, 0.02, nota_rodape or FONTE, fontsize=14, color="#555")
    fig.savefig(OUT / f"{nome}.png")
    plt.close(fig)


def legenda_grupos(contagem, pl):
    lg = [(f"PL {pl}", PL_COR)]
    for g in ("direita", "centro-direita", "centro", "centro-esquerda", "esquerda"):
        n = contagem.get(g, 0) - (pl if g == "direita" else 0)
        rot = "outros de direita" if g == "direita" else g
        if n > 0:
            lg.append((f"{rot} {n}", COR_GRUPO[g] if g != "direita" else TONS["direita"][0]))
    return lg


def assentos_de(contagem_por_partido, cor):
    ordem = sorted(contagem_por_partido.index, key=chave_ordem)
    out = []
    for p in ordem:
        for _ in range(int(contagem_por_partido[p])):
            out.append({"partido": p, "grupo": grupo(p), "cor": cor[p]})
    return ordem, out


def camara():
    cad = pd.read_csv(RES / "a1_cadeiras_por_partido_e_ano.csv").set_index("sig")
    saida = {}
    todos = sorted(set(cad.index[cad["2022"] > 0]) | set(cad.index[cad["2026"] > 0]))
    cor = paleta(todos)
    for ano in ("2022", "2026"):
        c = cad[ano][cad[ano] > 0]
        ordem, assentos = assentos_de(c, cor)
        cont = pd.Series([a["grupo"] for a in assentos]).value_counts().to_dict()
        saida[ano] = {"total": len(assentos), "contagem_por_grupo": cont,
                      "ordem_dos_partidos": [{"partido": p, "cadeiras": int(c[p]), "grupo": grupo(p), "cor": cor[p]} for p in ordem], "assentos": assentos}
        dc = cont.get("direita", 0) + cont.get("centro-direita", 0)
        desenhar_hemiciclo(assentos, f"Câmara eleita em {ano}: 513 cadeiras",
                           f"Direita {cont.get('direita', 0)} · centro-direita {cont.get('centro-direita', 0)} · centro {cont.get('centro', 0)} · centro-esquerda {cont.get('centro-esquerda', 0)} · esquerda {cont.get('esquerda', 0)}",
                           f"{15 if ano == '2022' else 16}_camara_cadeiras_{ano}", f"PL {int(c.get('PL', 0))}", legenda_grupos(cont, int(c.get("PL", 0))))
        saida[ano]["direita_mais_centro_direita"] = dc
    saida["limiares"] = {"CPI": 171, "bloquear_PEC": 206, "maioria_absoluta": 257, "PEC": 308, "impeachment_autorizar": 342}
    (ANI / "camara_2022_2026.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")


def senado():
    comp = pd.read_csv(RES / "a2_composicao_fev2027.csv")
    comp["sig"] = comp["sig"].fillna("S/PARTIDO")
    api = json.loads((RAIZ / "dados/brutos/senado/atual.json").read_text(encoding="utf-8"))["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    hoje = pd.DataFrame([{"nome": p["IdentificacaoParlamentar"]["NomeParlamentar"], "uf": p["IdentificacaoParlamentar"]["UfParlamentar"],
                          "sig": campos.sigla(p["IdentificacaoParlamentar"].get("SiglaPartidoParlamentar", "") or "S/PARTIDO")} for p in api])
    cor = paleta(list(set(comp.sig) | set(hoje.sig)))
    out = {"limiares": {"CPI": 27, "bloquear_PEC": 33, "maioria_absoluta": 41, "PEC": 49, "condenar_impeachment": 54}}
    for rot, df, nome, titulo in (("hoje", hoje, "21_senado_cadeiras_hoje", "Senado hoje (out/2026): 81 cadeiras"),
                                  ("2027", comp, "17_senado_cadeiras_2027", "Senado a partir de fevereiro de 2027: 81 cadeiras")):
        df = df.assign(k=df.sig.map(chave_ordem)).sort_values("k")
        assentos = [{"partido": r.sig, "uf": r.uf, "nome": r.nome, "grupo": grupo(r.sig), "cor": cor[r.sig], **({"origem": r.origem} if "origem" in df else {})} for r in df.itertuples()]
        cont = pd.Series([a["grupo"] for a in assentos]).value_counts().to_dict()
        pl = int((df.sig == "PL").sum())
        dc = cont.get("direita", 0) + cont.get("centro-direita", 0)
        out[rot] = {"total": len(assentos), "contagem_por_grupo": cont, "PL": pl, "direita_mais_centro_direita": dc, "assentos": assentos}
        desenhar_hemiciclo(assentos, titulo,
                           f"Direita {cont.get('direita', 0)} · centro-direita {cont.get('centro-direita', 0)} · centro {cont.get('centro', 0)} · centro-esquerda {cont.get('centro-esquerda', 0)} · esquerda {cont.get('esquerda', 0)} · direita + centro-direita = {dc} (PEC 49, impeachment 54)",
                           nome, f"PL {pl}", legenda_grupos(cont, pl))
    (ANI / "senado_hoje_e_2027.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    old = ANI / "senado_2027.json"
    if old.exists():
        old.unlink()


def mapa_ufs(cores_uf, titulo, sub, nome, legenda, rotulos=None, rodape=None):
    gj = json.loads((RAIZ / "dados/brutos/ibge/malha_ufs_minima.json").read_text(encoding="utf-8"))
    cod = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
    escuros = {PL_COR, COR_GRUPO["direita"], COR_GRUPO["esquerda"], "#3F6CB5", "#3949AB"}
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    ax = fig.add_axes([0.08, 0.08, 0.6, 0.78])
    fig.suptitle(titulo, x=0.04, y=0.97, ha="left", fontsize=30, fontweight="bold")
    fig.text(0.04, 0.91, sub, fontsize=20, color="#444")
    for f in gj["features"]:
        uf = cod[f["properties"]["codarea"]]
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for p in polys:
            ax.add_patch(Polygon(np.array(p[0]), closed=True, facecolor=cores_uf.get(uf, "#EEEEEE"), edgecolor="white", linewidth=0.3 if uf == "DF" else 1.2))
        if rotulos:
            arr = np.vstack([np.array(p[0]) for p in polys])
            cx, cy = arr[:, 0].mean(), arr[:, 1].mean()
            dx, dy = {"DF": (1.6, 0.9), "GO": (-1.2, -0.6), "RJ": (1.4, -0.9), "ES": (1.2, 0.0), "SE": (0.9, -0.4), "AL": (1.0, 0.0)}.get(uf, (0, 0))
            fora = uf in ("DF", "RJ", "ES", "SE", "AL")
            ax.text(cx + dx, cy + dy, rotulos.get(uf, uf), ha="center", va="center", fontsize=13,
                    color="#222" if fora else ("white" if cores_uf.get(uf) in escuros else "#222"), fontweight="bold")
    ax.set_xlim(-74.5, -34); ax.set_ylim(-34, 5.5); ax.set_aspect("equal"); ax.axis("off")
    y = 0.75
    for rot, cor in legenda:
        fig.text(0.68, y, "■", color=cor, fontsize=34, va="center")
        fig.text(0.705, y, rot, fontsize=18, va="center")
        y -= 0.06
    fig.text(0.04, 0.02, rodape or "Fonte: TSE (07/out/2026) e IBGE (malha). Grupo = como o partido se declara (Valor Econômico, ago/2026).", fontsize=14, color="#555")
    fig.savefig(OUT / f"{nome}.png")
    plt.close(fig)


def cor_estado(partido):
    if campos.sigla(partido) == "PL":
        return PL_COR
    return COR_GRUPO.get(grupo(partido), "#EEEEEE")


def governos():
    g = pd.read_csv(RES / "a3_governos.csv")
    apo = pd.read_csv(RAIZ / "dados" / "apoios_declarados.csv")
    dados = {}
    for ano in (2022, 2026):
        x = g[g.ano == ano]
        cores, rot, lista = {}, {}, []
        for r in x.itertuples():
            if r.situacao == "2o turno em disputa":
                cores[r.uf] = "#E6E6E6"
                lista.append({"uf": r.uf, "situacao": "2o turno", "finalistas": r.finalistas})
            else:
                c = cor_estado(r.partido)
                cores[r.uf] = c
                a = apo[(apo.ano == ano) & (apo.uf == r.uf)]
                lista.append({"uf": r.uf, "situacao": r.situacao, "governador": r.nome, "partido": r.partido, "grupo": grupo(r.partido), "cor": c,
                              "apoio_declarado": a.apoio.iloc[0] if len(a) else None})
            rot[r.uf] = r.uf
        dados[str(ano)] = lista
        dec = x[x.situacao != "2o turno em disputa"]
        ct = dec.partido.map(grupo).value_counts()
        npl = int((dec.partido == "PL").sum())
        leg = [("PL", PL_COR), ("outros de direita", COR_GRUPO["direita"]), ("centro-direita", COR_GRUPO["centro-direita"]), ("centro", COR_GRUPO["centro"]),
               ("centro-esquerda", COR_GRUPO["centro-esquerda"]), ("esquerda", COR_GRUPO["esquerda"])] + ([("2º turno em 25/out", "#E6E6E6")] if ano == 2026 else [])
        sub = (f"{len(dec)} decididos: direita {ct.get('direita', 0)} (PL {npl}), centro-direita {ct.get('centro-direita', 0)}, centro {ct.get('centro', 0)}, "
               f"centro-esquerda {ct.get('centro-esquerda', 0)}, esquerda {ct.get('esquerda', 0)}") + (f" · {int((x.situacao == '2o turno em disputa').sum())} em 2º turno" if ano == 2026 else "")
        mapa_ufs(cores, f"Governos estaduais, {ano}" + (" (1º turno)" if ano == 2026 else ""), sub, f"{18 if ano == 2022 else 19}_mapa_governos_{ano}", leg, rot)
    (ANI / "governos_2022_2026.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


def senado_por_uf():
    e = pd.read_csv(RES / "a2_composicao_fev2027.csv")
    e = e[e.origem == "eleito em 2026"]
    cores, rot, dados = {}, {}, {}
    for uf, x in e.groupby("uf"):
        npl = int((x.sig == "PL").sum())
        gs = [grupo(s) for s in x.sig]
        dir_ = sum(k == "direita" for k in gs)
        esq = sum(k in ("esquerda", "centro-esquerda") for k in gs)
        if npl == 2:
            c = PL_COR
        elif dir_ >= 1:
            c = COR_GRUPO["direita"]
        elif esq == 0:
            c = COR_GRUPO["centro-direita"] if any(k == "centro-direita" for k in gs) else COR_GRUPO["centro"]
        elif esq == 1:
            c = "#CE93D8"
        else:
            c = COR_GRUPO["esquerda"]
        cores[uf] = c
        rot[uf] = uf
        dados[uf] = [{"nome": r.nome, "partido": r.sig, "grupo": grupo(r.sig)} for r in x.itertuples()]
    (ANI / "senado_eleitos_por_uf_2026.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    leg = [("2 do PL", PL_COR), ("1 de direita (PL ou Novo)", COR_GRUPO["direita"]), ("centro-direita, sem direita", COR_GRUPO["centro-direita"]), ("centro, sem direita", COR_GRUPO["centro"]),
           ("1 de esquerda ou centro-esquerda", "#CE93D8"), ("2 de esquerda ou centro-esquerda", COR_GRUPO["esquerda"])]
    mapa_ufs(cores, "Senado, 2026: quem levou as duas vagas de cada estado", f"PL {int((e.sig == 'PL').sum())} das 54 vagas · direita declarada {sum(grupo(s) == 'direita' for s in e.sig)}", "20_mapa_senado_2026", leg, rot)


def figura_barras(nome, titulo, sub, rodape):
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.14)
    fig.suptitle(titulo, x=0.05, y=0.96, ha="left", fontsize=30, fontweight="bold")
    fig.text(0.05, 0.885, sub, fontsize=20, color="#444")
    fig.text(0.05, 0.02, rodape, fontsize=14, color="#555")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return fig, ax


def grafico_grupos_camara():
    e1 = pd.read_csv(RES / "e1_camara_por_grupo.csv")
    fig, ax = figura_barras("22", "Câmara: cadeiras por grupo, como cada partido se declara", "2018, 2022 e 2026 · 513 cadeiras",
                            "Fonte: TSE. Grupo = autodeclaração do partido (Valor Econômico, ago/2026); sigla antiga vai para o partido herdeiro (PSL e DEM → União).")
    anos = [2018, 2022, 2026]
    x = np.arange(len(GRUPOS))
    w = 0.26
    tons = {2018: 0.35, 2022: 0.65, 2026: 1.0}
    for i, a in enumerate(anos):
        v = [int(e1[(e1.ano == a) & (e1.grupo == g)].cadeiras.iloc[0]) for g in GRUPOS]
        bars = ax.bar(x + (i - 1) * w, v, w, color=[COR_GRUPO[g] for g in GRUPOS], alpha=tons[a], label=str(a))
        for b, n in zip(bars, v):
            ax.text(b.get_x() + b.get_width() / 2, n + 3, str(n), ha="center", fontsize=17, fontweight="bold" if a == 2026 else None)
    ax.set_xticks(x)
    ax.set_xticklabels([g.replace("-", "-\n") for g in GRUPOS])
    ax.set_ylabel("cadeiras")
    ax.text(0.99, 0.95, "barras: 2018 · 2022 · 2026 (mais forte)", transform=ax.transAxes, ha="right", fontsize=17, color="#555")
    fig.savefig(OUT / "22_camara_cadeiras_por_grupo.png")
    plt.close(fig)


def grafico_escada(nome, casa, tab, limiares, total, rodape):
    t = pd.read_csv(RES / tab).iloc[0]
    d, dc, dcc = int(t.direita_sozinha), int(t.direita_mais_centro_direita), int(t.direita_centro_direita_e_centro)
    esq = int(t.esquerda_e_centro_esquerda)
    fig, ax = figura_barras(nome, f"{casa}: até onde cada grupo chega se votar unido", f"{total} cadeiras · linhas = os votos que cada decisão exige", rodape)
    linhas = [("direita (PL, Novo, Missão)", d, COR_GRUPO["direita"]), ("+ centro-direita", dc, COR_GRUPO["centro-direita"]), ("+ centro", dcc, COR_GRUPO["centro"]),
              ("esquerda + centro-esquerda", esq, COR_GRUPO["esquerda"])]
    y = np.arange(len(linhas))[::-1]
    for (rot, v, c), yy in zip(linhas, y):
        ax.barh(yy, v, color=c, height=0.55)
        ax.text(v + total * 0.01, yy, str(v), va="center", fontsize=22, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([l[0] for l in linhas])
    fig.subplots_adjust(left=0.25, right=0.96, top=0.74)
    for i, (rot, n) in enumerate(limiares):
        ax.axvline(n, color="#222", lw=1.6, ls="--", zorder=0)
        ax.text(n, len(linhas) - 0.5 + 0.42 * (i % 3), f"{n} · {rot.replace(chr(10), ' ')}", ha="center", va="bottom", fontsize=15,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.set_xlim(0, total)
    ax.set_ylim(-0.6, len(linhas) + 0.95)
    fig.savefig(OUT / f"{nome}.png")
    plt.close(fig)


def grafico_pl():
    o = pd.read_csv(RES / "e5_pl_121_resumo.csv")
    ordem = ["eleito em 2022 pelo PL", "eleito em 2022 por outro partido e foi para o PL", "assumiu o mandato depois de 2022 (suplente) e se elegeu pelo PL",
             "disputou deputado federal em 2022 e não se elegeu", "primeira disputa para deputado federal (desde 2022)"]
    rot = ["já eram do PL\n(eleitos em 2022)", "vieram de outro\npartido", "suplente que\nassumiu", "perderam em 2022\ne voltaram", "primeira disputa"]
    v = [int(o.set_index("origem").cadeiras.get(k, 0)) for k in ordem]
    fig, ax = figura_barras("25", "De onde vieram os 121 deputados do PL", "Eleitos em 2026, pela história de cada um em 2022",
                            "Fonte: TSE (candidaturas de 2022 e 2026, mesma pessoa por nome e data de nascimento) e Câmara (bancada na véspera).")
    bars = ax.bar(range(len(v)), v, color=[PL_COR, "#3949AB", "#5C6BC0", "#7986CB", "#9FA8DA"])
    for b, n in zip(bars, v):
        ax.text(b.get_x() + b.get_width() / 2, n + 1, str(n), ha="center", fontsize=24, fontweight="bold")
    ax.set_xticks(range(len(v)))
    ax.set_xticklabels(rot, fontsize=18)
    fig.savefig(OUT / "25_pl_de_onde_vieram_os_121.png")
    plt.close(fig)

    d = R["e5"]["pl_98_destino"]
    ordem = ["reeleito deputado pelo PL", "disputou senador: eleito", "disputou governador: eleito", "disputou deputado estadual: eleito",
             "disputou deputado e não se elegeu", "disputou senador: não eleito", "não disputou nenhum cargo em 2026"]
    rot = ["reeleitos\ndeputados", "eleitos\nsenadores", "eleito\ngovernador", "eleitos dep.\nestaduais", "perderam a\nreeleição", "perderam\no Senado", "não\ndisputaram"]
    v = [int(d.get(k, 0)) for k in ordem]
    fig, ax = figura_barras("26", "Os 98 deputados que o PL tinha na véspera: o que houve com cada um", "Eleição de 2026",
                            "Fonte: TSE (candidaturas de 2026) e Câmara (deputados em exercício em 30/09/2026).")
    bars = ax.bar(range(len(v)), v, color=[PL_COR, "#1E40AF", "#3949AB", "#5C6BC0", "#BDBDBD", "#BDBDBD", "#E0E0E0"])
    for b, n in zip(bars, v):
        ax.text(b.get_x() + b.get_width() / 2, n + 1, str(n), ha="center", fontsize=24, fontweight="bold")
    ax.set_xticks(range(len(v)))
    ax.set_xticklabels(rot, fontsize=18)
    fig.savefig(OUT / "26_pl_os_98_da_vespera.png")
    plt.close(fig)


def nomes_trailer():
    """Os nomes do trailer, com o resultado oficial de cada um (para os cartões da edição)."""
    s = pd.read_csv(RES / "e6_senado_esquerda_mais_votados_nao_eleitos.csv")
    c = pd.read_csv(RES / "e6_esquerda_que_disputou_e_nao_se_elegeu.csv")
    e6 = pd.read_csv(RES / "e6_eleitos_2022_e_o_que_houve_em_2026.csv")
    out = {"senado_nao_eleitos": s.head(10).to_dict("records"),
           "camara_e_governo_nao_eleitos": c.head(20)[["nome", "uf", "partido_2022", "votos_2022", "cargo_2026", "partido_2026", "situacao"]].to_dict("records"),
           "janones": e6[e6.nome.str.contains("JANONES", na=False)].to_dict("records")}
    (ANI / "nomes_do_trailer.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def borrar():
    for n in ("05_puxadores_cadeiras_garantidas", "10_pesquisas_erro_no_vencedor", "16_camara_cadeiras_2026", "19_mapa_governos_2026",
              "23_camara_limiares_2026", "24_senado_limiares_2027", "17_senado_cadeiras_2027"):
        im = Image.open(OUT / f"{n}.png").convert("RGB").filter(ImageFilter.GaussianBlur(18))
        im.save(OUT / f"{n}_borrado.png")
    for velho in ("01_camara_cadeiras_por_campo_r1_borrado", "02_camara_ganhos_e_perdas_por_partido_borrado"):
        p = OUT / f"{velho}.png"
        if p.exists():
            p.unlink()


if __name__ == "__main__":
    camara(); senado(); governos(); senado_por_uf()
    grafico_grupos_camara()
    grafico_escada("23_camara_limiares_2026", "Câmara 2026", "e2_camara_limiares_2026.csv",
                   [("CPI", 171), ("bloqueia PEC", 206), ("maioria\nabsoluta", 257), ("PEC", 308), ("autoriza\nimpeachment", 342)], 513,
                   "Fonte: TSE; Constituição, arts. 51, 58, 60 e 69. Campo não é bloco de votação: é o teto de cada grupo votando unido.")
    grafico_escada("24_senado_limiares_2027", "Senado a partir de 2027", "e3_senado_limiares_2027.csv",
                   [("CPI", 27), ("bloqueia\nPEC", 33), ("maioria\nabsoluta", 41), ("PEC", 49), ("condena no\nimpeachment", 54)], 81,
                   "Fonte: TSE e Senado; Constituição, arts. 52, 58 e 60. Campo não é bloco de votação: é o teto de cada grupo votando unido.")
    grafico_pl(); nomes_trailer(); borrar()
    print("ok animacao")
