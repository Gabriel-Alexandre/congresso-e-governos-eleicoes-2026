"""R2 (comportamento no plenario) e a base de deputados em exercicio em 30/09/2026.

Entradas: dados/brutos/camara (votacoesVotos, votacoesOrientacoes, votacoes, deputados.csv), 2023 a 2026.
Saidas: dados/derivados/plenario_deputados.parquet, dados/derivados/votos_d3.parquet,
        resultados/p0_plenario_resumo.csv
Criterio (docs/PRE_REGISTRO.md, secao 1, R2): % dos votos Sim ou Nao iguais a orientacao do Governo nas votacoes
em que o Governo orientou Sim ou Nao; deputado com menos de 50 votacoes validas = sem classificacao.
"Em exercicio em 30/09/2026" = votou em ao menos uma votacao nominal entre 01/07 e 30/09/2026 (emenda 1 do pre-registro).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from congresso.comum import DER, RES, ler_camara  # noqa: E402

ANOS = (2023, 2024, 2025, 2026)
D3 = {"V1": "2270800-135", "V4": "2383019-91", "P": "2487436-169"}


def main() -> None:
    RES.mkdir(exist_ok=True)
    votos = pd.concat([ler_camara("votacoesVotos", a) for a in ANOS], ignore_index=True)
    orient = pd.concat([ler_camara("votacoesOrientacoes", a) for a in ANOS], ignore_index=True)
    votos["data"] = pd.to_datetime(votos["dataHoraVoto"])
    votos = votos.rename(columns={"deputado_id": "id", "deputado_nome": "nome", "deputado_siglaPartido": "partido", "deputado_siglaUf": "uf"})

    # orientacao do governo: Sim ou Nao
    gov = orient[(orient["siglaBancada"] == "Governo") & (orient["orientacao"].isin(["Sim", "Não"]))]
    gov = gov.drop_duplicates("idVotacao")[["idVotacao", "orientacao"]].rename(columns={"orientacao": "gov"})
    m = votos[votos["voto"].isin(["Sim", "Não"])].merge(gov, on="idVotacao")
    m["igual"] = (m["voto"] == m["gov"]).astype(int)
    r2 = m.groupby("id").agg(n_validos=("igual", "size"), taxa=("igual", "mean")).reset_index()

    # exercicio em 30/09/2026 e partido no ultimo voto ate essa data
    ate = votos[votos["data"] <= "2026-09-30 23:59:59"].sort_values("data")
    ult = ate.groupby("id").tail(1)[["id", "nome", "uf", "partido", "data"]].rename(columns={"data": "ultimo_voto", "partido": "partido_vespera"})
    exerc = votos[(votos["data"] >= "2026-07-01") & (votos["data"] <= "2026-09-30 23:59:59")]["id"].unique()
    ult["em_exercicio_30_09"] = ult["id"].isin(exerc)

    # partido mais frequente nos votos de 2023 a 2026 (para classificar o deputado pelo partido de maior parte do mandato)
    pm = votos.groupby(["id", "partido"]).size().reset_index(name="n").sort_values(["id", "n"]).groupby("id").tail(1)[["id", "partido"]].rename(columns={"partido": "partido_principal"})
    base = ult.merge(r2, on="id", how="left").merge(pm, on="id", how="left")
    base["n_validos"] = base["n_validos"].fillna(0).astype(int)
    base["classe_r2"] = pd.cut(base["taxa"], bins=[-0.01, 0.40, 0.70, 1.01], labels=["oposicao", "independente", "governista"]).astype(str)
    base.loc[base["n_validos"] < 50, "classe_r2"] = "sem classificacao"

    # chave de ligacao com o TSE: nome civil + nascimento
    dep = pd.read_csv(Path(DER).parent / "brutos" / "camara" / "deputados.csv", sep=";", dtype=str, encoding="utf-8-sig", engine="python")
    dep["id"] = dep["uri"].str.extract(r"/deputados/(\d+)$")[0]
    base = base.merge(dep[["id", "nomeCivil", "dataNascimento", "siglaSexo"]], on="id", how="left")
    base.to_parquet(DER / "plenario_deputados.parquet", index=False)

    # votos das votacoes do D3
    d3 = votos[votos["idVotacao"].isin(D3.values())][["idVotacao", "id", "voto", "partido", "uf"]]
    d3.to_parquet(DER / "votos_d3.parquet", index=False)

    resumo = pd.DataFrame(
        {
            "medida": ["votos nominais lidos", "votacoes com orientacao Sim/Nao do Governo", "deputados com ao menos 1 voto", "em exercicio em 30/09/2026", "com R2 (50+ votacoes validas)"],
            "valor": [len(votos), gov["idVotacao"].nunique(), base["id"].nunique(), int(base["em_exercicio_30_09"].sum()), int((base["n_validos"] >= 50).sum())],
        }
    )
    resumo.to_csv(RES / "p0_plenario_resumo.csv", index=False)
    print(resumo.to_string(index=False))
    print(base[base.em_exercicio_30_09].classe_r2.value_counts())
    for k, v in D3.items():
        x = d3[d3.idVotacao == v].voto.value_counts().to_dict()
        print(k, v, x)


if __name__ == "__main__":
    main()
