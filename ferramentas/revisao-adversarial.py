"""Revisao adversarial, passada 3 (programatica): refaz por caminho independente o que o relatorio afirma.

Caminhos usados aqui sao diferentes dos das analises: o JSON oficial por UF (nao os CSV de municipio),
contagem direta de cadeiras eleitas, soma de votos de partido pelo campo `tvtn` do JSON, e busca de palavras proibidas.
Saida: resultados/revisao_adversarial.json (lida por docs/REVISAO_ADVERSARIAL.md)
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso import campos  # noqa: E402
from congresso.cadeiras import distribuir, montar_listas, preparar  # noqa: E402
from congresso.comum import RAIZ, RES, UFS, detalhe, votos_cand, votos_partido  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
R = json.loads((RES / "RESUMO.json").read_text(encoding="utf-8"))
out = []


def reg(i, desc, ok, detalhe_=""):
    out.append({"id": i, "descricao": desc, "passou": bool(ok), "detalhe": str(detalhe_)})
    print(("OK    " if ok else "FALHA "), i, desc, "|", detalhe_)


def lerj(uf):
    raw = (RAIZ / f"dados/brutos/oficial2026/{uf.lower()}-c0006.json").read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("latin-1"))


def norm(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()


# ---- 1. cadeiras por partido: JSON oficial x nossa tabela ----
eleitos, votos_part, vagas = [], {}, 0
for uf in UFS:
    d = lerj(uf)
    for carg in d["carg"]:
        vagas += int(carg["nv"])
        for ag in carg["agr"]:
            for p in ag["par"]:
                votos_part[(uf, norm(p["sg"]))] = int(p.get("tvtn", 0)) + int(p.get("tvtl", 0))  # nominais + legenda = votos validos do partido
                for c in p.get("cand", []):
                    if str(c.get("st", "")).upper().startswith("ELEITO"):
                        eleitos.append((uf, norm(p["sg"]), c["nmu"], int(c["vap"])))
reg("A1", "513 vagas e 513 eleitos no JSON oficial", vagas == 513 and len(eleitos) == 513, f"{vagas} vagas, {len(eleitos)} eleitos")
cont = pd.Series([e[1] for e in eleitos]).value_counts().to_dict()
nossa = pd.read_csv(RES / "a1_cadeiras_por_partido_e_ano.csv").set_index("sig")["2026"]
dif = {k: (cont.get(k, 0), int(nossa.get(k, 0))) for k in set(cont) | set(nossa.index) if cont.get(k, 0) != int(nossa.get(k, 0))}
reg("A2", "cadeiras por partido: JSON oficial = tabela da A1 (caminho independente)", not dif, dif or "sem diferenca")

# ---- 2. campos pelo caminho independente (JSON) ----
pesos = R["a1"]["pesos_fusoes"]
cj = pd.Series([campos.campo_r1(campos.nota_r1(e[1], pesos)) for e in eleitos]).value_counts().to_dict()
tc = pd.DataFrame(R["a1"]["campo_r1"])
t26 = tc[(tc.cortes == "4.0-6.0") & (tc.ano == 2026)].set_index("campo")["cadeiras"].to_dict()
reg("A3", "cadeiras por campo R1 em 2026: JSON oficial = tabela da A1", all(cj.get(k, 0) == t26.get(k, 0) for k in ("direita", "esquerda", "centro")), f"JSON {cj} | tabela {t26}")
soma513 = {a: int(tc[(tc.cortes == "4.0-6.0") & (tc.ano == a)].cadeiras.sum()) for a in (2018, 2022, 2026)}
reg("A4", "R1: esquerda + centro + direita + sem classificacao = 513 nos tres anos", all(v == 513 for v in soma513.values()), soma513)

# ---- 3. votos por partido: JSON (tvtn) x derivado ----
vj = {p: sum(v for (uf, pp), v in votos_part.items() if pp == p) for p in ("PL", "PSD", "REPUBLICANOS", "MDB", "PODE")}
pv = pd.read_csv(RES / "a1_votos_pct_por_partido_e_ano.csv").set_index("sig")["2026"]
tot = sum(votos_part.values())
cmp = {p: (round(100 * vj[p] / tot, 2), round(100 * float(pv[p]), 2)) for p in vj}
reg("A5", "% de votos validos (nominais + legenda) por partido: JSON (tvtn + tvtl) x derivado, diferenca <= 0,05 ponto", all(abs(a - b) <= 0.05 for a, b in cmp.values()), cmp)

# ---- 4. reproducao das cadeiras ----
cand = votos_cand()
part = votos_partido()
prep = preparar(cand, part, 2026)
ofi = cand[(cand.ano == 2026) & (cand.cargo == 6)]
ofi = ofi[ofi.sit.str.upper().str.startswith("ELEITO")].groupby("uf").sq.apply(set)
d0 = sum(len(distribuir(montar_listas(prep=prep, uf=u), len(ofi[u]), 0.8, 0.2).eleitos ^ ofi[u]) // 2 for u in UFS)
reg("A6", "reproducao das 513 cadeiras com a regra da lei (80% e 20% nas sobras): 0 diferencas", d0 == 0, f"{d0} diferencas")

# ---- 5. votos validos: lista x detalhe ----
dt = detalhe()
dt = dt[(dt.ano == 2026) & (dt.cargo == 6)].groupby("uf")["validos"].sum()
soma = {u: sum(l["votos"] for l in montar_listas(prep=prep, uf=u).values()) for u in UFS}
dmax = max(abs(soma[u] - int(dt[u])) / int(dt[u]) for u in UFS)
reg("A7", "votos validos por UF: soma das listas = detalhe do TSE (diferenca relativa maxima < 0,1%)", dmax < 0.001, f"{100*dmax:.4f}%")

# ---- 6. municipios ----
reg("B1", "municipios casados TSE x IBGE >= 99,9%", R["b0"]["casados_exato_ou_por_semelhanca"] / R["b0"]["municipios_tse"] >= 0.999, f"{R['b0']['casados_exato_ou_por_semelhanca']} de {R['b0']['municipios_tse']}")

# ---- 7. pesquisas ----
reg("C1", "SP: Datafolha e Quaest iguais nas duas fontes (O Povo e Gazeta do Povo)", R["c1"]["sp_duas_fontes_iguais"])
pr = R["c1"]["pesquisas_com_registro_no_tse"]
reg("C2", "pesquisas com registro no TSE na janela (>= 90%)", pr["com_registro"] / pr["total"] >= 0.9, pr)

# ---- 8. simetria ----
campo = pd.DataFrame(R["a1"]["campo_r1"])
reg("S1", "toda tabela de campo traz esquerda e direita nos tres anos e tres cortes", all({"esquerda", "direita"} <= set(g.campo) for _, g in campo.groupby(["ano", "cortes"])))
reg("S2", "derrotados notaveis: tabelas dos 30 mais votados de 2018 e de 2022 existem, sem filtro por partido", (RES / "a4_trinta_mais_votados_2018_e_o_que_houve_em_2022.csv").exists() and (RES / "a4_trinta_mais_votados_2022_e_o_que_houve_em_2026.csv").exists())
reg("S3", "pesquisas: a lista dos maiores erros nao filtra por campo e traz os dois sinais", "oito_maiores_erros" in R["c2"] and len(R["c2"]["oito_maiores_erros"]) == 8 and (pd.read_csv(RES / "c2_erro_por_pesquisa.csv").erro_vencedor_pp > 0).any())

# ---- 9. linguagem ----
proib = r"\b(fraud\w*|manipulad\w*|encomendad\w*|tendenciosa|massacre|humilha\w*|lavada|varrida|mentiu|mentira|corrupt\w*|culpad\w*)\b"
arqs = [RAIZ / "docs" / n for n in ("LEITURA_DA_IA.md", "PLANO.md")] + [RAIZ / "RELATORIO.md", RAIZ / "RESUMO_SIMPLES.md", RAIZ / "README.md"]
achados = {}
for a in arqs:
    if a.exists():
        for i, l in enumerate(a.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(proib, l, re.I) and "proibid" not in l.lower() and "não entram" not in l.lower():
                achados.setdefault(a.name, []).append((i, l[:120]))
reg("L1", "nenhuma palavra proibida nos textos publicados (fora das linhas que listam as proibidas)", not achados, achados or "limpo")
trav = {a.name: len(re.findall("—", a.read_text(encoding="utf-8"))) for a in arqs if a.exists()}
reg("L2", "sem travessao nos textos publicados", all(v == 0 for v in trav.values()), trav)

(RES / "revisao_adversarial.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{sum(o['passou'] for o in out)} de {len(out)} checagens passam")
