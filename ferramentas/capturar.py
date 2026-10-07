"""Captura de fontes da imprensa: guarda o HTML, o sha256 e o trecho copiado em dados/CAPTURAS.csv.

Uso: python ferramentas/capturar.py            (captura tudo de FONTES abaixo que ainda nao foi capturado)

Cada fonte tem um id, a URL e uma ou mais expressoes que o texto da pagina precisa conter. O trecho gravado e a
frase da pagina que contem a expressao (copiada, nao parafraseada). Se a expressao nao aparecer, a linha sai com
status 'trecho_nao_encontrado' e a fonte NAO pode ser usada no relatorio.
"""
from __future__ import annotations

import csv
import hashlib
import html
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "dados" / "brutos" / "capturas"
CSV = RAIZ / "dados" / "CAPTURAS.csv"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

# id, url, [expressoes], assunto
FONTES = [
    ("opovo-pesquisas-governador", "https://www.opovo.com.br/noticias/politica/eleicoes/2026/10/04/resultados-das-pesquisas-datafolha-e-quaest-para-governador.html", ["Quaest Acre", "Datafolha Minas Gerais"], "pesquisas Datafolha e Quaest para governador, todos os estados"),
    ("gazeta-pesquisas-sp", "https://gazetadopovo.com.br/eleicoes/2026/sao-paulo-2026/quais-pesquisas-acertaram-e-erraram-para-governador-de-sao-paulo", ["62,65%", "AtlasIntel"], "pesquisas de governador de SP contra a urna"),
    ("metropoles-janones", "https://www.metropoles.com/minas-gerais/apesar-de-reeleito-janones-perdeu-mais-de-160-mil-votos-em-quatro-anos", ["Janones"], "Janones reeleito com queda de votos"),
    ("poder360-marina", "https://www.poder360.com.br/poder-eleicoes/marina-silva-diz-que-nao-sera-candidata-a-deputada-federal/", ["deputada federal"], "Marina Silva nao disputaria a Camara"),
    ("radio-senado-bancada-pl", "https://www12.senado.leg.br/radio/1/noticia/2026/10/05/pl-tera-a-maior-bancada-da-camara-dos-deputados", ["PL"], "bancada do PL na Camara"),
    ("cnn-camara-reeleicao", "https://www.cnnbrasil.com.br/eleicoes/eleicoes-2026-camara-consegue-reeleger-mais-da-metade-dos-deputados/", ["reeleger", "deputados"], "reeleicao na Camara"),
    ("acritica-renovacao", "https://acritica.net/eleicoes-2026/camara-renova-35-das-cadeiras-e-tera-183-deputados-em-primeiro-mandato/", ["183"], "renovacao de 35% da Camara"),
    ("poder360-aprovacao-quaest", "https://www.poder360.com.br/poder-eleicoes-2026/governo-lula-e-aprovado-por-48-e-desaprovado-por-47-diz-quaest/", ["48%", "47%"], "aprovacao do governo, Quaest, julho de 2026"),
    ("poder360-desconfianca-stf", "https://www.poder360.com.br/poder-pesquisas/desconfianca-no-stf-atinge-43-maior-nivel-desde-2012/", ["43%"], "desconfianca no STF, Datafolha, marco de 2026"),
    ("metropoles-confianca-stf", "https://www.metropoles.com/brasil/confianca-no-stf-cai-de-50-para-43-em-7-meses-diz-quaest", ["43%", "50%"], "confianca no STF, Quaest"),
    ("dgabc-desconfianca-stf-quaest", "https://www.dgabc.com.br/Noticia/4346869/desconfianca-com-o-stf-cresce-10-pontos-e-alcanca-56-aponta-pesquisa-quaest", ["56%"], "desconfianca no STF, Quaest, setembro de 2026"),
    ("gazeta-moraes-vorcaro", "https://gazetadopovo.com.br/eleicoes/2026/moraes-vota-em-colegio-de-sao-paulo-sob-crise-no-stf-por-relacao-com-vorcaro", ["Vorcaro"], "Moraes e Vorcaro"),
    ("gazeta-master-inss-stf", "https://gazetadopovo.com.br/eleicoes/2026/master-emendas-rio-de-janeiro-inss-stf-dita-ritmo-casos-explosivos-impacto-eleitoral", ["Master"], "Master, INSS e STF e o impacto eleitoral"),
    ("wikipedia-master", "https://en.wikipedia.org/wiki/Banco_Master_scandal", ["Banco Master"], "Banco Master scandal (indice de fontes primarias)"),
    ("metropoles-condenacao-bolsonaro", "https://www.metropoles.com/brasil/trama-golpista-stf-condena-bolsonaro-a-27-anos-e-3-meses-de-prisao", ["27 anos"], "condenacao de Bolsonaro"),
    ("gazeta-impeachment-senado", "https://www.gazetadopovo.com.br/eleicoes/2026/gazeta-do-povo-mapeia-candidatos-senado-impeachment-ministros-stf/", ["impeachment"], "candidatos ao Senado e impeachment de ministros do STF"),
    ("ndmais-stf-senado", "https://ndmais.com.br/politica/stf-vira-tema-central-na-eleicao-para-o-senado-em-2026/", ["Senado"], "STF como tema da eleicao do Senado"),
    ("metropoles-pesquisas-presidente", "https://www.metropoles.com/colunas/andreza-matais/pesquisas-acertaram-votacao-de-lula-mas-subestimaram-flavio-bolsonaro", ["Flávio"], "pesquisas de presidente (so contexto)"),
    ("cnn-sobras", "https://www.cnnbrasil.com.br/politica/hugo-pede-ao-stf-que-regras-sobre-sobras-eleitorais-valham-a-partir-de-2026/", ["sobras"], "regra das sobras eleitorais"),
    ("conjur-sete-deputados", "https://www.conjur.com.br/2025-jul-31/camara-declara-perda-de-mandato-de-sete-deputados-e-convoca-substitutos/", ["sete deputados"], "perda de mandato de sete deputados pela regra das sobras"),
    ("nexo-perfil-eleitos", "https://www.nexojornal.com.br/grafico/2026/10/04/perfil-deputados-federais-eleitos-2026", ["deputados"], "perfil dos deputados federais eleitos"),
    ("cnn-governadores-apoio", "https://www.cnnbrasil.com.br/eleicoes/governadores-eleitos-flavio-lula/", ["governadores"], "apoio dos governadores eleitos"),
]


def texto(h: str) -> str:
    h = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h))


def trecho(t: str, expr: str) -> str | None:
    i = t.find(expr)
    if i < 0:
        return None
    ini = max(t.rfind(". ", 0, i) + 2, i - 280)
    fim = t.find(". ", i)
    fim = i + 280 if fim < 0 else min(fim + 1, i + 280)
    return t[ini:fim].strip()


def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    ja = set()
    if CSV.exists():
        with open(CSV, encoding="utf-8", newline="") as f:
            ja = {r["id"] for r in csv.DictReader(f)}
    novo = not CSV.exists()
    with open(CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["id", "url", "capturado_utc", "bytes", "sha256", "status", "assunto", "trecho"])
        for id_, url, exprs, assunto in FONTES:
            if id_ in ja:
                continue
            r = subprocess.run(["curl", "-sL", "-m", "60", "-A", UA, url], capture_output=True)
            corpo = r.stdout
            (PASTA / f"{id_}.html").write_bytes(corpo)
            try:
                h = corpo.decode("utf-8")
            except UnicodeDecodeError:
                h = corpo.decode("latin-1")
            t = texto(h)
            achados = [x for x in (trecho(t, e) for e in exprs) if x]
            status = "ok" if len(achados) == len(exprs) and len(corpo) > 5000 else "trecho_nao_encontrado"
            w.writerow([id_, url, datetime.now(timezone.utc).isoformat(timespec="seconds"), len(corpo), hashlib.sha256(corpo).hexdigest(), status, assunto, " || ".join(achados)[:900]])
            print(id_, status, len(corpo), flush=True)
            time.sleep(1.0)


if __name__ == "__main__":
    main()
