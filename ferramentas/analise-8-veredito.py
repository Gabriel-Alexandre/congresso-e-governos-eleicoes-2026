"""A leitura da IA: placar das hipoteses e veredito por arena.

Cada frase com numero busca o numero em resultados/RESUMO.json ou nos CSV de resultados/. O texto e opiniao da IA, marcada como
opiniao, escrita depois da revisao adversarial (docs/REVISAO_ADVERSARIAL.md) e passada pelo teste do espelho.
Saidas: docs/LEITURA_DA_IA.md e resultados/placar_hipoteses.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso.comum import RAIZ, RES  # noqa: E402

R = json.loads((RES / "RESUMO.json").read_text(encoding="utf-8"))


def f1(x):
    return f"{x:.1f}".replace(".", ",")


def f2(x):
    return f"{x:.2f}".replace(".", ",")


def sg(x, d=1):
    return f"{x:+.{d}f}".replace(".", ",").replace("-", "−")


def n(x):
    return f"{int(x):,}".replace(",", ".")


def main() -> None:
    campo = pd.DataFrame(R["a1"]["campo_r1"])
    c46 = campo[campo.cortes == "4.0-6.0"]
    dir_c = {a: int(c46[(c46.ano == a) & (c46.campo == "direita")].cadeiras.iloc[0]) for a in (2018, 2022, 2026)}
    esq_c = {a: int(c46[(c46.ano == a) & (c46.campo == "esquerda")].cadeiras.iloc[0]) for a in (2018, 2022, 2026)}
    dir_v = {a: float(c46[(c46.ano == a) & (c46.campo == "direita")].pct_votos.iloc[0]) for a in (2018, 2022, 2026)}
    esq_v = {a: float(c46[(c46.ano == a) & (c46.campo == "esquerda")].pct_votos.iloc[0]) for a in (2018, 2022, 2026)}
    dir_p = {a: float(c46[(c46.ano == a) & (c46.campo == "direita")].pct_cadeiras.iloc[0]) for a in (2018, 2022, 2026)}
    s35 = campo[(campo.cortes == "3.5-5.5") & (campo.campo == "direita")].set_index("ano").cadeiras
    s45 = campo[(campo.cortes == "4.5-6.5") & (campo.campo == "direita")].set_index("ano").cadeiras
    e35 = campo[(campo.cortes == "3.5-5.5") & (campo.campo == "esquerda")].set_index("ano").cadeiras
    e45 = campo[(campo.cortes == "4.5-6.5") & (campo.campo == "esquerda")].set_index("ano").cadeiras
    pl = R["a1"]["pl_serie"]
    d6 = pd.DataFrame(R["d6"]["por_campo"])
    bonus = {a: float(d6[(d6.ano == a) & (d6.campo == "direita")].cadeiras_menos_votos_pp.iloc[0]) for a in (2018, 2022, 2026)}
    reel = pd.DataFrame(R["d5"]["reeleicao_deputados"])
    rl = {(r.de, r.campo_r1_na_eleicao_anterior): r for r in reel.itertuples()}
    sw = pd.DataFrame(R["b1"]["swing_direita_resumo"])
    sw6 = sw[(sw.cargo == 6) & sw.periodo.str.startswith("2022")].iloc[0]
    sw3 = sw[(sw.cargo == 3) & sw.periodo.str.startswith("2022")].iloc[0]
    sw3p = sw[(sw.cargo == 3) & sw.periodo.str.contains("placebo")].iloc[0]
    sw5 = sw[(sw.cargo == 5) & sw.periodo.str.startswith("2018")].iloc[0]
    sw5p = sw[(sw.cargo == 5) & sw.periodo.str.startswith("2010")].iloc[0]
    ar = pd.DataFrame(R["b4"]["arrasto"])
    A = lambda a, c: float(ar[(ar.ano == a) & (ar.cargo == c)].correlacao_media_ponderada_por_uf.iloc[0])  # noqa: E731
    r2m = R["b2"]["r2_modelo_deputado_federal"]
    abst = pd.DataFrame(R["b3"]["abstencao_nacional"]).set_index("ano")
    cf = R["b3"]["contrafactual_comparecimento_2022"]
    se = R["a2"]["eleitos_por_campo_r1"]
    comp = R["a2"]["composicao_fev2027"]
    lim = R["a2"]["limiares"]
    d8 = R["d8"]
    gov = pd.DataFrame(R["a3"]["governos_por_campo_r1"]).set_index("ano")
    d3 = pd.DataFrame(R["d3"]["modelos"])
    v1 = d3[d3.votacao.str.startswith("V1") & (d3.desfecho == "eleito em 2026")].iloc[0]
    v4 = d3[d3.votacao.str.startswith("V4") & (d3.desfecho == "eleito em 2026")].iloc[0]
    dd = pd.DataFrame(R["d3"]["descricao"])
    c2 = R["c2"]; c4 = R["c4"]
    _e = pd.read_csv(RES / 'c2_erro_por_pesquisa.csv').set_index(['uf', 'instituto'])['erro_vencedor_pp']
    rj_d, rj_q, ap_q = _e[('RJ', 'Datafolha')], _e[('RJ', 'Quaest')], _e[('AP', 'Quaest')]
    ex = pd.read_csv(RES / 'c2_erro_por_pesquisa.csv').dropna(subset=['subestimou_flavio_pp_exploratoria']).groupby('uf')['subestimou_flavio_pp_exploratoria'].mean()
    ex_pos = ', '.join(ex[ex > 5].sort_values(ascending=False).index)
    ex_neg = ', '.join(f"{u_} ({f1(abs(v_))})" for u_, v_ in ex[ex < -5].sort_values().items())
    puxa = pd.read_csv(RES / "a5_puxadores.csv").query("ano==2026")
    nik = puxa[puxa.candidato.str.contains("NIKOLAS")].iloc[0]
    pav = puxa[puxa.candidato.str.contains("PAVANATO")].iloc[0]
    r2c = {int(k): v for k, v in {"2022": R["a1"]["r2_coorte_2022"], "2026": R["a1"]["r2_coorte_2026"]}.items()}
    ep = R["a2"]["eleitos_por_partido_2026"]
    lista_fed = R["a1"]["cadeiras_por_lista_2022"], R["a1"]["cadeiras_por_lista_2026"]
    fedpt = (lista_fed[0].get("PT/PC do B/PV"), lista_fed[1].get("PT/PC do B/PV"))

    vp = pd.read_csv(RES / 'a1_votos_pct_por_partido_e_ano.csv').set_index('sig')
    dv = (100 * (vp['2026'] - vp['2022'])).round(1)
    perdas = ', '.join(f"{ {'UNIAO': 'União', 'SOLIDARIEDADE': 'Solidariedade'}.get(p_, p_) } {sg(dv[p_])}" for p_ in ('UNIAO', 'PP', 'SOLIDARIEDADE', 'PSDB') if p_ in dv.index) + ' pontos'
    # bloco E: autodeclaracao dos partidos, com o PL no centro (emendas 21 e 22)
    E1 = R["e1"]; E3 = R["e3"]; E4 = R["e4"]; E5 = R["e5"]
    cc = {int(a): v for a, v in E1["camara_cadeiras"].items()}
    c3 = {int(a): v for a, v in E1["camara_em_3"].items()}
    v3 = {int(a): v for a, v in E1["camara_votos_em_3"].items()}
    lc = {r["votos_necessarios"]: r for r in R["e2"]["camara_2026"]}
    lc22 = {r["votos_necessarios"]: r for r in R["e2"]["camara_2022"]}
    blc = R["e2"]["camara_2026_bloco"]
    vet = R["e2"]["derrubar_veto_2027"]
    ls = {r["votos_necessarios"]: r for r in E3["senado_limiares_2027"]}
    sh3 = E3["senado_hoje_em_3"]
    s273 = E3["senado_2027_em_3"]
    sh = E3["senado_em_exercicio_out2026"]
    o121 = E5["pl_121_origem"]
    d98 = E5["pl_98_destino"]
    mig = E5["migrantes_de_onde"]
    nomes_part = {"UNIAO": "União", "REPUBLICANOS": "Republicanos", "PODE": "Podemos", "AVANTE": "Avante"}
    mig_txt = ", ".join(f"{v} do {nomes_part.get(k, k)}" for k, v in sorted(mig.items(), key=lambda kv: -kv[1]))
    sen_pl = pd.read_csv(RES / "e5_pl_98_da_vespera_destino.csv").query("destino == 'disputou senador: eleito'")["nome"].tolist()
    apo = E4["apoio_declarado_2026"]
    g3 = {int(a): v for a, v in E4["governos_em_3"].items()}
    cv_cd22 = R["e1"]["camara_pct_votos"]["2022"]["centro-direita"]
    cv_cd26 = R["e1"]["camara_pct_votos"]["2026"]["centro-direita"]
    el3 = E4["pct_eleitorado_governado_2026_em_3"]
    p3 = E1["partido_de_bolsonaro"]
    k_nao = [k for k in o121 if k.startswith("não disputou a Câmara em 2022")]
    n_nao = sum(o121[k] for k in k_nao)
    n_nunca = o121.get("não disputou a Câmara em 2022: nenhuma candidatura estadual ou federal de 2006 a 2018", 0)
    placar = [
        {"id": "H1", "nome": "Virada do eleitorado da esquerda para a direita", "status": "inconsistente", "confianca": "média",
         "onde": f"esquerda (com a centro-esquerda): {f1(v3[2022]['esquerda'])}% → {f1(v3[2026]['esquerda'])}% dos votos para deputado; pela R1, direita {f1(dir_v[2022])}% → {f1(dir_v[2026])}%"},
        {"id": "H9", "nome": "Do centro para a direita, e dentro da direita para o PL", "status": "consistente", "confianca": "alta",
         "onde": f"direita (com a centro-direita) {f1(v3[2022]['direita'])}% → {f1(v3[2026]['direita'])}% dos votos e {c3[2022]['direita']} → {c3[2026]['direita']} deputados; centro {f1(v3[2022]['centro'])}% → {f1(v3[2026]['centro'])}%; PL {f1(pl['2022']['pct_votos'])}% → {f1(pl['2026']['pct_votos'])}%"},
        {"id": "H2", "nome": "Referendo sobre o governo", "status": "não testável", "confianca": "baixa",
         "onde": "só há uma aprovação capturada (Quaest, jul/2026, 48 × 47); sem série"},
        {"id": "H3", "nome": "Anti-incumbência (cansaço de quem está no cargo)", "status": "inconsistente", "confianca": "média",
         "onde": f"deputados reeleitos: {f1(rl[(2022,'todos')].pct_reeleito_entre_todos)}% contra {f1(rl[(2018,'todos')].pct_reeleito_entre_todos)}% em 2022"},
        {"id": "H4", "nome": "Estrutura e eficiência (listas, federações, puxadores)", "status": "consistente", "confianca": "alta",
         "onde": f"bônus de cadeiras da direita: {sg(bonus[2018])} → {sg(bonus[2022])} → {sg(bonus[2026])} pp; puxadores"},
        {"id": "H5", "nome": "Máquina (emendas, fundo, mandato)", "status": "não testável", "confianca": "baixa", "onde": "emendas não foram analisadas nesta rodada"},
        {"id": "H6", "nome": "Casos e escândalos (Master, STF, INSS, condenação)", "status": "não testável", "confianca": "baixa",
         "onde": f"voto na PEC da Blindagem sem relação com a eleição ({sg(v1.coef_sim*100)} pp); séries de opinião insuficientes"},
        {"id": "H7", "nome": "Composição do eleitorado (perfil e abstenção)", "status": "inconsistente", "confianca": "média",
         "onde": f"perfil soma {f1(100*r2m['ganho_do_perfil'])} ponto de R² além da UF; abstenção {f1(abst.loc[2022,'abstencao_pct'])}% → {f1(abst.loc[2026,'abstencao_pct'])}%"},
        {"id": "H8", "nome": "Arrasto do candidato à Presidência", "status": "consistente", "confianca": "alta",
         "onde": f"correlação com o voto de direita: senador {f2(A(2018,'senador'))} → {f2(A(2026,'senador'))}, deputado {f2(A(2022,'deputado federal'))} → {f2(A(2026,'deputado federal'))}"},
    ]
    (RES / "placar_hipoteses.json").write_text(json.dumps(placar, ensure_ascii=False, indent=1), encoding="utf-8")

    t = []
    t.append(f"""# A leitura da IA, arena por arena

**Escrito em:** 07/out/2026. **O que é:** a opinião da IA que executou o processo, marcada como opinião, depois da revisão adversarial em três passadas ([`REVISAO_ADVERSARIAL.md`](REVISAO_ADVERSARIAL.md)). Cada número sai de [`resultados/RESUMO.json`](../resultados/RESUMO.json) ou dos CSV de `resultados/`.

> ⚠️ **Opinião não é prova.** O [`RELATORIO.md`](../RELATORIO.md) diz o que os dados fecham. Este arquivo diz qual é a leitura mais provável de cada resultado, o grau de confiança e o que ficou sem resposta. Nenhuma frase aqui julga intenção de pessoa, partido ou instituto, e nenhuma afirma causa onde o desenho só mostra coincidência.
>
> **Dependência da régua.** "Direita", "centro" e "esquerda" são definições (docs/PRE_REGISTRO.md §1). O que vale nas três réguas é dito como robusto; o que depende de uma régua é dito como dependente dela. **R1** é a escala de especialistas de 2021, que põe MDB, PSD, PSDB e Podemos na direita (notas de 7,0 a 7,2). **R2** é o voto no plenário contra a orientação do governo. **R3** é a coligação formal na eleição presidencial: em 2026 o PL concorreu sem coligação, então R3 não é comparável entre 2022 e 2026.

## O placar

| # | Hipótese | Situação | Confiança | O que sustenta |
|---|---|---|---|---|""")
    for h in placar:
        t.append(f"| {h['id']} | {h['nome']} | **{h['status']}** | {h['confianca']} | {h['onde']} |")
    t.append(f"""
*consistente* = as previsões da hipótese aparecem nos testes nomeados; *inconsistente* = aparece o contrário; *não testável* = o dado coletado não alcança. Mais de uma hipótese pode valer ao mesmo tempo. **H9** entrou depois de ver os resultados, com o parâmetro da autodeclaração (emendas 21 e 22 do pré-registro).

---

## O parâmetro principal: direita, centro e esquerda pelo jeito que cada partido se declara

**Como se conta (emendas 21 e 22, 07/out, a pedido do autor, depois de ver os resultados):** cada partido vai para o grupo em que ele mesmo se declara (Valor Econômico, ago/2026), e os grupos se juntam em três, do mesmo jeito dos dois lados: **direita** = quem se declara de direita (PL, Novo, Missão) **e** de centro-direita (PP, Republicanos, União Brasil, PRD); **centro** = só quem se declara de centro (MDB, PSD, Podemos, PSDB, Cidadania, Solidariedade, Avante e os que não se declaram no eixo); **esquerda** = quem se declara de esquerda (PT, PCdoB, PV, PSOL) **e** de centro-esquerda (PSB, PDT, Rede). Sigla antiga vai para o partido que a herdou (PSL e DEM → União). O GPS Partidário da Folha (set/2026), que mede comportamento, também põe PL e Novo à direita e MDB e PSD no centro. R1, R2 e R3 continuam abaixo como comparação.

**Câmara, os fatos (alto):** a direita foi de {c3[2018]['direita']} deputados em 2018 para {c3[2022]['direita']} em 2022 e **{c3[2026]['direita']}** em 2026; o centro de {c3[2018]['centro']} para {c3[2022]['centro']} e **{c3[2026]['centro']}**; a esquerda de {c3[2018]['esquerda']} para {c3[2022]['esquerda']} e **{c3[2026]['esquerda']}**. Em votos para deputado, de 2022 para 2026: direita {f1(v3[2022]['direita'])}% → {f1(v3[2026]['direita'])}%, centro {f1(v3[2022]['centro'])}% → {f1(v3[2026]['centro'])}%, esquerda {f1(v3[2022]['esquerda'])}% → {f1(v3[2026]['esquerda'])}%. Dentro da direita, PL, Novo e Missão foram de {cc[2022]['direita']} para {cc[2026]['direita']} deputados e a centro-direita de {cc[2022]['centro-direita']} para {cc[2026]['centro-direita']}; dentro da esquerda, PT, PCdoB, PV e PSOL foram de {cc[2022]['esquerda']} para {cc[2026]['esquerda']} e a centro-esquerda de {cc[2022]['centro-esquerda']} para {cc[2026]['centro-esquerda']} (o PDT foi de 16 para 6). O partido de Bolsonaro em cada eleição: PSL com {p3['2018 (PSL)']} em 2018, PL com {p3['2022 (PL)']} em 2022 e {p3['2026 (PL)']} em 2026.

**Câmara, o que cada grupo alcança (alto para a conta, baixo para o comportamento):** com **{blc['direita']}** deputados, a direita passa da maioria absoluta (257), o que a Câmara eleita em 2022 não tinha ({lc22[257]['direita']}). Votando unida, ela elege o presidente da Câmara, aprova lei complementar, abre CPI, barra qualquer PEC (206) e, com os {vet['senado_direita_por_partido']} senadores (49 na conta do Poder360, acima de 41), **derruba veto do Presidente da República** (art. 66 §4º). Faltam {blc['falta_pec']} votos para uma PEC (308) e {blc['falta_impeachment']} para autorizar um impeachment de Presidente (342). A esquerda, com {blc['esquerda']}, não barra sozinha nem uma PEC (faltam {blc['falta_esquerda_barrar_pec']} para 206) nem a autorização de um impeachment (faltam {blc['falta_esquerda_barrar_impeachment']} para 172). O centro ({blc['centro']}) decide o que passa de 308 e de 342.

**A leitura da IA sobre o que isso significa (opinião, confiança média):** o Congresso de 2027 pesa diferente conforme quem ganhar a Presidência. Um governo do Flávio começaria com a direita acima da maioria absoluta nas duas Casas e a poucas dezenas de votos de mudar a Constituição. Um governo do Lula enfrentaria uma direita capaz de derrubar seus vetos, abrir CPIs e barrar suas PECs, e a esquerda sozinha não teria votos para barrar a abertura de um impeachment. Tudo isso supõe a direita votando unida, e partido não vota sempre unido; a análise não diz quem vai ganhar.

**Senado, os fatos e a conta (alto para a conta):** hoje, pelo partido atual, a direita tem {sh3['direita']} dos 81 senadores, o centro {sh3['centro']} e a esquerda {sh3['esquerda']} ({sh3['sem partido']} sem partido). A partir de fevereiro de 2027: direita **{s273['direita']}** (PL {E3['senado_pl']['fev_2027_partido_atual']}), centro {s273['centro']} e esquerda {s273['esquerda']} ({s273['sem partido']} sem partido). Com {ls[49]['direita']}, a direita passa de 41, fica no limite de uma PEC (49) e a **{ls[54]['falta_a_direita']}** dos 54 que condenam um ministro do STF num impeachment (pela conta do Poder360, por senador, 49 e a 5). A esquerda terá {ls[33]['esquerda']}, abaixo dos 33 que bloqueiam uma PEC.

**Conferência com o Poder360 (alto):** a lista de partidos que o Poder360 usou na Câmara em 05/out (classificação da UFPR e da UEM) aplicada às nossas cadeiras dá {R['e7']['camara_pela_lista_do_poder360']['nossa_conta']['2026']['direita']} de direita, {R['e7']['camara_pela_lista_do_poder360']['nossa_conta']['2026']['centro']} de centro e {R['e7']['camara_pela_lista_do_poder360']['nossa_conta']['2026']['esquerda']} de esquerda, exatamente o publicado. A diferença para a nossa conta (265, 124, 124) é **só o PSDB** (11 deputados), que se declara centro-democrático e o Poder360 põe na direita; a esquerda é a mesma. No Senado, o Poder360 (04/out) classificou **cada senador** pela orientação individual (49 de direita, 27 de esquerda, 5 de centro); por partido, a direita soma {ls[49]['direita']}. As duas contas põem a direita no limite da PEC (49). O projeto não refaz a conta senador a senador.

**Governos (alto):** dos 20 decididos no 1º turno, a direita ficou com **{g3[2026]['direita']}** (5 do PL), o centro com {g3[2026]['centro']} e a esquerda com {g3[2026]['esquerda']}; {g3[2026]['em 2o turno']} vão a 2º turno. Em 2022 eram {g3[2022]['direita']}, {g3[2022]['centro']} e {g3[2022]['esquerda']} de 27. Os governos de direita já decididos somam {f1(el3['direita'])}% do eleitorado, os de centro {f1(el3['centro'])}% e os de esquerda {f1(el3['esquerda'])}% ({f1(el3['em 2o turno'])}% em estados de 2º turno). Pelo apoio declarado na eleição presidencial (CNN Brasil), os {apo['Flavio']['governos']} governadores eleitos que apoiam Flávio governarão {f1(apo['Flavio']['pct_eleitorado'])}% do eleitorado, e os {apo['Lula']['governos']} que apoiam Lula, {f1(apo['Lula']['pct_eleitorado'])}%.

**Como o PL chegou a {p3['2026 (PL)']} (alto para a descrição):** dos {p3['2026 (PL)']} eleitos, {o121.get('eleito em 2022 pelo PL', 0)} já tinham sido eleitos pelo PL em 2022, {o121.get('eleito em 2022 por outro partido e foi para o PL', 0)} foram eleitos em 2022 por outro partido e mudaram para o PL antes da eleição ({mig_txt}), {o121.get('disputou deputado federal em 2022 e não se elegeu', 0)} tinham disputado em 2022 sem se eleger, {o121.get('assumiu o mandato depois de 2022 (suplente) e se elegeu pelo PL', 0)} assumiu como suplente e {n_nao} não disputaram a Câmara em 2022: {n_nunca} sem nenhuma candidatura estadual ou federal de 2006 a 2018 (eleição municipal não está nos dados), {o121.get('não disputou a Câmara em 2022: já tinha disputado deputado federal antes', 0)} que já tinham disputado deputado federal antes (alguns ex-deputados) e {o121.get('não disputou a Câmara em 2022: já tinha disputado outro cargo estadual ou federal', 0)} que tinham disputado outro cargo. Dos 98 deputados que o PL tinha na véspera, {d98.get('reeleito deputado pelo PL', 0)} se reelegeram, **{d98.get('disputou senador: eleito', 0)} foram eleitos senadores** ({', '.join(sen_pl)}), {d98.get('disputou governador: eleito', 0)} governador, {d98.get('disputou deputado estadual: eleito', 0)} deputados estaduais, {d98.get('disputou deputado e não se elegeu', 0)} perderam a reeleição e {d98.get('disputou senador: não eleito', 0)} perderam a disputa ao Senado. Os votos nominais do PL para deputado foram de {n(E5['pl_votos_nominais']['2022'])} para {n(E5['pl_votos_nominais']['2026'])}; os dez mais votados do partido somaram {n(E5['pl_top10_votos_2026'])}.

**A leitura da IA (opinião, confiança alta para a direção, média para o tamanho):** em votos para deputado, a direita ganhou {f1(v3[2026]['direita'] - v3[2022]['direita'])} pontos e o centro perdeu {f1(v3[2022]['centro'] - v3[2026]['centro'])}, quase o mesmo tamanho, enquanto a esquerda ficou parada ({f1(v3[2022]['esquerda'])}% → {f1(v3[2026]['esquerda'])}%). Dentro da direita houve uma segunda mudança, maior: o PL ganhou {f1(pl['2026']['pct_votos'] - pl['2022']['pct_votos'])} pontos e a centro-direita perdeu {f1(cv_cd22 - cv_cd26)}. O dado é por partido e não mostra quem trocou de voto, um a um. Em cadeiras, a direita foi de {c3[2022]['direita']} para {c3[2026]['direita']} deputados e de {sh3['direita']} para {s273['direita']} senadores; a consequência prática é que, votando unida, ela passa da maioria absoluta nas duas Casas, derruba veto e fica no limite de uma PEC no Senado. **Campo não é bloco de votação**: a conta é o teto do que cada grupo alcança se votar unido, não uma previsão.

**O que acompanha o crescimento do PL (descrição, não causa; opinião, confiança média):** (1) o partido trouxe deputados de outras siglas antes da eleição e elegeu {n_nao} nomes que não tinham disputado a Câmara em 2022, {n_nunca} deles sem candidatura estadual ou federal anterior; (2) usou a própria bancada para disputar o Senado, e {d98.get('disputou senador: eleito', 0)} deputados viraram senadores; (3) puxadores com votação muito acima da média (Nikolas Ferreira e Lucas Pavanato, cada um com mais de 3 milhões); (4) o voto no PL andou junto com o voto em Flávio para presidente (H8). **O que não dá para separar** é quanto disso veio dos casos da campanha (Banco Master, STF, INSS, condenação de Bolsonaro): faltam medições de opinião perto de cada caso (H6).

---

## Câmara dos Deputados, pelos outros parâmetros (R1, R2, R3)

**Base de 2022:** o arquivo atual do TSE (PL {pl['2022']['cadeiras']}, PT 69). Matérias da época deram PL 99 e PT 68; a diferença é compatível com a troca de sete mandatos decidida pelo STF sobre as sobras (fonte `conjur-sete-deputados`), mas não foi verificada cadeira a cadeira.

**Os fatos (alto):** o PL passou de {pl['2022']['cadeiras']} para {pl['2026']['cadeiras']} deputados ({f1(pl['2022']['pct_votos'])}% → {f1(pl['2026']['pct_votos'])}% dos votos). A federação PT/PCdoB/PV passou de {fedpt[0]} para {fedpt[1]}. Pela R1, a direita foi de {dir_c[2022]} para {dir_c[2026]} cadeiras ({f1(dir_p[2022])}% → {f1(dir_p[2026])}%) e a esquerda de {esq_c[2022]} para {esq_c[2026]}; em votos, a direita ficou em {f1(dir_v[2022])}% → {f1(dir_v[2026])}% e a esquerda em {f1(esq_v[2022])}% → {f1(esq_v[2026])}%. Com os cortes da escala deslocados em meio ponto, a direita vai de {int(s35[2022])} a {int(s35[2026])} (corte 3,5 a 5,5) ou de {int(s45[2022])} a {int(s45[2026])} (corte 4,5 a 6,5), e a esquerda de {int(e35[2022])} a {int(e35[2026])} ou de {int(e45[2022])} a {int(e45[2026])}.

**Pela R2 (voto no plenário):** a bancada que votou majoritariamente contra a orientação do governo (40% ou menos de concordância) foi de {r2c[2022]['oposicao']} para {r2c[2026]['oposicao']} cadeiras (com cortes de 65% e 45%, de {R['a1']['r2_sensibilidade'][2]['oposicao']} para {R['a1']['r2_sensibilidade'][3]['oposicao']}). Essa é a medida que mais se aproxima de "o campo que se opõe ao governo cresceu", e ela cresceu. Duas ressalvas: em 2026 os deputados novos herdam a classe mediana do partido (os de 2022 só entram pelo próprio histórico), e o corte de 70% põe quase todo o centrão como governista.

**A leitura da IA (opinião, confiança média):** o que mudou na Câmara foi principalmente **dentro do campo de direita**, não entre os campos. O PL ganhou {f1(pl['2026']['pct_votos']-pl['2022']['pct_votos'])} pontos de voto enquanto o voto somado dos partidos de direita pela R1 mal mexeu ({f1(dir_v[2026]-dir_v[2022])} ponto). Os votos saíram principalmente de partidos do mesmo campo ({perdas}) e de legendas extintas ou fundidas, e a esquerda pela R1 teve {abs(esq_c[2026]-esq_c[2022])} cadeiras a menos, por causa de uma queda grande do PDT, enquanto a federação do PT cresceu. A frase "a esquerda saiu bastante da Câmara" **não é sustentada** por esses dados, e a frase "a direita dominou a Câmara" só vale no sentido de que ela já era maioria em 2018 e 2022: o que os dados mostram é o PL indo de {pl['2022']['cadeiras']} para {pl['2026']['cadeiras']} cadeiras, a bancada de oposição pela R2 indo de {r2c[2022]['oposicao']} para {r2c[2026]['oposicao']} e o centro pela R1 indo de {int(c46[(c46.ano == 2022) & (c46.campo == 'centro')].cadeiras.iloc[0])} para {int(c46[(c46.ano == 2026) & (c46.campo == 'centro')].cadeiras.iloc[0])}.

**O que acompanha o tamanho do PL em cadeiras (descrição, não causa; opinião, confiança média a alta):** três coisas que se medem. (1) **Concentração:** {f1(pl['2026']['pct_votos'])}% dos votos e {pl['2026']['cadeiras']} cadeiras. (2) **Eficiência do sistema:** o bônus de cadeiras da direita sobre os votos foi de {sg(bonus[2026])} ponto em 2026, contra {sg(bonus[2022])} em 2022 e {sg(bonus[2018])} em 2018. (3) **Puxadores:** Nikolas Ferreira fez {n(nik.votos)} votos ({f1(nik.pct_da_lista)}% da lista do PL em Minas) e, sem os votos dele, a lista teria {int(nik.cadeiras_a_mais_pelo_candidato)} cadeiras a menos (uma delas a dele); Lucas Pavanato, em São Paulo, {n(pav.votos)} votos e {int(pav.cadeiras_a_mais_pelo_candidato)} cadeiras a mais para a lista. A regra de sobras aplicada em 2026 (que reproduz as 513 cadeiras) **não** favoreceu o PL: com todos os partidos disputando as sobras, o PL teria {R['a5']['sobras']['ganhadores_perdedores_todos_partidos_10pct']['PL']} cadeiras a mais.

**Renovação e incumbentes (opinião, confiança média):** {f1(R['a4']['pct_eleitos_que_nao_estavam_em_exercicio'])}% dos eleitos não estavam na Câmara na véspera ({R['a1']['origem_cadeiras_2026_total']['reeleito, mesmo partido da vespera']} se reelegeram pelo mesmo partido). Dos eleitos de 2022, {f1(rl[(2022,'todos')].pct_reeleito_entre_todos)}% se reelegeram, contra {f1(rl[(2018,'todos')].pct_reeleito_entre_todos)}% dos eleitos de 2018 na eleição de 2022. Por campo (R1), a esquerda foi de {f1(rl[(2018,'esquerda')].pct_reeleito_entre_todos)}% para {f1(rl[(2022,'esquerda')].pct_reeleito_entre_todos)}% e a direita de {f1(rl[(2018,'direita')].pct_reeleito_entre_todos)}% para {f1(rl[(2022,'direita')].pct_reeleito_entre_todos)}%. Isso não combina com uma onda geral contra quem está no cargo (H3). Dos reeleitos, {f1(R['a4']['pct_reeleitos_com_queda_de_votos'])}% tiveram menos votos que em 2022 (mediana da razão 2026 sobre 2022: {f2(R['a4']['mediana_razao_votos_reeleitos_2026_sobre_2022'])}). André Janones foi reeleito com 78.780 votos contra 238.967 em 2022, a segunda maior queda proporcional entre os reeleitos; a lista das maiores quedas e das maiores altas tem deputados de vários partidos (`resultados/a4_reeleitos_maiores_quedas_2022_2026.csv` e `..._altas_...`).

**O caso do voto no plenário (opinião, confiança baixa):** entre quem disputou a reeleição, votar a favor da PEC da Blindagem (16/09/2025) não teve relação com ser reeleito: {f1(dd.iloc[0].pct_eleitos_entre_os_que_disputaram_sim)}% contra {f1(dd.iloc[0].pct_eleitos_entre_os_que_disputaram_nao)}%, e {sg(v1.coef_sim*100)} ponto (IC95 {sg(v1.ic95_baixo*100)} a {sg(v1.ic95_alto*100)}) dentro do mesmo partido e estado. Na votação do aumento do número de deputados, a diferença foi de {sg(v4.coef_sim*100)} pontos (IC95 {sg(v4.ic95_baixo*100)} a {sg(v4.ic95_alto*100)}), sem significância depois da correção. O placebo não pôde ser estimado ({int(d3[d3.votacao.str.startswith('P') & (d3.desfecho == 'eleito em 2026')].n.iloc[0])} deputados com variação dentro do partido e do estado). **Isso não prova que os casos não pesaram**: são duas votações, e o voto individual no plenário não mede a exposição de cada deputado a nenhum dos casos.

## Senado Federal

**Os fatos (alto):** o PL elegeu {ep['PL']} das 54 vagas; MDB {ep['MDB']}, PT {ep['PT']}; pela R1, a direita elegeu {se['2026']['direita']} (contra {se['2018']['direita']} em 2018), o centro {se['2026']['centro']} ({se['2018']['centro']}) e a esquerda {se['2026']['esquerda']} ({se['2018']['esquerda']}). Em fevereiro de 2027 o PL terá {comp['por_partido']['PL']} das {comp['total']} cadeiras. A esquerda ganhou vaga em {', '.join(R['a2']['ufs_onde_a_esquerda_ganhou_vaga'])} e perdeu em {', '.join(R['a2']['ufs_onde_a_esquerda_perdeu_vaga'])}, em relação a 2018.

**Os limiares (alto para a conta, baixo para o significado):** a R1 põe {lim['direita_r1']} dos 81 senadores na direita, acima de 41, de 49 e de 54, mas essa direita inclui MDB ({comp['por_partido']['MDB']}), PSD ({comp['por_partido']['PSD']}) e PSDB ({comp['por_partido']['PSDB']}). O PL sozinho tem {lim['PL']}, abaixo de 41. Campo pela R1 não é bloco de votação e a conta não diz o que o Senado fará.

**O tema STF (opinião, confiança baixa a média):** dos 54 eleitos, {d8['eleitos_por_posicao']['a favor']} constavam como favoráveis ao impeachment de ministros do STF na lista da Gazeta do Povo, {d8['eleitos_por_posicao'].get('contra', 0)} como contrários, {d8['eleitos_por_posicao'].get('sem posicao', 0)} sem posição ou não localizados e {d8['eleitos_por_posicao'].get('outra (neutro, reforma ou outra)', 0)} em outra posição; {d8['eleitos_por_posicao'].get('fora da lista da Gazeta', 0)} não constavam na lista. **Todos** os {d8['eleitos_por_posicao']['a favor']} favoráveis estão no campo de direita pela R1. Isso mostra que a posição era comum entre os eleitos; **não** mostra que a posição causou o voto (os favoráveis também eram, em geral, de partidos que já ganhavam nesses estados). A lista tem fonte única, e o Senado de 2027 não pode ser contado por ela porque os 27 senadores com mandato até 2031 não entram.

**A leitura da IA (opinião, confiança média):** o Senado de 2026 foi o cargo em que o voto acompanhou mais o voto em Bolsonaro para presidente (Jair pelo PSL em 2018 e pelo PL em 2022, Flávio pelo PL em 2026; correlação municipal de {f2(A(2018,'senador'))} em 2018 para {f2(A(2026,'senador'))} em 2026). O dado mede **correlação** entre municípios, e ela subiu. "Arrasto do candidato presidencial" é a leitura mais simples, não a única: a mesma correlação apareceria se os eleitores escolhessem os cargos pelo mesmo critério, sem que um puxasse o outro. O que ela não é, por si, é mudança de opinião dos eleitores de cada estado, que o dado não mede.

## Governos estaduais

**Os fatos (alto):** foram decididos {int(gov.loc[2026,'decididos'])} governos no 1º turno e {int(gov.loc[2026,'em_disputa'])} vão a 2º turno. Dos 20, {int(gov.loc[2026,'decididos_direita'])} são de partidos de direita pela R1 e {int(gov.loc[2026,'decididos_esquerda'])} de esquerda; em 2022 eram {int(gov.loc[2022,'decididos_direita'])} de 27 e {int(gov.loc[2022,'decididos_esquerda'])}, e em 2018 {int(gov.loc[2018,'decididos_direita'])} de 27 e {int(gov.loc[2018,'decididos_esquerda'])}. {R['a3']['decididos_2026_com_o_mesmo_governador_de_2022']} dos 20 são o mesmo governador de 2022 e {R['a3']['decididos_2026_trocaram_de_campo_r1']} estados trocaram de campo pela R1 (ambos eram de PSB e passaram a PSD ou PP). O voto de direita para governador subiu {f1(sw3.swing_direita_medio_ponderado_pp)} ponto contra {f1(sw3p.swing_direita_medio_ponderado_pp)} em 2018→2022. Apoio declarado, pela CNN Brasil (R3): {R['a3']['apoio_declarado_2026']['Flavio']} a Flávio, {R['a3']['apoio_declarado_2026']['Lula']} a Lula, {R['a3']['apoio_declarado_2026']['Caiado']} a Caiado e {R['a3']['apoio_declarado_2026']['neutro']} sem apoio.

**A leitura da IA (opinião, confiança média):** nos governos não houve troca de lado; houve **continuidade com mais PL**. Pela R1, a direita já tinha a maioria dos governos em 2018 e 2022; pela autodeclaração em três grupos (direita com a centro-direita), ela tinha 7 de 27 em 2018 e 11 de 27 em 2022, e ficou com 10 dos 20 decididos agora. O PL passou a ter 5 dos 20 decididos (2 em 2022). Dos 8 governadores de 2022 que tentaram continuar no cargo, 7 venceram ou foram ao 2º turno.

## As pesquisas

**Os fatos (alto para a conta, médio para a cobertura):** foram analisadas {c2['pesquisas_analisadas']} pesquisas de Datafolha e Quaest da véspera, em {c4['margem_subestimada']['disputas']} disputas de governador. O primeiro colocado (o eleito, ou o primeiro dos 7 estados que vão a 2º turno) apareceu abaixo da urna em {R['c4']['vencedor_subestimado']['com_vencedor_abaixo_da_urna']} delas; a margem entre os dois primeiros foi menor na pesquisa que na urna em {c4['margem_subestimada']['com_margem_menor_que_a_urna']}; erro médio do vencedor de {f1(abs(c2['erro_medio_com_sinal_vencedor_pp']))} ponto abaixo; {c2['fora_da_margem']['proporcao']} das {c2['fora_da_margem']['total']} ficaram fora da margem declarada no vencedor. Em {c4['margem_subestimada']['disputas_com_maioria_das_pesquisas_apertadas_demais']} das {c4['margem_subestimada']['disputas']} disputas a maioria das pesquisas mostrou corrida mais apertada que a urna (p = {f2(c4['margem_subestimada']['p_binomial_bicaudal_disputas'])}, teste do sinal).

**O erro tem direção por campo? (opinião, confiança média):** nas disputas em que um candidato era de Flávio e o outro de Lula (R3, {c4['r3_flavio']['disputas']} disputas) a pesquisa subestimou o lado de Flávio em {c4['r3_flavio']['disputas_em_que_subestimou']} (p = {f2(c4['r3_flavio']['p_binomial_bicaudal'])}); pela R1 ({c4['r1_direita']['disputas']} disputas), em {c4['r1_direita']['disputas_em_que_subestimou']} (p = {f2(c4['r1_direita']['p_binomial_bicaudal'])}). No teste exploratório, definido depois de ver os resultados (um dos dois primeiros alinhado a Flávio, o outro qualquer), foram {c4['exploratoria_flavio_contra_qualquer_outro']['disputas_em_que_subestimou']} de {c4['exploratoria_flavio_contra_qualquer_outro']['disputas']} (p = {f2(c4['exploratoria_flavio_contra_qualquer_outro']['p_binomial_bicaudal'])}); a média foi de {sg(c4['exploratoria_flavio_contra_qualquer_outro']['media_pp'])} ponto de subestimação do lado de Flávio e a mediana de {sg(c4['exploratoria_flavio_contra_qualquer_outro']['mediana_pp'])}, ou seja, a média é puxada por cinco disputas ({ex_pos}), em que o candidato do PL terminou mais à frente do que as pesquisas mostravam, enquanto em {ex_neg} pontos as pesquisas deram ao lado de Flávio mais do que a urna deu. Com 6 a 13 disputas, esses testes só acusariam desvios grandes e constantes; **ausência de direção neste teste não é prova de ausência de erro por campo**. **Nenhum teste mostra erro numa direção de campo.** O que os dados sustentam é outro padrão: as pesquisas mostraram corridas mais apertadas do que as urnas deram, para quem terminou em primeiro, **seja qual fosse o campo**. Os maiores erros no vencedor foram no Rio de Janeiro (Datafolha {f1(abs(rj_d))} pontos abaixo e Quaest {f1(abs(rj_q))}), onde o candidato do PL terminou em primeiro, com mais votos que o previsto, e vai ao 2º turno, e no Amapá (Quaest {f1(abs(ap_q))} pontos), onde nenhum dos dois finalistas é do PL.

**O que isso não permite dizer:** não há "erro sistemático" no sentido do pré-registro, porque faltam duas coisas: a comparação com 2022 e a separação entre mudança de última hora e erro da pesquisa (não foram coletadas as pesquisas anteriores). O padrão pode ser mudança de última hora, abstenção diferencial ou decisão tardia de quem estava indeciso; os dados não separam. Também só entraram dois institutos.

## O que o eleitor sinalizou

**A leitura da IA (opinião, confiança baixa a média):** juntando H1, H2 e H3: (a) o voto de direita pela R1 ficou estável na Câmara ({f1(dir_v[2022])}% → {f1(dir_v[2026])}%), (b) os deputados que tentaram continuar se reelegeram mais que na eleição anterior, e (c) a esquerda pela R1 manteve {f1(esq_v[2026])}% dos votos. **Esse conjunto não combina com "o eleitor quis mudar tudo".** Combina com um eleitorado que manteve a divisão de 2022, concentrou parte do voto de direita no PL (provavelmente puxado pelo candidato presidencial, H8) e pouco mexeu na abstenção ({f1(abst.loc[2022,'abstencao_pct'])}% → {f1(abst.loc[2026,'abstencao_pct'])}%; com o comparecimento de 2022, o voto de direita seria {f2(cf['direita_pct_com_comparecimento_de_2022'])}%, contra {f2(cf['direita_pct_real_2026'])}%). O perfil do município (religião, renda, cor, idade, Bolsa Família) explica pouco da variação do voto: a UF sozinha explica {100*r2m['so_uf']:.0f}%, e o perfil soma {f1(100*r2m['ganho_do_perfil'])} ponto. **O que não dá para dizer** é como o eleitor se enxerga (autoposicionamento) ou se os casos (Master, STF, INSS, condenação de Bolsonaro) pesaram: não há série de opinião suficiente neste projeto.

## O que o projeto não consegue dizer

1. Em quem cada pessoa votou: tudo aqui é entre municípios.
2. Se os casos (Master e ministros do STF, condenação de Bolsonaro, INSS, tarifaço, PEC da Blindagem) mudaram votos: as séries de opinião capturadas têm menos de duas medições do mesmo instituto antes e depois dos eventos.
3. O efeito de emendas parlamentares e de gasto de campanha: não foram analisados (a prestação de contas final ainda não existe).
4. Se as pesquisas erraram em 2026 mais que em 2022 e se a causa foi mudança de última hora: faltam as pesquisas anteriores e as de 2022. Pesquisas de Senado não foram coletadas.
5. O 2º turno: os 7 estados em disputa estão como "em disputa".
6. Se a classificação de campo de especialistas de 2021 ainda descreve os partidos de 2026: ela põe o PL na posição do antigo PR, e partidos novos ou fundidos herdam a média das origens.
""")
    (RAIZ / "docs" / "LEITURA_DA_IA.md").write_text("\n".join(t), encoding="utf-8")
    print("ok veredito")


if __name__ == "__main__":
    main()
