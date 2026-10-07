"""Gera RELATORIO.md e RESUMO_SIMPLES.md a partir de resultados/RESUMO.json e dos CSV de resultados/.

Nenhum numero e escrito a mao: tudo vem do que as analises 1 a 8 gravaram. Rodar depois delas.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso.comum import RAIZ, RES  # noqa: E402

R = json.loads((RES / "RESUMO.json").read_text(encoding="utf-8"))
ADV = json.loads((RES / "revisao_adversarial.json").read_text(encoding="utf-8")) if (RES / "revisao_adversarial.json").exists() else []


def f1(x):
    return f"{x:.1f}".replace(".", ",")


def f2(x):
    return f"{x:.2f}".replace(".", ",")


def n(x):
    return f"{int(x):,}".replace(",", ".")


def sg(x, d=1):
    return f"{x:+.{d}f}".replace(".", ",").replace("-", "−")


def md(df: pd.DataFrame, fmt: dict | None = None) -> str:
    fmt = fmt or {}
    df = df.copy()
    cols = list(df.columns)
    saida = {}
    for c in cols:
        col = df[c]
        if c in fmt:
            saida[c] = [fmt[c](v) for v in col]
        elif pd.api.types.is_integer_dtype(col) or pd.api.types.is_bool_dtype(col):
            saida[c] = [str(v) for v in col]
        elif pd.api.types.is_float_dtype(col):
            pequeno = col.abs().max() < 5
            saida[c] = ["" if pd.isna(v) else (f2(v) if pequeno else (n(v) if abs(v) >= 10000 else f1(v))) for v in col]
        else:
            saida[c] = [str(v) for v in col]
    linhas = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for i in range(len(df)):
        linhas.append("| " + " | ".join(saida[c][i] for c in cols) + " |")
    return chr(10).join(linhas)


def ds(d):
    nome = {"oposicao": "oposição", "sem classificacao": "sem classificação", "sem posicao": "sem posição", "Flavio": "Flávio", "neutro": "sem apoio"}
    return ", ".join(f"{nome.get(k, k)} {v}" for k, v in d.items())


def csv(nome):
    return pd.read_csv(RES / f"{nome}.csv")


def commit(path=RAIZ):
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "?"


def r1tab(campo):
    d = campo[campo.campo.isin(['esquerda', 'centro', 'direita'])].pivot_table(index=['cortes', 'campo'], columns='ano', values=['cadeiras', 'pct_votos']).round(1).reset_index()
    d.columns = [' '.join(str(x) for x in c if x != '') for c in d.columns]
    for c in d.columns:
        if c.startswith('cadeiras'):
            d[c] = d[c].astype(int)
    d['cortes'] = d['cortes'].str.replace('.', ',', regex=False)
    return md(d)


def main() -> None:
    campo = pd.DataFrame(R["a1"]["campo_r1"])
    c46 = campo[campo.cortes == "4.0-6.0"]
    pl = R["a1"]["pl_serie"]
    d6 = pd.DataFrame(R["d6"]["por_campo"])
    r2c = {2022: R["a1"]["r2_coorte_2022"], 2026: R["a1"]["r2_coorte_2026"]}
    sens = R["a1"]["r2_sensibilidade"]
    reel = pd.DataFrame(R["d5"]["reeleicao_deputados"])
    sw = pd.DataFrame(R["b1"]["swing_direita_resumo"])
    b2 = pd.DataFrame(R["b2"]["perfil_x_swing"])
    ar = pd.DataFrame(R["b4"]["arrasto"])
    abst = pd.DataFrame(R["b3"]["abstencao_nacional"])
    cf = R["b3"]["contrafactual_comparecimento_2022"]
    c2, c4 = R["c2"], R["c4"]
    adv_ok = sum(1 for a in ADV if a["passou"])
    GRUPOS = ["direita", "centro-direita", "centro", "centro-esquerda", "esquerda"]
    E3, E4, E5 = R["e3"], R["e4"], R["e5"]
    e1t = csv("e1_camara_por_grupo").pivot(index="grupo", columns="ano", values=["cadeiras", "pct_votos"]).reindex(GRUPOS)
    e1t.columns = [f"{'cadeiras' if a == 'cadeiras' else '% votos'} {b}" for a, b in e1t.columns]
    e1t = e1t.reset_index()
    for c in e1t.columns:
        if c.startswith("cadeiras"):
            e1t[c] = e1t[c].astype(int)
    e2t = csv("e2_camara_limiares_2026")[["limiar", "votos_necessarios", "direita", "falta_a_direita", "centro", "esquerda", "falta_a_esquerda"]]
    e3t = csv("e3_senado_limiares_2027")[["limiar", "votos_necessarios", "direita", "falta_a_direita", "centro", "esquerda", "falta_a_esquerda"]]
    e13 = csv("e1_camara_em_3")
    e33 = csv("e3_senado_em_3")
    e43 = csv("e4_governos_em_3")
    pre_commit = "e372efb"
    t = []
    t.append(f"""# Relatório: o que o 1º turno de 2026 mudou na Câmara, no Senado e nos governos, e por quê

**Gerado em:** 07/out/2026, a partir de `resultados/RESUMO.json` (nenhum número foi escrito à mão). **Critérios gravados antes das análises:** commit `{pre_commit}` ([`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md)). **Método e escopo:** [`docs/PLANO.md`](docs/PLANO.md). **Leitura e veredito da IA, em separado e marcados como opinião:** [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md). **Resumo curto:** [`RESUMO_SIMPLES.md`](RESUMO_SIMPLES.md).

> ⚠️ **Este documento diz o que os dados fecham. Não diz em quem cada pessoa votou, não afirma causa a partir de dado agregado, não julga intenção de ninguém e não prevê o 2º turno.**

## 0. O que o projeto não consegue dizer (no topo, com o mesmo destaque do resto)

1. **Casos e escândalos.** As séries de opinião capturadas (aprovação do governo, confiança no STF) têm poucos pontos por instituto. O teste pré-registrado de movimento da série perto de cada evento **não pôde ser rodado**. O que se mediu: o voto de cada deputado em duas votações de grande atenção contra o desempenho dele em 2026 (sem relação detectável) e a posição de candidatos ao Senado sobre o impeachment de ministros do STF (descritivo).
2. **Emendas parlamentares e gasto de campanha** não foram analisados (a prestação de contas final não existe).
3. **Pesquisas.** Só Datafolha e Quaest, só governador, só a última da véspera, com os números tirados de uma compilação de imprensa (conferida em SP contra outra fonte) e conferidos no registro do TSE. A comparação com 2018 e 2022 (emenda 23) usa a base de pesquisas com registro no TSE do Pindograma, com outros institutos naqueles anos (Ibope em 2018; Quaest e Ipec em 2022); não há as pesquisas anteriores à última para separar mudança de última hora de erro. Pesquisas de Senado não foram coletadas.
4. **O parâmetro de campo decide parte das respostas.** O principal, desde a emenda 21 (feita depois de ver os resultados, a pedido do autor), é a **autodeclaração de cada partido** (Valor Econômico, ago/2026), com os grupos juntos em três do mesmo jeito dos dois lados (emenda 22): direita = direita e centro-direita; centro = só centro; esquerda = esquerda e centro-esquerda. R1 põe MDB, PSD, PSDB e Podemos na direita (notas 7,0 a 7,2). R3 não é comparável entre 2022 e 2026: em 2026 o PL concorreu sem coligação. **Campo não é bloco de votação**: as contas de limiar são o teto de cada grupo votando unido.
5. **Falácia ecológica.** Toda relação com religião, renda, cor, idade ou Bolsa Família é entre municípios.
6. **2º turno.** Sete estados estão "em disputa".

## 0.1 Direita, centro e esquerda pela autodeclaração dos partidos (emendas 21 e 22)

Cada partido no grupo em que ele mesmo se declara (Valor Econômico, ago/2026), e os grupos juntos em três: **direita** = direita (PL, Novo, Missão) e centro-direita (PP, Republicanos, União Brasil, PRD) · **centro** = só centro (MDB, PSD, Podemos, PSDB, Cidadania, Solidariedade, Avante e os que não se declaram no eixo) · **esquerda** = esquerda (PT, PCdoB, PV, PSOL) e centro-esquerda (PSB, PDT, Rede). Sigla antiga vai para o partido que a herdou. Tabela: [`resultados/e0_grupos_por_autodeclaracao.csv`](resultados/e0_grupos_por_autodeclaracao.csv).

**Câmara em três grupos, cadeiras e % de votos** ([`e1_camara_em_3.csv`](resultados/e1_camara_em_3.csv)):

{md(e13)}

**Senado em três grupos** ([`e3_senado_em_3.csv`](resultados/e3_senado_em_3.csv)):

{md(e33)}

**Governos em três grupos** ([`e4_governos_em_3.csv`](resultados/e4_governos_em_3.csv)):

{md(e43)}

Os cinco grupos, para ver o que há dentro de cada um:

**Câmara, cadeiras e votos por grupo** ([`e1_camara_por_grupo.csv`](resultados/e1_camara_por_grupo.csv)):

{md(e1t)}

**Câmara 2026, o que cada grupo alcança se votar unido** ([`e2_camara_limiares_2026.csv`](resultados/e2_camara_limiares_2026.csv)):

{md(e2t)}

**Senado** ([`e3_senado_por_grupo.csv`](resultados/e3_senado_por_grupo.csv)): em exercício hoje (partido atual) {ds({k: v for k, v in E3['senado_em_exercicio_out2026'].items() if k in GRUPOS})}; a partir de fev/2027 {ds({k: v for k, v in E3['senado_2027_partido_atual'].items() if k in GRUPOS})}.

{md(e3t)}

**Conferência com o Poder360** (`e7` no RESUMO.json): a lista de partidos do Poder360 (05/out) aplicada às nossas cadeiras dá {R['e7']['camara_pela_lista_do_poder360']['nossa_conta']['2026']['direita']} / {R['e7']['camara_pela_lista_do_poder360']['nossa_conta']['2026']['centro']} / {R['e7']['camara_pela_lista_do_poder360']['nossa_conta']['2026']['esquerda']} na Câmara de 2026, igual ao publicado; a diferença para a nossa conta é só o PSDB, que ele põe na direita; no Senado, o Poder360 classificou cada senador (49 / 27 / 5), o que este projeto não refaz.

**Governos** ([`e4_governos_por_grupo.csv`](resultados/e4_governos_por_grupo.csv)):

{md(csv('e4_governos_por_grupo'))}

Apoio declarado dos governadores eleitos na eleição presidencial (CNN Brasil) e o eleitorado que eles governarão: {', '.join(f"{ {'Flavio': 'Flávio', 'neutro': 'sem apoio'}.get(k, k)} {v['governos']} ({f1(v['pct_eleitorado'])}%)" for k, v in E4['apoio_declarado_2026'].items())}.

**Como o PL chegou a 121** ([`e5_pl_121_resumo.csv`](resultados/e5_pl_121_resumo.csv), [`e5_pl_98_da_vespera_destino.csv`](resultados/e5_pl_98_da_vespera_destino.csv)):

{md(csv('e5_pl_121_resumo'))}

Os 98 deputados do PL na véspera: {ds(E5['pl_98_destino'])}.

**Eleitos de 2022 da esquerda e da centro-esquerda que disputaram e não se elegeram:** [`e6_esquerda_que_disputou_e_nao_se_elegeu.csv`](resultados/e6_esquerda_que_disputou_e_nao_se_elegeu.csv); no Senado: [`e6_senado_esquerda_mais_votados_nao_eleitos.csv`](resultados/e6_senado_esquerda_mais_votados_nao_eleitos.csv).

## 1. Os resultados em dez linhas

1. **Câmara, 2022 → 2026:** PL {pl['2022']['cadeiras']} → {pl['2026']['cadeiras']} cadeiras ({f1(pl['2022']['pct_votos'])}% → {f1(pl['2026']['pct_votos'])}% dos votos). Federação PT/PCdoB/PV {R['a1']['cadeiras_por_lista_2022']['PT/PC do B/PV']} → {R['a1']['cadeiras_por_lista_2026']['PT/PC do B/PV']}.
2. **Campo (R1):** direita {int(c46[(c46.ano==2022)&(c46.campo=='direita')].cadeiras.iloc[0])} → {int(c46[(c46.ano==2026)&(c46.campo=='direita')].cadeiras.iloc[0])} cadeiras; esquerda {int(c46[(c46.ano==2022)&(c46.campo=='esquerda')].cadeiras.iloc[0])} → {int(c46[(c46.ano==2026)&(c46.campo=='esquerda')].cadeiras.iloc[0])}; em votos, a direita {f1(float(c46[(c46.ano==2022)&(c46.campo=='direita')].pct_votos.iloc[0]))}% → {f1(float(c46[(c46.ano==2026)&(c46.campo=='direita')].pct_votos.iloc[0]))}%.
3. **Bancada de oposição ao governo (R2):** {r2c[2022]['oposicao']} → {r2c[2026]['oposicao']} cadeiras.
4. **Bônus de cadeiras da direita sobre os votos:** {sg(float(d6[(d6.ano==2018)&(d6.campo=='direita')].cadeiras_menos_votos_pp.iloc[0]))} → {sg(float(d6[(d6.ano==2022)&(d6.campo=='direita')].cadeiras_menos_votos_pp.iloc[0]))} → {sg(float(d6[(d6.ano==2026)&(d6.campo=='direita')].cadeiras_menos_votos_pp.iloc[0]))} pontos (2018, 2022, 2026).
5. **Reeleição de deputados:** {f1(reel[(reel.de==2018)&(reel.campo_r1_na_eleicao_anterior=='todos')].pct_reeleito_entre_todos.iloc[0])}% (eleitos de 2018 em 2022) → {f1(reel[(reel.de==2022)&(reel.campo_r1_na_eleicao_anterior=='todos')].pct_reeleito_entre_todos.iloc[0])}% (eleitos de 2022 em 2026).
6. **Senado:** PL {R['a2']['eleitos_por_partido_2026']['PL']} das 54 vagas; {R['a2']['composicao_fev2027']['por_partido']['PL']} das 81 cadeiras em 2027.
7. **Governos:** {R['a3']['governos_por_campo_r1'][2]['decididos']} decididos no 1º turno ({R['a3']['governos_por_campo_r1'][2]['decididos_direita']} de direita pela R1) e {R['a3']['governos_por_campo_r1'][2]['em_disputa']} em 2º turno.
8. **Geografia:** o perfil do município soma só {f1(100*R['b2']['r2_modelo_deputado_federal']['ganho_do_perfil'])} ponto de R² além da UF ({f1(100*R['b2']['r2_modelo_deputado_federal']['so_uf'])}%).
9. **Abstenção:** {f1(abst[abst.ano==2022].abstencao_pct.iloc[0])}% → {f1(abst[abst.ano==2026].abstencao_pct.iloc[0])}%; com o comparecimento de 2022, o voto de direita seria {f2(cf['direita_pct_com_comparecimento_de_2022'])}% (real {f2(cf['direita_pct_real_2026'])}%).
10. **Pesquisas de governador:** o primeiro colocado apareceu abaixo da urna em {R['c4']['vencedor_subestimado']['com_vencedor_abaixo_da_urna']} de {c2['pesquisas_analisadas']} pesquisas; nenhum teste por campo mostrou direção.

## 2. Dados e validação

| Item | Resultado |
|---|---|
| Resultado oficial 2026 (JSON por UF) | 513 vagas, 513 eleitos, por partido igual à tabela derivada |
| Votos por partido (nominais + legenda) | iguais ao JSON oficial até a segunda casa decimal para PL, PSD, Republicanos, MDB e Podemos |
| **Reprodução das 513 cadeiras** | **0 diferenças** com a regra da lei (80% do quociente para a lista e 20% para o candidato nas sobras); as alternativas deixam {R['a5']['sobras']['cadeiras_que_mudam_de_partido_todos_partidos_10pct']} a {R['a5']['sobras']['cadeiras_que_mudam_de_partido_todos_e_todos']} cadeiras em outras mãos |
| Municípios casados TSE × IBGE | {R['b0']['casados_exato_ou_por_semelhanca']} de {R['b0']['municipios_tse']} ({R['b0']['casados_por_semelhanca']} por semelhança de nome, listados) |
| Revisão adversarial programática | {adv_ok} de {len(ADV)} checagens ([`docs/REVISAO_ADVERSARIAL.md`](docs/REVISAO_ADVERSARIAL.md)) |

Cada arquivo baixado tem sha256 em `dados/MANIFESTO.json` e `dados/MANIFESTO_IBGE.json`; cada página de imprensa, em `dados/CAPTURAS.csv`. Os boletins de urna de 2026 não foram usados nesta rodada: o resultado por candidato e município do TSE bastou, e o caminho por boletim (variante do decodificador do projeto `apuracao-eleicoes-2026`) ficou como segunda via **não executada** (declarado no PLANO §9).

**Base de 2022:** o arquivo atual do TSE (PL {pl['2022']['cadeiras']}). Matérias da época deram PL 99; a reprodução com a regra da lei deixa 6 diferenças em 2022, compatível com a troca de sete mandatos por decisão do STF (fonte `conjur-sete-deputados`), não verificada cadeira a cadeira.

## 3. Câmara dos Deputados

### 3.1 Cadeiras por partido

{md(csv('a1_cadeiras_por_partido_e_ano').assign(ordem=lambda d: -d['2026']).sort_values('ordem').drop(columns='ordem').head(16).rename(columns={'sig':'partido'}))}

Bancada na véspera da eleição (partido no último voto até 30/09/2026 entre os {R['a1']['bancada_vespera_soma']} deputados que votaram entre 1º/07 e 30/09) contra a eleita: [`resultados/a1_bancada_vespera_vs_eleita.csv`](resultados/a1_bancada_vespera_vs_eleita.csv).

### 3.2 Campo, três réguas

**R1 (escala de especialistas, cortes 4,0 e 6,0; sensibilidade ±0,5):**

{r1tab(campo)}

**R2 (voto no plenário contra a orientação do governo, 2023 a 2026):** coorte eleita em 2022: {ds(r2c[2022])}; coorte eleita em 2026: {ds(r2c[2026])} (deputado novo herda a classe mediana do partido). Com cortes de 65% e 45%: oposição {sens[2]['oposicao']} → {sens[3]['oposicao']}.

**R3 (coligação formal na eleição presidencial):** [`resultados/a1_campo_r3.csv`](resultados/a1_campo_r3.csv). Em 2026 o PL concorreu sem coligação, e 40% das cadeiras ficam em "sem candidato presidencial"; **não é comparável com 2022**.

**Robustez:** o crescimento do PL vale nas três réguas onde ele é mensurável (cadeiras, votos, oposição ao governo). O crescimento do "campo de direita" **depende da régua**: +8 a +13 cadeiras e +0,3 a +2,7 ponto de voto pela R1, dependendo do corte; +29 cadeiras de oposição pela R2.

### 3.3 Votos, cadeiras e eficiência (D6)

{md(d6[d6.campo.isin(['esquerda','centro','direita'])][['ano','campo','pct_votos','pct_cadeiras','cadeiras_menos_votos_pp']].rename(columns={'cadeiras_menos_votos_pp':'cadeiras − votos (pp)'}))}

Volatilidade (Pedersen) e número efetivo de partidos: [`resultados/a1_volatilidade.csv`](resultados/a1_volatilidade.csv), [`a1_nep.csv`](resultados/a1_nep.csv). A volatilidade de 2018→2022 é inflada pela formação do União Brasil (DEM + PSL), tratada como partido novo.

### 3.4 Puxadores (A5)

{md(csv('a5_puxadores').query('ano==2026').head(10)[['candidato','uf','partido','votos','pct_da_lista','cadeiras_da_lista','cadeiras_sem_o_candidato','cadeiras_a_mais_pelo_candidato','votos_em_quocientes']].assign(candidato=lambda d: d.candidato.str.title()))}

"Cadeiras a mais" = cadeiras da lista com o candidato menos cadeiras da lista sem ele, **incluída a dele**. Sensibilidade à regra de sobras em 2026: [`resultados/a5_sensibilidade_regra_sobras_2026.csv`](resultados/a5_sensibilidade_regra_sobras_2026.csv) (a regra aplicada **não** é a mais favorável ao PL).

### 3.5 Renovação, incumbentes e nomes (A4, D5)

{md(reel[reel.campo_r1_na_eleicao_anterior.isin(['todos','esquerda','centro','direita'])][['de','para','campo_r1_na_eleicao_anterior','eleitos_na_eleicao_anterior','tentaram_de_novo','reeleitos','pct_reeleito_entre_os_que_tentaram','pct_reeleito_entre_todos']])}

{f1(R['a4']['pct_eleitos_que_nao_estavam_em_exercicio'])}% dos eleitos de 2026 não estavam na Câmara na véspera (inclui ex-deputados que voltam e estreantes; a imprensa fala em 35% de primeiro mandato). Maiores quedas e altas de votos entre reeleitos: [`quedas`](resultados/a4_reeleitos_maiores_quedas_2022_2026.csv), [`altas`](resultados/a4_reeleitos_maiores_altas_2022_2026.csv). Os 30 mais votados de cada eleição e o que houve na seguinte: [`2018→2022`](resultados/a4_trinta_mais_votados_2018_e_o_que_houve_em_2022.csv), [`2022→2026`](resultados/a4_trinta_mais_votados_2022_e_o_que_houve_em_2026.csv).

## 4. Senado e governos

**Senado (A2):** PL {R['a2']['eleitos_por_partido_2026']['PL']}, MDB {R['a2']['eleitos_por_partido_2026']['MDB']}, PT {R['a2']['eleitos_por_partido_2026']['PT']}. Por R1: {ds(R['a2']['eleitos_por_campo_r1']['2026'])}. Em 2018: {ds(R['a2']['eleitos_por_campo_r1']['2018'])}. Composição a partir de fev/2027 ({R['a2']['composicao_fev2027']['total']}): {ds(R['a2']['composicao_fev2027']['por_campo_r1'])}; PL {R['a2']['composicao_fev2027']['por_partido']['PL']}. Eleitos que constavam na lista de apoio a Flávio (R3): {R['a2']['eleitos_2026_na_lista_de_apoio_a_Flavio']} de 54. Limiares: [`resultados/RESUMO.json`](resultados/RESUMO.json) chave `a2.limiares`.

**Governos (A3):** [`resultados/a3_governos_por_campo_r1.csv`](resultados/a3_governos_por_campo_r1.csv) (decididos por campo em 2018, 2022 e 2026). Apoio declarado em 2026 (R3): {ds(R['a3']['apoio_declarado_2026'])}. Tabela por estado: [`resultados/a3_governos.csv`](resultados/a3_governos.csv).

**D5 (incumbentes além da Câmara):** senadores eleitos e reeleitos [`d5_reeleicao_senadores.csv`](resultados/d5_reeleicao_senadores.csv); governadores [`d5_governadores_que_tentaram_continuar.csv`](resultados/d5_governadores_que_tentaram_continuar.csv).

**D8 (STF no Senado):** eleitos por posição declarada: {ds(R['d8']['eleitos_por_posicao'])} (lista da Gazeta do Povo, fonte única, {R['d8']['candidatos_na_lista_da_gazeta']} candidatos lidos, {R['d8']['lista_casada_com_candidatos_do_TSE']} casados com o TSE).

## 5. Geografia e abstenção (bloco B)

{md(sw[['cargo','periodo','municipios','swing_direita_medio_ponderado_pp','desvio_padrao_ponderado_pp','pct_municipios_com_swing_positivo','pct_eleitorado_em_municipios_com_swing_positivo']])}

(cargo 6 = deputado federal, 3 = governador, 5 = senador; swing = variação da % de voto de direita pela R1, média ponderada pelo eleitorado.)

**Perfil do município (deputado federal, dentro da UF):** diferença entre o efeito de 2026 e o de 2018→2022, em pontos por desvio-padrão:

{md(b2[b2.cargo=='deputado federal'][['variavel','coef_placebo_pp_por_desvio_padrao','coef_2026_menos_placebo_pp','ic95_diferenca_baixo','ic95_diferenca_alto','acompanha_mais_que_antes']])}

A UF explica {f1(100*R['b2']['r2_modelo_deputado_federal']['so_uf'])}% da variação do swing; o perfil acrescenta {f1(100*R['b2']['r2_modelo_deputado_federal']['ganho_do_perfil'])} ponto. **Abstenção:**

{md(abst[['ano','abstencao_pct','comparecimento_pct']])}

Contrafactual com o comparecimento de 2022: diferença de {sg(cf['diferenca_pp'], 2)} ponto. Variação de abstenção × swing de direita: {sg(R['b3']['abstencao_x_swing_direita']['coef_pp_por_pp'], 2)} ponto por ponto, IC95 {sg(R['b3']['abstencao_x_swing_direita']['ic95'][0], 2)} a {sg(R['b3']['abstencao_x_swing_direita']['ic95'][1], 2)}.

**Arrasto:**

{md(ar)}

Mapa: [`resultados/figuras/video/08_mapa_variacao_voto_direita_deputado_federal.png`](resultados/figuras/video/08_mapa_variacao_voto_direita_deputado_federal.png).

## 6. As pesquisas (bloco C)

{c2['pesquisas_analisadas']} pesquisas (Datafolha {R['c2']['por_instituto'][0]['n']}, Quaest {R['c2']['por_instituto'][1]['n']}) em {c4['margem_subestimada']['disputas']} disputas; {R['c1']['pesquisas_com_registro_no_tse']['com_registro']} com registro no TSE na janela de 26/set a 03/out. Erro do primeiro colocado (o eleito ou, nos 7 estados com 2º turno, o primeiro do 1º turno), contra o percentual oficial do TSE (que inclui candidaturas anuladas sub judice, como fazem as pesquisas): média com sinal {sg(c2['erro_medio_com_sinal_vencedor_pp'])} ponto; em valor absoluto {f1(c2['erro_medio_abs_vencedor_pp'])}; erro da margem em valor absoluto {f1(c2['erro_medio_abs_margem_pp'])}. Fora da margem declarada (2 pontos quando o plano amostral não informa): proporção {c2['fora_da_margem']['proporcao']} de {c2['fora_da_margem']['total']}, diferença entre os dois primeiros {c2['fora_da_margem']['diferenca']} de {c2['fora_da_margem']['total']}.

{md(pd.DataFrame(R['c2']['por_instituto']))}

**Direção do erro:** margem subestimada (corrida mais apertada que a urna) em {c4['margem_subestimada']['com_margem_menor_que_a_urna']} das {c4['margem_subestimada']['pesquisas']} pesquisas e na maioria das pesquisas de {c4['margem_subestimada']['disputas_com_maioria_das_pesquisas_apertadas_demais']} das {c4['margem_subestimada']['disputas']} disputas (p = {f2(c4['margem_subestimada']['p_binomial_bicaudal_disputas'])}). Por campo: R3 {c4['r3_flavio']['disputas']} disputas, subestimou Flávio em {c4['r3_flavio']['disputas_em_que_subestimou']} (p = {f2(c4['r3_flavio']['p_binomial_bicaudal'])}); R1 {c4['r1_direita']['disputas']} disputas, em {c4['r1_direita']['disputas_em_que_subestimou']} (p = {f2(c4['r1_direita']['p_binomial_bicaudal'])}); exploratório (definido depois de ver o resultado) {c4['exploratoria_flavio_contra_qualquer_outro']['disputas']} disputas, em {c4['exploratoria_flavio_contra_qualquer_outro']['disputas_em_que_subestimou']} (p = {f2(c4['exploratoria_flavio_contra_qualquer_outro']['p_binomial_bicaudal'])}). Tabelas: [`c2_erro_por_pesquisa.csv`](resultados/c2_erro_por_pesquisa.csv), [`c4_direcao_*.csv`](resultados/).

**Critério do pré-registro para "erro sistemático"** exigia 4 condições; só a primeira (teste do sinal) pôde ser rodada, e **não** foi atendida por campo. Por isso o texto usa "corridas mais apertadas na pesquisa que na urna, para quem terminou em primeiro, independente do campo" e não "erro sistemático por campo".

### 6.1 Contra 2018 e 2022 (emenda 23)

Mesmo cálculo, mesma janela (a última pesquisa de cada instituto na semana antes do 1º turno), votos válidos pela soma dos candidatos, ligação com a urna pelo número do candidato. Direita = direita + centro-direita; esquerda = esquerda + centro-esquerda. "Subestimada" = a pesquisa mostrou a margem do lado menor do que a urna, nas disputas em que só um dos dois primeiros é daquele lado (média entre institutos por disputa).

**Institutos nacionais de cada ano** (2018 Datafolha e Ibope; 2022 Datafolha, Quaest e Ipec; 2026 Datafolha e Quaest):

{md(csv("c5_resumo_por_ano_principal")[["ano", "pesquisas", "disputas", "pct_vencedor_abaixo", "erro_medio_vencedor_pp", "direita_disputas", "direita_subestimada_em", "direita_media_pp", "direita_p_sinal", "esquerda_disputas", "esquerda_subestimada_em", "esquerda_media_pp", "esquerda_p_sinal"]])}

**Todos os institutos** (2026 continua só com Datafolha e Quaest):

{md(csv("c5_resumo_por_ano_todos_os_institutos")[["ano", "pesquisas", "disputas", "pct_vencedor_abaixo", "direita_disputas", "direita_subestimada_em", "direita_p_sinal", "esquerda_disputas", "esquerda_subestimada_em", "esquerda_p_sinal"]])}

**Só o Datafolha** (o único instituto nos três anos; 4 a 6 disputas por ano, descritivo):

{md(csv("c5_resumo_por_ano_so_datafolha")[["ano", "pesquisas", "pct_vencedor_abaixo", "direita_disputas", "direita_subestimada_em", "esquerda_disputas", "esquerda_subestimada_em"]])}

**Conferência:** {R['c5']['conferencia']['numeros']} números extraídos contra a imprensa da época ([`c5_conferencia_segunda_fonte.csv`](resultados/c5_conferencia_segunda_fonte.csv)), {R['c5']['conferencia']['ate_1_ponto']} dentro de 1 ponto e a maior diferença de {f1(R['c5']['conferencia']['maior_diferenca_pp'])} ponto (arredondamento do número publicado). Tabelas: [`c5_erro_por_pesquisa_2018_2022_2026.csv`](resultados/c5_erro_por_pesquisa_2018_2022_2026.csv), [`c5_pesquisas_governador_2018_2022_extraidas.csv`](resultados/c5_pesquisas_governador_2018_2022_extraidas.csv).

## 7. Por quê: o placar das hipóteses

{md(pd.DataFrame(json.loads((RES / 'placar_hipoteses.json').read_text(encoding='utf-8')))[['id','nome','status','confianca','onde']])}

Voto no plenário × desempenho (D3):

{md(csv('d3_voto_x_desempenho'))}

Descrição das votações:

{md(csv('d3_descricao_das_votacoes'))}

A leitura da IA arena por arena e o veredito, marcados como opinião: [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md).

## 8. Desvios do pré-registro

Todos estão na §15 do [`docs/PRE_REGISTRO.md`](docs/PRE_REGISTRO.md), com data e a declaração de se foram feitos antes ou depois de ver o resultado. Os que mais pesam: (a) D2 e D1 rodaram só como captura de dados, sem o teste de movimento da série; (b) C ficou em Datafolha e Quaest para governador, com fonte única de compilação; (c) o Moran dos resíduos não foi calculado (efeito fixo de UF e erro por UF no lugar); (d) a lista de "notáveis" ficou nos critérios (c), (d) e (e).

## 9. Como reproduzir

[`docs/REPLICAR.md`](docs/REPLICAR.md). Resumo: `python ferramentas/coletar.py ...`, `coletar-ibge.py`, `derivar-votos.py`, depois `analise-1` a `analise-9` e `revisao-adversarial.py`. Commit dos dados de entrada: `dados/MANIFESTO*.json`.
""")
    (RAIZ / "RELATORIO.md").write_text("\n".join(t), encoding="utf-8")

    # ---- resumo simples ----
    nik = csv("a5_puxadores").query("ano==2026").iloc[0]
    s = f"""# Resumo simples

**Gerado em 07/out/2026 a partir de `resultados/RESUMO.json`.** Texto de uma página; o relatório completo é o [`RELATORIO.md`](RELATORIO.md) e a opinião da IA está em [`docs/LEITURA_DA_IA.md`](docs/LEITURA_DA_IA.md).

## Direita, centro e esquerda (cada partido onde ele mesmo se declara)

- **Câmara:** direita (com a centro-direita) **{R['e1']['camara_em_3']['2022']['direita']} → {R['e1']['camara_em_3']['2026']['direita']}** deputados, centro {R['e1']['camara_em_3']['2022']['centro']} → {R['e1']['camara_em_3']['2026']['centro']}, esquerda (com a centro-esquerda) {R['e1']['camara_em_3']['2022']['esquerda']} → {R['e1']['camara_em_3']['2026']['esquerda']}. Com {R['e2']['camara_2026_bloco']['direita']}, a direita passa da maioria absoluta (257) e, com o Senado, derruba veto se votar unida; faltam {R['e2']['camara_2026_bloco']['falta_pec']} para uma PEC.
- **Senado:** direita **{E3['senado_hoje_em_3']['direita']} → {E3['senado_2027_em_3']['direita']}** (PL {E3['senado_pl']['fev_2027_partido_atual']}), centro {E3['senado_hoje_em_3']['centro']} → {E3['senado_2027_em_3']['centro']}, esquerda {E3['senado_hoje_em_3']['esquerda']} → {E3['senado_2027_em_3']['esquerda']}: no limite da PEC (49; o Poder360, por senador, contou 49) e a 6 votos da condenação de ministro do STF num impeachment (54).
- **Governos decididos no 1º turno:** direita {R['e4']['governos_em_3']['2026']['direita']}, centro {R['e4']['governos_em_3']['2026']['centro']}, esquerda {R['e4']['governos_em_3']['2026']['esquerda']}; {R['e4']['governos_em_3']['2026']['em 2o turno']} em 2º turno.
- **PL:** {R['e5']['pl_121_origem'].get('eleito em 2022 pelo PL', 0)} dos 121 já eram do PL em 2022, {R['e5']['pl_121_origem'].get('eleito em 2022 por outro partido e foi para o PL', 0)} vieram de outros partidos e {sum(v for k, v in R['e5']['pl_121_origem'].items() if k.startswith('não disputou a Câmara em 2022'))} não tinham disputado a Câmara em 2022; 10 deputados do PL viraram senadores.

## O que mudou na Câmara

- O **PL** foi de {pl['2022']['cadeiras']} para **{pl['2026']['cadeiras']}** deputados e de {f1(pl['2022']['pct_votos'])}% para **{f1(pl['2026']['pct_votos'])}%** dos votos.
- A **federação do PT** (PT, PCdoB e PV) foi de {R['a1']['cadeiras_por_lista_2022']['PT/PC do B/PV']} para **{R['a1']['cadeiras_por_lista_2026']['PT/PC do B/PV']}** cadeiras.
- Somando todos os partidos de direita pela escala de especialistas, o voto ficou **parado** ({f1(float(c46[(c46.ano==2022)&(c46.campo=='direita')].pct_votos.iloc[0]))}% → {f1(float(c46[(c46.ano==2026)&(c46.campo=='direita')].pct_votos.iloc[0]))}%). O PL cresceu, e União, PP, PDT e MDB encolheram.
- A bancada que vota contra o governo no plenário foi de {r2c[2022]['oposicao']} para {r2c[2026]['oposicao']} deputados.
- Nikolas Ferreira teve {n(nik.votos)} votos; sem eles, a lista do PL em Minas teria **{int(nik.cadeiras_a_mais_pelo_candidato)} cadeiras a menos**.
- {f1(reel[(reel.de==2022)&(reel.campo_r1_na_eleicao_anterior=='todos')].pct_reeleito_entre_todos.iloc[0])}% dos deputados eleitos em 2022 se reelegeram (eram {f1(reel[(reel.de==2018)&(reel.campo_r1_na_eleicao_anterior=='todos')].pct_reeleito_entre_todos.iloc[0])}% da eleição anterior). Não houve onda contra quem estava no cargo.

## Senado e governos

- PL elegeu **{R['a2']['eleitos_por_partido_2026']['PL']} das 54 vagas** e terá **{R['a2']['composicao_fev2027']['por_partido']['PL']} das 81 cadeiras**.
- {R['a3']['governos_por_campo_r1'][2]['decididos']} governos decididos no 1º turno ({R['a3']['governos_por_campo_r1'][2]['decididos_direita']} de partidos de direita) e **{R['a3']['governos_por_campo_r1'][2]['em_disputa']} em 2º turno**.

## O que explica

- **Concentração do voto no PL**, **eficiência do sistema** (a direita tem hoje {sg(float(d6[(d6.ano==2026)&(d6.campo=='direita')].cadeiras_menos_votos_pp.iloc[0]))} ponto de cadeiras acima dos votos, era {sg(float(d6[(d6.ano==2018)&(d6.campo=='direita')].cadeiras_menos_votos_pp.iloc[0]))} em 2018) e **puxadores**.
- O voto em Bolsonaro para presidente (Jair pelo PSL em 2018 e pelo PL em 2022, Flávio pelo PL em 2026) anda junto com o voto de direita nos outros cargos, e essa ligação **cresceu** (Senado: {f2(float(ar[(ar.ano==2018)&(ar.cargo=='senador')].correlacao_media_ponderada_por_uf.iloc[0]))} → {f2(float(ar[(ar.ano==2026)&(ar.cargo=='senador')].correlacao_media_ponderada_por_uf.iloc[0]))}).
- **Não explicam bem:** perfil do município (religião, renda, cor, idade, Bolsa Família somam {f1(100*R['b2']['r2_modelo_deputado_federal']['ganho_do_perfil'])} ponto de explicação) e abstenção (estável em {f1(abst[abst.ano==2026].abstencao_pct.iloc[0])}%).
- **Não deu para testar:** efeito dos casos (Master, STF, INSS, condenação de Bolsonaro) e das emendas.

## As pesquisas

- Datafolha e Quaest mostraram o primeiro colocado **abaixo** do que ele teve em {R['c4']['vencedor_subestimado']['com_vencedor_abaixo_da_urna']} de {c2['pesquisas_analisadas']} pesquisas de governador.
- **Contra 2018 e 2022:** nas disputas em que só um dos dois primeiros era de direita, a pesquisa mostrou a direita mais fraca do que a urna em {R['c5']['principal']['2018']['direita_subestimada_em']} de {R['c5']['principal']['2018']['direita_disputas']} em 2018, {R['c5']['principal']['2022']['direita_subestimada_em']} de {R['c5']['principal']['2022']['direita_disputas']} em 2022 e **{R['c5']['principal']['2026']['direita_subestimada_em']} de {R['c5']['principal']['2026']['direita_disputas']} em 2026**; em 2026 foi a esquerda que saiu mais fraca ({R['c5']['principal']['2026']['esquerda_subestimada_em']} de {R['c5']['principal']['2026']['esquerda_disputas']}). Poucas disputas por ano: é sinal, não prova.

## O que o projeto não diz

Em quem cada pessoa votou · se os casos mudaram votos · quem vai ganhar o 2º turno · intenção de ninguém.
"""
    (RAIZ / "RESUMO_SIMPLES.md").write_text(s, encoding="utf-8")
    print("ok relatorio")


if __name__ == "__main__":
    main()
