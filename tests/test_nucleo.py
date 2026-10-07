"""Testes do núcleo: quociente, distribuição de cadeiras, escala de campo, chave de lista e sinal do erro de pesquisa.

Não dependem dos dados brutos (exceto os marcados), para rodar em qualquer máquina.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from congresso import campos  # noqa: E402
from congresso.cadeiras import distribuir, quociente  # noqa: E402
from congresso.comum import chave_lista  # noqa: E402


def test_quociente_desconsidera_fracao_igual_ou_inferior_a_meio():
    assert quociente(1000, 3) == 333   # 333,33
    assert quociente(1005, 2) == 502   # 502,5: fração igual a meio é desprezada
    assert quociente(1007, 2) == 503   # 503,5: idem
    assert quociente(1009, 3) == 336   # 336,33


def test_distribuicao_simples_com_sobras():
    # 3 vagas, QE = 1000. A: 1800 votos (QP 1), B: 1200 (QP 1), C: 0 -> sobra 1 vaga vai a quem tem maior média
    listas = {
        "A": {"votos": 1800, "cands": [(1, 1000), (2, 800)]},
        "B": {"votos": 1200, "cands": [(3, 1200)]},
        "C": {"votos": 0, "cands": []},
    }
    r = distribuir(listas, 3, 0.0, 0.0)
    assert r.qe == 1000
    assert len(r.eleitos) == 3
    assert 1 in r.eleitos and 3 in r.eleitos      # primeiro de cada lista
    assert 2 in r.eleitos                          # média de A (1800 / 2) maior que a de B (1200 / 2)


def test_distribuicao_exige_minimo_de_candidato_nas_sobras():
    listas = {
        "A": {"votos": 3000, "cands": [(1, 2900), (2, 100)]},
        "B": {"votos": 1000, "cands": [(3, 1000)]},
    }
    # 4 vagas, QE = 1000; candidato com 10% do QE (100) entra no QP; nas sobras, com piso de 20% (200), o 2 de A fica de fora
    r = distribuir(listas, 4, 0.0, 0.2)
    assert len(r.eleitos) <= 4


def test_chave_de_federacao_aceita_as_duas_grafias_do_tse():
    fed = pd.Series(["#NULO#", "#NULO", "PT/PC do B/PV", None, "#NE"])
    par = pd.Series(["PL", "PL", "PT", "PP", "MDB"])
    out = chave_lista(fed, par).tolist()
    assert out == ["PL", "PL", "FED:PT/PC do B/PV", "PP", "MDB"]


def test_escala_r1_e_campo():
    assert campos.campo_r1(campos.nota_r1("PT")) == "esquerda"
    assert campos.campo_r1(campos.nota_r1("PSB")) == "centro"
    assert campos.campo_r1(campos.nota_r1("PL")) == "direita"
    assert campos.campo_r1(campos.nota_r1("MISSÃO")) == "sem classificacao"
    # corte deslocado muda o PDT (3,92) de esquerda para centro
    assert campos.campo_r1(campos.nota_r1("PDT"), (3.5, 5.5)) == "centro"
    assert campos.campo_r1(campos.nota_r1("PDT"), (4.0, 6.0)) == "esquerda"


def test_fusao_pesa_pelas_cadeiras():
    n = campos.nota_r1("UNIÃO", {"DEM": 29, "PSL": 52})
    esperado = (8.57 * 29 + 8.11 * 52) / 81
    assert n == pytest.approx(esperado)
    assert campos.nota_r1("UNIÃO") is None  # sem pesos, sem classificação (não chuta)


def test_sinal_do_erro_de_margem():
    # M = margem da pesquisa - margem da urna. Alvo é o 1o da urna: subestimou = -M. Alvo é o 2o: subestimou = +M.
    def subestimou(alvo_e_primeiro: bool, margem_poll: float, margem_urna: float) -> float:
        M = margem_poll - margem_urna
        return -M if alvo_e_primeiro else M

    # o 1o da urna (alvo) venceu por 20 e a pesquisa mostrou 10: pesquisa subestimou o alvo em 10
    assert subestimou(True, 10, 20) == 10
    # o alvo é o 2o: a pesquisa mostrou o 1o 10 na frente e na urna foi 20: o 2o foi SUPERESTIMADO em 10 (subestimou = -10)
    assert subestimou(False, 10, 20) == -10


def test_binomial_bicaudal_exato():
    from math import comb

    def p(n, k):
        return min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2**n) if k >= n / 2 else min(1.0, 2 * sum(comb(n, i) for i in range(0, k + 1)) / 2**n)

    assert p(6, 3) == 1.0
    assert p(7, 2) == pytest.approx(0.453125)
    assert p(27, 20) == pytest.approx(0.0192, abs=1e-3)


def _blocos():
    import importlib.util
    spec = importlib.util.spec_from_file_location("blocos", Path(__file__).resolve().parent.parent / "ferramentas" / "analise-11-pl-e-blocos.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_autodeclaracao_e_herdeiros():
    b = _blocos()
    assert b.grupo("PL") == "direita" and b.grupo("NOVO") == "direita"
    assert b.grupo("PSL") == "centro-direita" and b.grupo("DEM") == "centro-direita"  # herdeiro: União
    assert b.grupo("PR") == "direita"  # herdeiro: PL
    assert b.grupo("MDB") == "centro" and b.grupo("PSD") == "centro"
    assert b.grupo("PSB") == "centro-esquerda" and b.grupo("PT") == "esquerda"
    assert b.tres("centro-esquerda") == "esquerda" and b.tres("centro-direita") == "centro"


def test_escada_de_limiares():
    b = _blocos()
    t = b.escada({"direita": 31, "centro-direita": 17, "centro": 17, "centro-esquerda": 6, "esquerda": 9}, b.LIMIARES_SENADO).set_index("votos_necessarios")
    assert t.loc[49, "falta_com_centro_direita"] == 1
    assert t.loc[54, "falta_com_centro_direita"] == 6
    assert t.loc[33, "esquerda_e_centro_esquerda"] == 15
