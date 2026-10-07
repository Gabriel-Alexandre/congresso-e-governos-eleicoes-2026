"""Coleta de fontes com manifesto sha256.

Uso: python ferramentas/coletar.py <grupo> [<grupo> ...]
Grupos: tse-principal, tse-partido, tse-serie, oficial-2026, camara, senado

Cada arquivo baixado entra em dados/MANIFESTO.json com url, bytes, sha256, Last-Modified e data da coleta.
O bruto fica em dados/brutos/ (fora do git). Teto de requisicoes: uma por vez, com pausa.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados" / "brutos"
MANIFESTO = RAIZ / "dados" / "MANIFESTO.json"
CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
OFICIAL = "https://resultados.tse.jus.br/oficial/ele2026/6259/dados"
UFS = "ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to".split()
UA = {"User-Agent": "congresso-e-governos-eleicoes-2026 (pesquisa aberta; contato: github Gabriel-Alexandre)"}


def carregar() -> dict:
    if MANIFESTO.exists():
        return json.loads(MANIFESTO.read_text(encoding="utf-8"))
    return {"arquivos": {}}


def salvar(m: dict) -> None:
    MANIFESTO.write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def baixar(url: str, destino: Path, m: dict, pausa: float = 0.4) -> None:
    chave = str(destino.relative_to(RAIZ)).replace("\\", "/")
    if chave in m["arquivos"] and destino.exists():
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    for tentativa in range(5):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                h = hashlib.sha256()
                n = 0
                with open(destino, "wb") as f:
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
                        h.update(chunk)
                        n += len(chunk)
                m["arquivos"][chave] = {
                    "url": url,
                    "bytes": n,
                    "sha256": h.hexdigest(),
                    "last_modified": r.headers.get("Last-Modified"),
                    "baixado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
            salvar(m)
            time.sleep(pausa)
            return
        except Exception as e:  # noqa: BLE001
            espera = 5 * (tentativa + 1)
            print(f"  falhou {url}: {e}; espera {espera}s", flush=True)
            time.sleep(espera)
    raise RuntimeError(f"nao baixou {url}")


def tse(anos, kinds):
    m = carregar()
    for a in anos:
        for k in kinds:
            if k.startswith("pesquisa"):
                url = f"{CDN}/pesquisa_eleitoral/{k}_{a}.zip"
                d = BRUTOS / "tse" / f"{k}_{a}.zip"
            else:
                url = f"{CDN}/{k}/{k}_{a}.zip"
                d = BRUTOS / "tse" / f"{k}_{a}.zip"
            print("baixando", url, flush=True)
            try:
                baixar(url, d, m)
            except RuntimeError as e:
                print(" ERRO", e, flush=True)


def oficial_2026():
    m = carregar()
    for u in UFS:
        for c in (6, 3, 5):
            url = f"{OFICIAL}/{u}/{u}-c{c:04d}-e006259-u.json"
            baixar(url, BRUTOS / "oficial2026" / f"{u}-c{c:04d}.json", m, pausa=0.3)
    print("oficial 2026 ok", flush=True)


def camara():
    m = carregar()
    base = "https://dadosabertos.camara.leg.br/arquivos"
    for ano in (2023, 2024, 2025, 2026):
        for nome in ("votacoesVotos", "votacoesOrientacoes", "votacoes", "votacoesObjetos"):
            baixar(f"{base}/{nome}/csv/{nome}-{ano}.csv", BRUTOS / "camara" / f"{nome}-{ano}.csv", m)
    baixar(f"{base}/deputados/csv/deputados.csv", BRUTOS / "camara" / "deputados.csv", m)
    for leg in (55, 56, 57):
        baixar(
            f"https://dadosabertos.camara.leg.br/api/v2/deputados?idLegislatura={leg}&itens=1000&formato=json",
            BRUTOS / "camara" / f"deputados-leg{leg}.json",
            m,
        )
    print("camara ok", flush=True)


def senado():
    m = carregar()
    baixar("https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json", BRUTOS / "senado" / "atual.json", m)
    print("senado ok", flush=True)


def bolsa_familia():
    m = carregar()
    baixar("https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/novo-bolsa-familia/202608_NovoBolsaFamilia.zip", BRUTOS / "mds" / "202608_NovoBolsaFamilia.zip", m)
    print("bolsa familia ok", flush=True)


GRUPOS = {
    "bolsa-familia": bolsa_familia,
    "tse-principal": lambda: tse(
        (2026, 2022, 2018),
        ("votacao_candidato_munzona", "detalhe_votacao_munzona", "consulta_cand", "pesquisa_eleitoral", "pesquisa_contratante"),
    ),
    "tse-partido": lambda: tse((2026, 2022, 2018, 2014, 2010, 2006), ("votacao_partido_munzona",)),
    "tse-serie": lambda: tse((2014, 2010, 2006), ("votacao_candidato_munzona", "detalhe_votacao_munzona", "consulta_cand")),
    "oficial-2026": oficial_2026,
    "camara": camara,
    "senado": senado,
}

if __name__ == "__main__":
    for g in sys.argv[1:]:
        GRUPOS[g]()
