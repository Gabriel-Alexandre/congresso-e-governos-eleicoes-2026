"""Graficos 1920x1080 para o video e para o relatorio. Todo numero vem de resultados/*.csv e RESUMO.json.

Cada grafico diz a unidade, a regua de campo (R1) quando houver, e a fonte. Saida: resultados/figuras/video/*.png
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso.comum import RAIZ, RES  # noqa: E402

OUT = RES / "figuras" / "video"
OUT.mkdir(parents=True, exist_ok=True)
R = json.loads((RES / "RESUMO.json").read_text(encoding="utf-8"))
FONTE = "Fonte: TSE (resultado oficial e dados abertos, 07/out/2026). Campos pela escala de especialistas (R1, Bolognesi et al., Dados 2023)."
COR = {"esquerda": "#C0392B", "centro": "#8E8E93", "direita": "#1F4E9C", "sem classificacao": "#D0D0D0", "pl": "#0B2C6B"}
plt.rcParams.update({"font.size": 22, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 34, "axes.titleweight": "bold", "figure.facecolor": "white"})


def novo(titulo, sub=None):
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.85, bottom=0.12)
    fig.suptitle(titulo, x=0.08, y=0.97, ha="left", fontsize=30, fontweight="bold")
    if sub:
        fig.text(0.08, 0.89, sub, fontsize=21, color="#444")
    return fig, ax


def fecha(fig, nome, nota=FONTE):
    fig.text(0.08, 0.012, textwrap.fill(nota, 175), fontsize=14, color="#555", va="bottom")
    fig.savefig(OUT / f"{nome}.png")
    plt.close(fig)


def g01_camara_campos():
    t = pd.read_csv(RES / "a1_campo_r1.csv").query("cortes=='4.0-6.0'")
    fig, ax = novo("Câmara: o campo de direita (R1) quase não mudou de tamanho", "Cadeiras por campo, de 513 (escala de especialistas; centro = notas 4 a 6)")
    anos = [2018, 2022, 2026]
    base = np.zeros(3)
    for k in ("esquerda", "centro", "direita", "sem classificacao"):
        v = np.array([t[(t.ano == a) & (t.campo == k)].cadeiras.iloc[0] for a in anos])
        ax.bar([str(a) for a in anos], v, bottom=base, color=COR[k], width=0.55, label=k)
        for i, x in enumerate(v):
            if x > 15:
                ax.text(i, base[i] + x / 2, str(x), ha="center", va="center", color="white", fontsize=26, fontweight="bold")
        base += v
    ax.set_ylabel("cadeiras"); ax.set_ylim(0, 580); ax.legend(frameon=False, fontsize=20, loc="upper left", ncol=4)
    fecha(fig, "01_camara_cadeiras_por_campo_r1")


def g02_ganhos_perdas():
    t = pd.read_csv(RES / "a1_bancada_vespera_vs_eleita.csv").sort_values("var_vs_2022")
    t = t[t.eleita_2026 > 0]  # fora os extintos ou fundidos (PSC, PTB, Patriota, PROS), que não são derrota
    t = pd.concat([t.head(7), t.tail(8)]).drop_duplicates("sig")
    fig, ax = novo("Câmara: o PL cresceu; União, PDT, PP e MDB encolheram", "Variação de cadeiras, eleição de 2026 menos eleição de 2022, por partido existente nas duas eleições")
    fig.subplots_adjust(left=0.16)
    cores = [COR["pl"] if s == "PL" else ("#2E7D32" if v > 0 else "#B23B3B") for s, v in zip(t.sig, t.var_vs_2022)]
    ax.barh(t.sig, t.var_vs_2022, color=cores)
    for i, v in enumerate(t.var_vs_2022):
        ax.text(v + (0.5 if v >= 0 else -0.5), i, f"{v:+d}", va="center", ha="left" if v >= 0 else "right", fontsize=22, fontweight="bold")
    ax.axvline(0, color="#333", lw=1.2); ax.set_xlabel("cadeiras a mais ou a menos"); ax.set_xlim(t.var_vs_2022.min() - 4, t.var_vs_2022.max() + 4)
    fecha(fig, "02_camara_ganhos_e_perdas_por_partido", FONTE + " Partidos extintos ou fundidos (PSC, PTB, Patriota, PROS, DEM, PSL) ficam de fora. Soma de cadeiras por partido, não por federação.")


def g03_origem():
    t = pd.read_csv(RES / "a1_origem_das_cadeiras_2026.csv").set_index("sig")
    cols = [c for c in t.columns]
    t["tot"] = t.sum(axis=1)
    t = t.sort_values("tot", ascending=False).head(9)
    reeleito = t[[c for c in cols if c.startswith("reeleito") or c.startswith("ex-titular")]].sum(axis=1)
    novo_ = t[[c for c in cols if c.startswith("entrante")]].sum(axis=1)
    fig, ax = novo("As cadeiras de 2026: quem voltou e quem entrou", "Origem das cadeiras de cada partido na Câmara eleita em 2026")
    fig.subplots_adjust(left=0.17)
    ax.barh(t.index[::-1], reeleito[::-1], color="#5B7DB1", label="já era deputado (vespera ou eleito em 2022)")
    ax.barh(t.index[::-1], novo_[::-1], left=reeleito[::-1], color="#F2A93B", label="entrou: não estava na Câmara na véspera")
    for i, (a, b) in enumerate(zip(reeleito[::-1], novo_[::-1])):
        ax.text(a / 2, i, str(int(a)), ha="center", va="center", color="white", fontsize=22, fontweight="bold")
        ax.text(a + b / 2, i, str(int(b)), ha="center", va="center", color="black", fontsize=22, fontweight="bold")
    ax.legend(frameon=False, fontsize=19, loc="lower right"); ax.set_xlabel("cadeiras")
    fecha(fig, "03_camara_origem_das_cadeiras", FONTE + " Ligação por nome civil e data de nascimento (candidatura × deputados.csv da Câmara).")


def g04_votos_cadeiras():
    t = pd.read_csv(RES / "d6_votos_x_cadeiras_por_campo.csv")
    t = t[t.campo.isin(["esquerda", "direita"])]
    fig, ax = novo("Votos e cadeiras: o bônus da direita em cadeiras cresceu", "Cadeiras (%) menos votos (%) por campo, pontos percentuais, Câmara")
    w = 0.35
    anos = [2018, 2022, 2026]
    for j, k in enumerate(("esquerda", "direita")):
        v = [t[(t.ano == a) & (t.campo == k)].cadeiras_menos_votos_pp.iloc[0] for a in anos]
        b = ax.bar(np.arange(3) + (j - 0.5) * w, v, w, color=COR[k], label=k)
        for x, y in zip(np.arange(3) + (j - 0.5) * w, v):
            ax.text(x, y + (0.1 if y >= 0 else -0.25), f"{y:+.1f}", ha="center", fontsize=22, fontweight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels([str(a) for a in anos]); ax.axhline(0, color="#333"); ax.legend(frameon=False, fontsize=20)
    fecha(fig, "04_camara_bonus_de_cadeiras_por_campo")


def g05_puxadores():
    t = pd.read_csv(RES / "a5_puxadores.csv").query("ano==2026").head(8).iloc[::-1]
    fig, ax = novo("Puxadores: cadeiras que a lista perderia sem o candidato", "Cadeiras da lista com o candidato menos sem ele (a dele inclusive), eleição de 2026")
    fig.subplots_adjust(left=0.27)
    nomes = [f"{n.title()} ({p}-{u})" for n, p, u in zip(t.candidato, t.partido, t.uf)]
    ax.barh(nomes, t.cadeiras_a_mais_pelo_candidato, color="#F2A93B")
    for i, (v, vv) in enumerate(zip(t.cadeiras_a_mais_pelo_candidato, t.votos)):
        ax.text(v + 0.1, i, f"{int(v)}  ({vv/1e6:.2f} mi de votos)", va="center", fontsize=21)
    ax.set_xlabel("cadeiras"); ax.set_xlim(0, t.cadeiras_a_mais_pelo_candidato.max() * 1.45)
    fecha(fig, "05_puxadores_cadeiras_garantidas", FONTE + " Redistribuição refeita com a regra que reproduz as 513 cadeiras.")


def g06_senado():
    comp = pd.read_csv(RES / "a2_composicao_fev2027.csv")
    ct = comp.groupby("sig").size().sort_values(ascending=False)
    fig, ax = novo("Senado a partir de fev/2027: 81 cadeiras", "Eleitos em 2026 (54) mais senadores com mandato até 2031 (27, partido atual na API do Senado)")
    cores = [COR["pl"] if s == "PL" else "#7A8CB8" for s in ct.index]
    ax.bar(ct.index, ct.values, color=cores)
    for i, v in enumerate(ct.values):
        ax.text(i, v + 0.3, str(v), ha="center", fontsize=22, fontweight="bold")
    plt.xticks(rotation=45, ha="right"); fig.subplots_adjust(bottom=0.27)
    ax.set_ylabel("senadores")
    fecha(fig, "06_senado_composicao_2027", FONTE + " Limiares: 41 (maioria absoluta), 49 (3/5) e 54 (2/3). Campos não equivalem a bloco de votação.")


def g07_governos():
    g = pd.read_csv(RES / "a3_governos.csv")
    g = g[g.ano == 2026]
    fig, ax = novo("Governos: 20 estados decididos e 7 em segundo turno", "Governadores eleitos no 1º turno de 2026, por partido; 7 estados vão a 2º turno em 25/out")
    dec = g[g.situacao != "2o turno em disputa"].groupby("partido").size().sort_values(ascending=False)
    cores = [COR["pl"] if s == "PL" else "#7A8CB8" for s in dec.index]
    ax.bar(dec.index, dec.values, color=cores)
    for i, v in enumerate(dec.values):
        ax.text(i, v + 0.05, str(v), ha="center", fontsize=22, fontweight="bold")
    plt.xticks(rotation=40, ha="right")
    ax.text(0.98, 0.9, "em disputa no 2º turno:\n" + ", ".join(g[g.situacao == "2o turno em disputa"].uf), transform=ax.transAxes, ha="right", fontsize=20, color="#444")
    ax.set_ylabel("governadores"); fig.subplots_adjust(bottom=0.25)
    fecha(fig, "07_governos_por_partido_2026")


def mapa(df, col, titulo, sub, nome, cmap="RdBu", vmax=10, rotulo="pontos percentuais"):
    gj = json.loads((RAIZ / "dados/brutos/ibge/malha_municipios_minima.json").read_text(encoding="utf-8"))
    val = dict(zip(df.ibge.astype(str), df[col]))
    patches, vals = [], []
    for f in gj["features"]:
        cod = f["properties"]["codarea"]
        if cod not in val:
            continue
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for p in polys:
            patches.append(Polygon(np.array(p[0]), closed=True)); vals.append(val[cod])
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    ax = fig.add_axes([0.20, 0.07, 0.55, 0.80])
    ax.set_anchor("C")
    fig.suptitle(titulo, x=0.03, y=0.98, ha="left", fontsize=34, fontweight="bold")
    fig.text(0.03, 0.915, sub, fontsize=21, color="#444")
    pc = PatchCollection(patches, cmap=cmap, linewidths=0)
    pc.set_array(np.clip(np.array(vals), -vmax, vmax)); pc.set_clim(-vmax, vmax)
    ax.add_collection(pc); ax.set_xlim(-74.5, -34); ax.set_ylim(-34, 5.5); ax.set_aspect("equal"); ax.axis("off")
    cax = fig.add_axes([0.78, 0.25, 0.015, 0.45]); cb = fig.colorbar(pc, cax=cax); cb.set_label(rotulo + " (azul = mais voto de direita)", fontsize=18); cb.ax.tick_params(labelsize=18)
    fecha(fig, nome, "Fonte: TSE e IBGE (malha). R1: escala de especialistas. Cor limitada a ±" + str(vmax) + " pp; municípios pequenos oscilam muito.")


def g08_mapa():
    s = pd.read_csv(RES / "b1_swing_municipal_deputado_federal.csv")
    mapa(s, "swing_dir", "Onde o voto de direita (R1) subiu e desceu", "Deputado federal, variação de 2022 para 2026 na % de votos válidos de partidos de direita, por município", "08_mapa_variacao_voto_direita_deputado_federal")


def g09_perfil():
    t = pd.DataFrame(R["b2"]["perfil_x_swing"]).query("cargo=='deputado federal'")
    nomes = {"pct_urbana": "% urbana", "pct_pretos_pardos": "% pretos e pardos", "pct_60mais": "% com 60 anos ou mais", "pct_superior": "% com superior completo", "pct_evangelicos": "% evangélicos", "pct_catolicos": "% católicos", "log_pib_pc": "PIB per capita (log)", "agro_share": "% agropecuária no valor adicionado", "bf_por_100hab": "Bolsa Família por 100 hab."}
    t = t.iloc[::-1]
    fig, ax = novo("O perfil do município quase não explica a variação do voto", "Efeito em 2026 menos o de 2018→2022 (pp por desvio-padrão, IC 95%). A UF sozinha explica 20% da variação; o perfil soma só 1,4 ponto")
    fig.subplots_adjust(left=0.31)
    y = np.arange(len(t))
    ax.errorbar(t.coef_2026_menos_placebo_pp, y, xerr=[t.coef_2026_menos_placebo_pp - t.ic95_diferenca_baixo, t.ic95_diferenca_alto - t.coef_2026_menos_placebo_pp], fmt="o", color="#1F4E9C", ecolor="#7A8CB8", capsize=6, ms=11, lw=2.5)
    ax.set_yticks(y); ax.set_yticklabels([nomes[v] for v in t.variavel]); ax.axvline(0, color="#333")
    ax.set_xlabel("pp por desvio-padrão (positivo = mais voto de direita em 2026 que no padrão anterior)")
    fecha(fig, "09_perfil_do_municipio_x_variacao", FONTE + " Relação entre municípios, não entre pessoas (falácia ecológica).")


def g10_pesquisas():
    t = pd.read_csv(RES / "c2_erro_por_pesquisa.csv").sort_values("erro_vencedor_pp")
    fig, ax = novo("Pesquisas: o primeiro colocado teve mais voto do que a pesquisa mostrou", "Erro no % do primeiro colocado (pesquisa menos urna, % oficial do TSE), pontos, 32 pesquisas de Datafolha e Quaest da véspera")
    cores = ["#1F4E9C" if i == "Quaest" else "#C0392B" for i in t.instituto]
    ax.barh([f"{u} {i[:1]}" for u, i in zip(t.uf, t.instituto)], t.erro_vencedor_pp, color=cores)
    ax.axvline(0, color="#333")
    ax.set_xlabel("pontos percentuais (negativo = pesquisa abaixo da urna)")
    ax.tick_params(axis="y", labelsize=13)
    ax.text(0.02, 0.95, "azul: Quaest (Q)   vermelho: Datafolha (D)", transform=ax.transAxes, fontsize=19)
    fecha(fig, "10_pesquisas_erro_no_vencedor", "Fonte: pesquisas em O Povo (04/out/2026); urnas: TSE. Resultado das pesquisas com fonte única de compilação (conferido em SP com a Gazeta do Povo).")


def g11_reeleicao():
    t = pd.read_csv(RES / "d5_reeleicao_deputados.csv").query("campo_r1_na_eleicao_anterior in ['todos','esquerda','centro','direita']")
    fig, ax = novo("Deputados que tentaram de novo: a taxa de reeleição subiu", "% reeleitos entre os eleitos da eleição anterior, por campo (R1) do partido na eleição anterior")
    ks = ["todos", "esquerda", "centro", "direita"]
    w = 0.38
    for j, (a0, a1) in enumerate(((2018, 2022), (2022, 2026))):
        v = [t[(t.de == a0) & (t.campo_r1_na_eleicao_anterior == k)].pct_reeleito_entre_todos.iloc[0] for k in ks]
        ax.bar(np.arange(4) + (j - 0.5) * w, v, w, label=f"{a0}→{a1}", color=["#9AA5B1", "#1F4E9C"][j])
        for x, y in zip(np.arange(4) + (j - 0.5) * w, v):
            ax.text(x, y + 1, f"{y:.0f}%", ha="center", fontsize=21, fontweight="bold")
    ax.set_xticks(range(4)); ax.set_xticklabels(ks); ax.legend(frameon=False, fontsize=20); ax.set_ylim(0, 85)
    fecha(fig, "11_reeleicao_de_deputados_por_campo")


def g12_arrasto():
    t = pd.DataFrame(R["b4"]["arrasto"])
    fig, ax = novo("Voto em Bolsonaro para presidente × voto de direita nos outros cargos", "Correlação entre municípios (não é causa), média por UF ponderada pelo eleitorado")
    cargos = ["deputado federal", "governador", "senador"]
    w = 0.26
    for j, a in enumerate((2018, 2022, 2026)):
        v = [t[(t.ano == a) & (t.cargo == c)].correlacao_media_ponderada_por_uf.tolist() for c in cargos]
        v = [x[0] if x else np.nan for x in v]
        ax.bar(np.arange(3) + (j - 1) * w, v, w, label=str(a), color=["#B8C2D1", "#7A8CB8", "#1F4E9C"][j])
        for x, y in zip(np.arange(3) + (j - 1) * w, v):
            if not np.isnan(y):
                ax.text(x, y + 0.01, f"{y:.2f}", ha="center", fontsize=20, fontweight="bold")
    ax.set_xticks(range(3)); ax.set_xticklabels(cargos); ax.legend(frameon=False, fontsize=20)
    fecha(fig, "12_arrasto_presidenciavel", "Fonte: TSE. Presidente: Jair Bolsonaro (PSL) em 2018 e (PL) em 2022, Flávio Bolsonaro (PL) em 2026. Senado 2022 não entra (1 vaga por UF).")


def g13_abstencao():
    t = pd.DataFrame(R["b3"]["abstencao_nacional"])
    fig, ax = novo("Abstenção: estável entre 2022 e 2026", "% de eleitores aptos que não compareceram, eleição para deputado federal")
    ax.plot(t.ano, t.abstencao_pct, marker="o", color="#1F4E9C", lw=4, ms=14)
    for x, y in zip(t.ano, t.abstencao_pct):
        ax.text(x, y + 0.4, f"{y:.1f}%", ha="center", fontsize=22, fontweight="bold")
    cf = R["b3"]["contrafactual_comparecimento_2022"]
    ax.text(0.02, 0.9, f"Com o comparecimento de 2022, o voto de direita seria {cf['direita_pct_com_comparecimento_de_2022']:.2f}% (real: {cf['direita_pct_real_2026']:.2f}%).", transform=ax.transAxes, fontsize=21)
    ax.set_ylim(14, 24); ax.set_xticks(t.ano)
    fecha(fig, "13_abstencao_nacional")


def g14_placar():
    p = json.loads((RES / "placar_hipoteses.json").read_text(encoding="utf-8")) if (RES / "placar_hipoteses.json").exists() else None
    if not p:
        return
    fig, ax = novo("Placar das hipóteses", "Cada explicação disse antes o que o dado mostraria (a H9 entrou depois). Opinião da IA")
    ax.axis("off")
    cores = {"consistente": "#2E7D32", "inconsistente": "#B23B3B", "não testável": "#8E8E93", "parcial": "#C98A00"}
    y = 0.92
    for h in p:
        ax.text(0.0, y, h["id"], fontsize=24, fontweight="bold", va="center", transform=ax.transAxes)
        ax.text(0.05, y, h["nome"], fontsize=22, va="center", transform=ax.transAxes)
        ax.text(0.66, y, h["status"], fontsize=22, fontweight="bold", color=cores.get(h["status"], "#333"), va="center", transform=ax.transAxes)
        ax.text(0.84, y, f"confiança {h['confianca']}", fontsize=19, color="#444", va="center", transform=ax.transAxes)
        ax.text(0.05, y - 0.04, h["onde"], fontsize=16, color="#555", va="center", transform=ax.transAxes)
        y -= 0.115
    fecha(fig, "14_placar_das_hipoteses", "Leitura da IA, marcada como opinião. Detalhe em docs/LEITURA_DA_IA.md.")


if __name__ == "__main__":
    for f in (g01_camara_campos, g02_ganhos_perdas, g03_origem, g04_votos_cadeiras, g05_puxadores, g06_senado, g07_governos, g08_mapa, g09_perfil, g10_pesquisas, g11_reeleicao, g12_arrasto, g13_abstencao, g14_placar):
        f()
        print(f.__name__, "ok", flush=True)
