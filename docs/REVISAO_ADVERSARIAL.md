# Revisão adversarial: três passadas

**Feita em:** 07/out/2026, pela mesma IA que executou o projeto (não é revisão de pessoa). Registro do que cada passada procurou, o que achou e o que mudou no texto. A passada 3 tem uma parte programática, em [`ferramentas/revisao-adversarial.py`](../ferramentas/revisao-adversarial.py), que refaz por caminho independente os números do relatório.

## Passada 1: o leitor que acha que o relatório minimiza a vitória da direita

| Objeção | O que foi checado | Resultado e mudança |
|---|---|---|
| "A R1 mistura MDB, PSD e Podemos com o PL: dizer que a direita não cresceu é artefato da régua." | O texto diz que o **PL** cresceu muito (98 → 121 cadeiras, 16,6% → 22,7% dos votos) e que o campo R1 ficou parado em votos. Sensibilidade com os cortes deslocados: direita +8 a +13 cadeiras. | Mantido. Acrescentado ao veredito **o número da R2** (bancada de oposição ao governo 102 → 131, +29), que é a medida mais favorável a "o campo de oposição cresceu" e antes só estava no relatório. |
| "A frase 'a direita já era maioria' esconde o crescimento." | O bônus de cadeiras da direita (+3,3 pontos, de −0,1 em 2018) está no topo da explicação. | Mantido. |
| "Teste de direção das pesquisas com 6 a 13 disputas não prova ausência." | Concordo: o poder é baixo. | Acrescentada frase explícita: **ausência de direção neste teste não é prova de ausência de erro por campo**. |
| "Você usou só duas votações para os escândalos." | O texto diz isso e diz que não prova que os casos não pesaram. | Mantido. |
| "Governos: 'continuidade' omite que o PL foi de 2 para 5 governadores decididos." | O número está no texto. | Mantido. |

## Passada 2: o leitor que acha que o relatório infla a direita ou desmerece a esquerda

| Objeção | O que foi checado | Resultado e mudança |
|---|---|---|
| "A R1 de 2021 põe o PL como o antigo PR (7,78) e o PDT na esquerda: o corte muda a contagem da esquerda de 89 a 120." | A faixa completa está no texto e no relatório (cortes 3,5–5,5, 4,0–6,0 e 4,5–6,5). | Mantido. |
| "A federação do PT cresceu e a esquerda R1 caiu: você escolheu o número que convém?" | O texto dá os dois (82 → 88 e 105 → 101) e a causa da queda (PDT, 16 → 6). | Mantido. |
| "No teste exploratório a média de subestimação do lado de Flávio é +2,3 pontos; você só mostrou o teste do sinal." | O sinal é 6 de 13 (p = 1,00); a média é +2,3 e a mediana −0,2. | Acrescentados **média, mediana e as disputas que puxam a média** (RJ, PR, RR, RS, RO a favor do PL; PA e SC no sentido contrário). |
| "'Arrasto do candidato presidencial' é causa, e o dado é correlação entre municípios." | De fato. | **Reescrito**: o dado mede correlação, e "arrasto" é a leitura mais simples, não a única. O título da figura 12 passou de "Arrasto: o voto no candidato do PL puxa..." para "Correlação entre o voto no candidato do PL e o de direita nos outros cargos", com "(não é causa)" no subtítulo. |
| "A lista dos derrotados notáveis só mostra um lado?" | Os 30 mais votados de 2018 e de 2022 saem de **todos** os partidos (tabelas `a4_trinta_mais_votados_*`). Os critérios (a) e (b) do pré-registro (ministros, líderes) **não foram executados** por falta de fonte estruturada. | Declarado na §15 do pré-registro e no relatório (§8). |

## Passada 3: método e linguagem (teste do espelho)

| Verificação | Resultado |
|---|---|
| Palavras da lista proibida, nos textos publicados | nenhuma (checagem L1) |
| Travessão nos textos publicados | nenhum (L2) |
| Adjetivo sem medida | **trocado** "um PL muito maior e um centro menor" por números (98 → 121; centro R1 28 → 23) |
| Título causal ("Por que o PL ganhou tanto") | **trocado** por "O que acompanha o tamanho do PL em cadeiras (descrição, não causa)" |
| Teste do espelho, frase a frase do veredito | com os lados trocados, as frases sobre o campo ("não sustentada" para "a esquerda saiu bastante" e para "a direita dominou") são escritas igual; as de pesquisa dizem "seja qual fosse o campo" |
| Causa a partir de agregado | nenhuma frase afirma causa de voto; H6 e H2 ficaram "não testável" |
| Simetria dos testes | todas as tabelas de campo trazem esquerda e direita (S1); os maiores erros de pesquisa saem sem filtro de campo (S3) |
| Fonte única | D8 (lista da Gazeta), C (compilação de O Povo) e Master/STF (linha do tempo) estão marcados como fonte única ou como sem teste |

## Parte programática (resultados em `resultados/revisao_adversarial.json`)

| # | O que refaz | Resultado |
|---|---|---|
| A1 | 513 vagas e 513 eleitos no JSON oficial por UF | passa |
| A2 | cadeiras por partido: JSON oficial = tabela derivada | passa (sem diferença) |
| A3 | cadeiras por campo (R1) em 2026 pelo JSON oficial = tabela da A1 | passa (388 / 101 / 23 / 1) |
| A4 | esquerda + centro + direita + sem classificação = 513 nos três anos | passa |
| A5 | % de votos válidos por partido: JSON (`tvtn` + `tvtl`) = derivado | passa (PL 22,72%; PSD 8,26%; Republicanos 6,96%; MDB 6,94%; Podemos 5,18%) |
| A6 | reprodução das 513 cadeiras com a regra da lei | passa (0 diferenças) |
| A7 | votos válidos por UF: soma das listas = detalhe do TSE | passa (0,0000%) |
| B1 | municípios TSE × IBGE ≥ 99,9% | passa (5.567 de 5.571) |
| C1 | SP: Datafolha e Quaest iguais em duas fontes | passa |
| C2 | pesquisas com registro no TSE na janela ≥ 90% | passa (30 de 32) |
| S1 a S3 | simetria | passam |
| L1, L2 | linguagem | passam |

**O que esta revisão não fez:** não é revisão de pessoa; não verificou a assinatura dos boletins nem os boletins (o projeto não os usou); não conferiu a classificação de campo contra outra escala; e a regra legal aplicada em 2026 é a que reproduz as 513 cadeiras, sem a fonte legal capturada.
