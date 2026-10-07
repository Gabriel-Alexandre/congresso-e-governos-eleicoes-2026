"""Dados e quadros de referência para as animações do vídeo (cadeiras da Câmara e do Senado, mapas dos estados).

Tudo sai das tabelas que as análises 2 e 3 já gravaram. A edição usa o JSON (ordem das cadeiras, partido, campo, cor);
os PNG são o quadro final de referência de cada animação.
Saídas: resultados/animacao/*.json e resultados/figuras/video/15 a 20 + versões borradas para o trailer.
"""
from __future__ import annotations

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

OUT = RES / "figuras" / "video"
ANI = RES / "animacao"
ANI.mkdir(parents=True, exist_ok=True)
R = json.loads((RES / "RESUMO.json").read_text(encoding="utf-8"))
PESOS = R["a1"]["pesos_fusoes"]
FONTE = "Fonte: TSE e Senado (07/out/2026). Cor pelo campo do partido na escala de especialistas (R1): vermelho esquerda, cinza centro, azul direita; PL em azul-escuro."
plt.rcParams.update({"font.size": 22, "figure.facecolor": "white"})

# tons por campo: cada partido ganha um tom dentro da cor do campo, do mais forte ao mais claro
TONS = {
    "esquerda": ["#B71C1C", "#D32F2F", "#E53935", "#EF5350", "#E57373", "#EF9A9A", "#FFCDD2"],
    "centro": ["#616161", "#757575", "#9E9E9E", "#BDBDBD", "#D5D5D5"],
    "direita": ["#1E88E5", "#64B5F6", "#0097A7", "#4FC3F7", "#26A69A", "#90CAF9", "#4DD0E1", "#80CBC4", "#81D4FA", "#B3E5FC", "#5C9BD5", "#A7C7E7"],
    "sem classificacao": ["#CFCFCF"],
}
PL_COR = "#0B2C6B"


def nota(p):
    return campos.nota_r1(p, PESOS)


def paleta(partidos):
    """partido -> cor, ordenados pela nota R1 (esquerda à direita)."""
    cor, usados = {}, {k: 0 for k in TONS}
    for p in sorted(partidos, key=lambda x: (nota(x) if nota(x) is not None else 99, x)):
        if campos.sigla(p) == "PL":
            cor[p] = PL_COR
            continue
        c = campos.campo_r1(nota(p))
        lista = TONS[c]
        cor[p] = lista[usados[c] % len(lista)]
        usados[c] += 1
    return cor


def hemiciclo(n, linhas=None):
    """Coordenadas de n assentos num semicírculo (fileiras concêntricas), da esquerda para a direita."""
    linhas = linhas or max(4, int(round(math.sqrt(n / 2.2))))
    raios = np.linspace(1.0, 2.2, linhas)
    comp = raios / raios.sum()
    por = np.floor(comp * n).astype(int)
    por[-1] += n - por.sum()
    pts = []
    for r, k in zip(raios, por):
        ang = np.linspace(math.pi, 0, k)
        pts += [(r * math.cos(a), r * math.sin(a), a) for a in ang]
    pts.sort(key=lambda t: (-t[2], t[0]))  # da esquerda (ângulo pi) para a direita (0)
    return [(x, y) for x, y, _ in pts]


def desenhar_hemiciclo(assentos, titulo, sub, nome, total_txt, legenda):
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
    fig.text(0.05, 0.02, FONTE, fontsize=14, color="#555")
    fig.savefig(OUT / f"{nome}.png")
    plt.close(fig)


def camara():
    cad = pd.read_csv(RES / "a1_cadeiras_por_partido_e_ano.csv").set_index("sig")
    saida = {}
    todos = sorted(set(cad.index[cad["2022"] > 0]) | set(cad.index[cad["2026"] > 0]))
    cor = paleta(todos)  # a mesma cor para o mesmo partido nos dois anos, para a transição da animação
    for ano in ("2022", "2026"):
        c = cad[ano][cad[ano] > 0]
        ordem = sorted(c.index, key=lambda p: (nota(p) if nota(p) is not None else 99, p))
        assentos = []
        for p in ordem:
            for _ in range(int(c[p])):
                assentos.append({"partido": p, "campo": campos.campo_r1(nota(p)), "nota_r1": nota(p), "cor": cor[p]})
        saida[ano] = {"total": len(assentos), "ordem_dos_partidos": [{"partido": p, "cadeiras": int(c[p]), "campo": campos.campo_r1(nota(p)), "cor": cor[p]} for p in ordem], "assentos": assentos}
        lg = [(f"{p} {int(c[p])}", cor[p]) for p in sorted(c.index, key=lambda x: -c[x])[:9]]
        camp = pd.Series([a["campo"] for a in assentos]).value_counts()
        desenhar_hemiciclo(assentos, f"Câmara eleita em {ano}: {len(assentos)} cadeiras", f"Esquerda {camp.get('esquerda', 0)} · centro {camp.get('centro', 0)} · direita {camp.get('direita', 0)} (escala de especialistas)", f"{15 if ano == '2022' else 16}_camara_cadeiras_{ano}", f"PL {int(c.get('PL', 0))}", lg)
    (ANI / "camara_2022_2026.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")


def senado():
    comp = pd.read_csv(RES / "a2_composicao_fev2027.csv")
    comp["sig"] = comp["sig"].fillna("S/PARTIDO")
    cor = paleta(list(comp.sig.unique()))
    comp["nota"] = comp.sig.map(nota)
    comp = comp.sort_values(["nota", "sig"], na_position="last")
    assentos = [{"partido": r.sig, "uf": r.uf, "nome": r.nome, "origem": r.origem, "campo": campos.campo_r1(nota(r.sig)), "cor": cor[r.sig]} for r in comp.itertuples()]
    (ANI / "senado_2027.json").write_text(json.dumps({"total": len(assentos), "limiares": {"maioria_absoluta": 41, "tres_quintos": 49, "dois_tercos": 54}, "assentos": assentos}, ensure_ascii=False, indent=1), encoding="utf-8")
    ct = comp.sig.value_counts()
    lg = [(f"{p} {int(ct[p])}", cor[p]) for p in ct.index[:9]]
    camp = comp.nota.map(lambda n: campos.campo_r1(n)).value_counts()
    desenhar_hemiciclo(assentos, "Senado a partir de fevereiro de 2027: 81 cadeiras", f"54 eleitos em 2026 e 27 com mandato até 2031 · esquerda {camp.get('esquerda', 0)} · centro {camp.get('centro', 0)} · direita {camp.get('direita', 0)}", "17_senado_cadeiras_2027", f"PL {int(ct.get('PL', 0))}", lg)


def mapa_ufs(cores_uf, titulo, sub, nome, legenda, rotulos=None):
    gj = json.loads((RAIZ / "dados/brutos/ibge/malha_ufs_minima.json").read_text(encoding="utf-8"))
    cod = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    ax = fig.add_axes([0.08, 0.08, 0.6, 0.78])
    fig.suptitle(titulo, x=0.04, y=0.97, ha="left", fontsize=30, fontweight="bold")
    fig.text(0.04, 0.91, sub, fontsize=20, color="#444")
    for f in gj["features"]:
        uf = cod[f["properties"]["codarea"]]
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for p in polys:
            arr = np.array(p[0])
            ax.add_patch(Polygon(arr, closed=True, facecolor=cores_uf.get(uf, "#EEEEEE"), edgecolor="white", linewidth=1.2))
        if rotulos:
            arr = np.vstack([np.array(p[0]) for p in polys])
            cx, cy = arr[:, 0].mean(), arr[:, 1].mean()
            # rótulos que colidem com o vizinho saem do lugar (DF dentro de GO; RJ, ES e SE pequenos)
            dx, dy = {"DF": (1.6, 0.9), "GO": (-1.2, -0.6), "RJ": (1.4, -0.9), "ES": (1.2, 0.0), "SE": (0.9, -0.4), "AL": (1.0, 0.0)}.get(uf, (0, 0))
            fora = uf in ("DF", "RJ", "ES", "SE", "AL")
            if (dx, dy) != (0, 0):
                cx, cy = cx + dx, cy + dy
            ax.text(cx, cy, rotulos.get(uf, uf), ha="center", va="center", fontsize=13, color="#222" if fora else ("white" if cores_uf.get(uf) in (PL_COR, "#3F6CB5", "#D32F2F", "#1E88E5") else "#222"), fontweight="bold")
    ax.set_xlim(-74.5, -34); ax.set_ylim(-34, 5.5); ax.set_aspect("equal"); ax.axis("off")
    y = 0.75
    for rot, cor in legenda:
        fig.text(0.68, y, "■", color=cor, fontsize=34, va="center")
        fig.text(0.705, y, rot, fontsize=18, va="center")
        y -= 0.06
    fig.text(0.04, 0.02, "Fonte: TSE (07/out/2026) e IBGE (malha). Campo pela escala de especialistas (R1).", fontsize=14, color="#555")
    fig.savefig(OUT / f"{nome}.png")
    plt.close(fig)


def governos():
    g = pd.read_csv(RES / "a3_governos.csv")
    cor_campo = {"esquerda": "#D32F2F", "centro": "#9E9E9E", "direita": "#1E88E5"}
    dados = {}
    for ano in (2022, 2026):
        x = g[g.ano == ano]
        cores, rot, lista = {}, {}, []
        for r in x.itertuples():
            if r.situacao == "2o turno em disputa":
                cores[r.uf] = "#D5D5D5"
                lista.append({"uf": r.uf, "situacao": "2o turno", "finalistas": r.finalistas})
            else:
                c = PL_COR if campos.sigla(r.partido) == "PL" else cor_campo.get(r.campo_r1, "#EEEEEE")
                cores[r.uf] = c
                lista.append({"uf": r.uf, "situacao": r.situacao, "governador": r.nome, "partido": r.partido, "campo": r.campo_r1, "cor": c})
            rot[r.uf] = r.uf
        dados[str(ano)] = lista
        ct = x[x.situacao != "2o turno em disputa"].campo_r1.value_counts()
        npl = int((x.partido == "PL").sum())
        leg = [("PL", PL_COR), ("outros de direita", "#1E88E5"), ("centro", "#9E9E9E"), ("esquerda", "#D32F2F")] + ([("2º turno em 25/out", "#D5D5D5")] if ano == 2026 else [])
        sub = f"{int((x.situacao != '2o turno em disputa').sum())} decididos: direita {ct.get('direita', 0)} (PL {npl}), centro {ct.get('centro', 0)}, esquerda {ct.get('esquerda', 0)}" + (f" · {int((x.situacao == '2o turno em disputa').sum())} em 2º turno" if ano == 2026 else "")
        mapa_ufs(cores, f"Governos estaduais, {ano}" + (" (1º turno)" if ano == 2026 else ""), sub, f"{18 if ano == 2022 else 19}_mapa_governos_{ano}", leg, rot)
    (ANI / "governos_2022_2026.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


def senado_por_uf():
    e = pd.read_csv(RES / "a2_composicao_fev2027.csv")
    e = e[e.origem == "eleito em 2026"]
    cores, rot, dados = {}, {}, {}
    for uf, x in e.groupby("uf"):
        npl = int((x.sig == "PL").sum())
        camp = [campos.campo_r1(nota(s)) for s in x.sig]
        ndir = sum(k == "direita" for k in camp)
        if npl == 2:
            c = PL_COR
        elif npl == 1 and ndir == 2:
            c = "#3F6CB5"
        elif ndir == 2:
            c = "#90CAF9"
        elif ndir == 1:
            c = "#B39DDB"
        else:
            c = "#E57373"
        cores[uf] = c
        rot[uf] = uf
        dados[uf] = [{"nome": r.nome, "partido": r.sig, "campo": campos.campo_r1(nota(r.sig))} for r in x.itertuples()]
    (ANI / "senado_eleitos_por_uf_2026.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    leg = [("2 do PL", PL_COR), ("1 do PL e 1 de outro de direita", "#3F6CB5"), ("2 de direita, sem PL", "#90CAF9"), ("1 de direita e 1 de esquerda ou centro", "#B39DDB"), ("nenhum de direita", "#E57373")]
    mapa_ufs(cores, "Senado, 2026: quem levou as duas vagas de cada estado", f"PL {int((e.sig == 'PL').sum())} das 54 vagas", "20_mapa_senado_2026", leg, rot)


def borrar():
    for n in ("01_camara_cadeiras_por_campo_r1", "02_camara_ganhos_e_perdas_por_partido", "05_puxadores_cadeiras_garantidas", "10_pesquisas_erro_no_vencedor", "16_camara_cadeiras_2026", "19_mapa_governos_2026"):
        im = Image.open(OUT / f"{n}.png").convert("RGB").filter(ImageFilter.GaussianBlur(18))
        im.save(OUT / f"{n}_borrado.png")


if __name__ == "__main__":
    camara(); senado(); governos(); senado_por_uf(); borrar()
    print("ok animacao")
