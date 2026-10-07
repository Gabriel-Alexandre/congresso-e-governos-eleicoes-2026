"""Coleta do Censo 2022 e do PIB municipal no SIDRA/IBGE, por UF, com manifesto sha256.

Cada resposta bruta fica em dados/brutos/ibge/<tabela>-<uf>.json e entra no dados/MANIFESTO.json.
Usa curl por causa de uma falha intermitente do urllib com o servidor do IBGE.
Tabelas (conferidas nos metadados do IBGE em 07/out/2026):
  9923  populacao por situacao do domicilio (urbana, rural)
  9606  populacao por cor ou raca
  9514  populacao por faixa de idade
  10061 pessoas de 18+ por nivel de instrucao (total e superior completo)
  10198 pessoas de 15+ por religiao
  5938  PIB municipal 2022 (PIB) e 2021 (valor adicionado da agropecuaria e total: o IBGE ainda nao publicou a divisao setorial de 2022 e 2023, aparece como "...")
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados" / "brutos" / "ibge"
MANIFESTO = RAIZ / "dados" / "MANIFESTO_IBGE.json"
UF_COD = {
    "ac": 12, "al": 27, "am": 13, "ap": 16, "ba": 29, "ce": 23, "df": 53, "es": 32, "go": 52, "ma": 21,
    "mg": 31, "ms": 50, "mt": 51, "pa": 15, "pb": 25, "pe": 26, "pi": 22, "pr": 41, "rj": 33, "rn": 24,
    "ro": 11, "rr": 14, "rs": 43, "sc": 42, "se": 28, "sp": 35, "to": 17,
}
IDADE_60 = "93095,93096,93097,93098,49108,49109,60040,60041,6653"
IDADE_MAIS = "100362," + IDADE_60
TABELAS = {
    "9923": "t/9923/n6/in%20n3%20{u}/v/93/p/2022/c1/all",
    "9606": "t/9606/n6/in%20n3%20{u}/v/93/p/2022/c86/all/c2/6794/c287/100362",
    "9514": "t/9514/n6/in%20n3%20{u}/v/93/p/2022/c2/6794/c286/113635/c287/" + IDADE_MAIS,
    "10061": "t/10061/n6/in%20n3%20{u}/v/2667/p/2022/c1568/120704,99713/c58/95253/c2/6794/c86/95251",
    "10198": "t/10198/n6/in%20n3%20{u}/v/950/p/2022/c133/all/c58/95253/c59/93024",
    "5938": "t/5938/n6/in%20n3%20{u}/v/37/p/2022",
    "5938v": "t/5938/n6/in%20n3%20{u}/v/513,498/p/2021",
}


def carregar() -> dict:
    return json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {"arquivos": {}}


def main() -> None:
    m = carregar()
    BRUTOS.mkdir(parents=True, exist_ok=True)
    for tab, caminho in TABELAS.items():
        for uf, cod in UF_COD.items():
            destino = BRUTOS / f"{tab}-{uf}.json"
            chave = str(destino.relative_to(RAIZ)).replace("\\", "/")
            if chave in m["arquivos"] and destino.exists():
                continue
            url = "https://apisidra.ibge.gov.br/values/" + caminho.format(u=cod)
            for tentativa in range(5):
                r = subprocess.run(["curl", "-s", "-m", "120", url], capture_output=True)
                if r.returncode == 0 and r.stdout.startswith(b"["):
                    break
                time.sleep(4 * (tentativa + 1))
            else:
                raise RuntimeError(f"falhou {url}")
            destino.write_bytes(r.stdout)
            m["arquivos"][chave] = {
                "url": url,
                "bytes": len(r.stdout),
                "sha256": hashlib.sha256(r.stdout).hexdigest(),
                "last_modified": None,
                "baixado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            MANIFESTO.write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            time.sleep(0.5)
        print("tabela", tab, "ok", flush=True)


if __name__ == "__main__":
    main()
