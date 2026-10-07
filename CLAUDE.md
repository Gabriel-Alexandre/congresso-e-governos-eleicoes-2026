# CLAUDE.md: como operar neste repositório

As regras moram em `.cursor/rules/*.mdc`, que o Cursor carrega sozinho e o Claude Code não. Este arquivo é roteador: se um fato aqui contradisser o arquivo dono, o dono ganha.

## Leia antes de qualquer coisa

| Ordem | Arquivo | Para quê |
|---|---|---|
| 1 | `ESTADO.md` | onde o trabalho parou |
| 2 | `.cursor/rules/congresso-fundamentos.mdc` | a doutrina, sempre |
| 3 | `docs/PLANO.md` | o método, o escopo e as fases |
| 4 | `docs/PRE_REGISTRO.md` | os critérios; nenhuma análise roda antes de ele estar em commit |
| 5 | `docs/FONTES_DE_DADOS.md` | endereços, o que existe e o que não existe |
| 6 | `docs/LEITURA_DA_IA.md` e `RELATORIO.md` | o resultado, quando a pergunta for sobre ele |

## O que nunca fazer

- Dar número que não saiu de script sobre dado com hash.
- Ler os boletins do repositório do vídeo 5 sem conferir o hash de `dados/FONTE_APURACAO.json`, ou escrever qualquer coisa naquele repositório.
- Mudar critério sem a entrada na §15 do pré-registro.
- Escrever número à mão no relatório.
- Chamar de "direita" ou "esquerda" sem dizer qual régua.
- Usar as palavras da lista da doutrina.
- Baixar em massa sem teto de requisições (o TSE devolve 429) e sem manifesto.
- Fazer commit ou push sem o autor confirmar (o autor mandou o commit e o push desta execução em 07/out/2026; isso não vale para as próximas).
