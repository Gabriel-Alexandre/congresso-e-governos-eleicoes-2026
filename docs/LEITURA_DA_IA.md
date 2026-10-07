# A leitura da IA, arena por arena

**Escrito em:** 07/out/2026. **O que é:** a opinião da IA que executou o processo, marcada como opinião, depois da revisão adversarial em três passadas ([`REVISAO_ADVERSARIAL.md`](REVISAO_ADVERSARIAL.md)). Cada número sai de [`resultados/RESUMO.json`](../resultados/RESUMO.json) ou dos CSV de `resultados/`.

> ⚠️ **Opinião não é prova.** O [`RELATORIO.md`](../RELATORIO.md) diz o que os dados fecham. Este arquivo diz qual é a leitura mais provável de cada resultado, o grau de confiança e o que ficou sem resposta. Nenhuma frase aqui julga intenção de pessoa, partido ou instituto, e nenhuma afirma causa onde o desenho só mostra coincidência.
>
> **Dependência da régua.** "Direita", "centro" e "esquerda" são definições (docs/PRE_REGISTRO.md §1). O que vale nas três réguas é dito como robusto; o que depende de uma régua é dito como dependente dela. **R1** é a escala de especialistas de 2021, que põe MDB, PSD, PSDB e Podemos na direita (notas de 7,0 a 7,2). **R2** é o voto no plenário contra a orientação do governo. **R3** é a coligação formal na eleição presidencial: em 2026 o PL concorreu sem coligação, então R3 não é comparável entre 2022 e 2026.

## O placar

| # | Hipótese | Situação | Confiança | O que sustenta |
|---|---|---|---|---|
| H1 | Virada de opinião para a direita | **inconsistente** | média | Câmara: voto de direita 72,0% → 72,3%; governo e Senado: subida menor que a anterior |
| H2 | Referendo sobre o governo | **não testável** | baixa | só há uma aprovação capturada (Quaest, jul/2026, 48 × 47); sem série |
| H3 | Anti-incumbência (cansaço de quem está no cargo) | **inconsistente** | média | deputados reeleitos: 57,5% contra 55,6% em 2022 |
| H4 | Estrutura e eficiência (listas, federações, puxadores) | **consistente** | alta | bônus de cadeiras da direita: −0,1 → +2,1 → +3,3 pp; puxadores |
| H5 | Máquina (emendas, fundo, mandato) | **não testável** | baixa | emendas não foram analisadas nesta rodada |
| H6 | Casos e escândalos (Master, STF, INSS, condenação) | **não testável** | baixa | voto na PEC da Blindagem sem relação com a eleição (−5,2 pp); séries de opinião insuficientes |
| H7 | Composição do eleitorado (perfil e abstenção) | **inconsistente** | média | perfil soma 1,4 ponto de R² além da UF; abstenção 20,8% → 20,9% |
| H8 | Arrasto do candidato à Presidência | **consistente** | alta | correlação com o voto de direita: senador 0,53 → 0,70, deputado 0,31 → 0,39 |

*consistente* = as previsões da hipótese aparecem nos testes nomeados; *inconsistente* = aparece o contrário; *não testável* = o dado coletado não alcança. Mais de uma hipótese pode valer ao mesmo tempo.

---

## Câmara dos Deputados

**Base de 2022:** o arquivo atual do TSE (PL 98, PT 69). Matérias da época deram PL 99 e PT 68; a diferença é compatível com a troca de sete mandatos decidida pelo STF sobre as sobras (fonte `conjur-sete-deputados`), mas não foi verificada cadeira a cadeira.

**Os fatos (alto):** o PL passou de 98 para 121 deputados (16,6% → 22,7% dos votos). A federação PT/PCdoB/PV passou de 82 para 88. Pela R1, a direita foi de 380 para 388 cadeiras (74,1% → 75,6%) e a esquerda de 105 para 101; em votos, a direita ficou em 72,0% → 72,3% e a esquerda em 21,1% → 20,5%. Com os cortes da escala deslocados em meio ponto, a direita vai de 380 a 388 (corte 3,5–5,5) ou de 368 a 381 (corte 4,5–6,5), e a esquerda de 89 a 95 ou de 120 a 116.

**Pela R2 (voto no plenário):** a bancada que votou majoritariamente contra a orientação do governo (40% ou menos de concordância) foi de 104 para 131 cadeiras (com cortes de 65% e 45%, de 109 para 134). Essa é a medida que mais se aproxima de "o campo que se opõe ao governo cresceu", e ela cresceu. Duas ressalvas: em 2026 os deputados novos herdam a classe mediana do partido (os de 2022 só entram pelo próprio histórico), e o corte de 70% põe quase todo o centrão como governista.

**A leitura da IA (opinião, confiança média):** o que mudou na Câmara foi principalmente **dentro do campo de direita**, não entre os campos. O PL ganhou 6,1 pontos de voto enquanto o voto somado dos partidos de direita pela R1 mal mexeu (0,3 ponto). Os votos saíram principalmente de partidos do mesmo campo (União −2,2, PP −1,1, Solidariedade −0,7, PSDB −0,6 pontos) e de legendas extintas ou fundidas, e a esquerda pela R1 teve 4 cadeiras a menos, por causa de uma queda grande do PDT, enquanto a federação do PT cresceu. A frase "a esquerda saiu bastante da Câmara" **não é sustentada** por esses dados, e a frase "a direita dominou a Câmara" só vale no sentido de que ela já era maioria em 2018 e 2022: o que os dados mostram é o PL indo de 98 para 121 cadeiras, a bancada de oposição pela R2 indo de 104 para 131 e o centro pela R1 indo de 28 para 23.

**O que acompanha o tamanho do PL em cadeiras (descrição, não causa; opinião, confiança média a alta):** três coisas que se medem. (1) **Concentração:** 22,7% dos votos e 121 cadeiras. (2) **Eficiência do sistema:** o bônus de cadeiras da direita sobre os votos foi de +3,3 ponto em 2026, contra +2,1 em 2022 e −0,1 em 2018. (3) **Puxadores:** Nikolas Ferreira fez 3.119.318 votos (68,4% da lista do PL em Minas) e, sem os votos dele, a lista teria 10 cadeiras a menos (uma delas a dele); Lucas Pavanato, em São Paulo, 3.038.438 votos e 5 cadeiras a mais para a lista. A regra de sobras aplicada em 2026 (que reproduz as 513 cadeiras) **não** favoreceu o PL: com todos os partidos disputando as sobras, o PL teria 5 cadeiras a mais.

**Renovação e incumbentes (opinião, confiança média):** 42,3% dos eleitos não estavam na Câmara na véspera (296 se reelegeram pelo mesmo partido). Dos eleitos de 2022, 57,5% se reelegeram, contra 55,6% dos eleitos de 2018 na eleição de 2022. Por campo (R1), a esquerda foi de 67,0% para 61,0% e a direita de 54,8% para 57,4%. Isso não combina com uma onda geral contra quem está no cargo (H3). Dos reeleitos, 37,3% tiveram menos votos que em 2022 (mediana da razão 2026 sobre 2022: 1,10). André Janones foi reeleito com 78.780 votos contra 238.967 em 2022, a segunda maior queda proporcional entre os reeleitos; a lista das maiores quedas e das maiores altas tem deputados de vários partidos (`resultados/a4_reeleitos_maiores_quedas_2022_2026.csv` e `..._altas_...`).

**O caso do voto no plenário (opinião, confiança baixa):** entre quem disputou a reeleição, votar a favor da PEC da Blindagem (16/09/2025) não teve relação com ser reeleito: 68,2% contra 67,0%, e −5,2 ponto (IC95 −19,6 a +9,2) dentro do mesmo partido e estado. Na votação do aumento do número de deputados, a diferença foi de +20,2 pontos (IC95 −3,5 a +44,0), sem significância depois da correção. O placebo não pôde ser estimado (17 deputados com variação dentro do partido e do estado). **Isso não prova que os casos não pesaram**: são duas votações, e o voto individual no plenário não mede a exposição de cada deputado a nenhum dos casos.

## Senado Federal

**Os fatos (alto):** o PL elegeu 19 das 54 vagas; MDB 7, PT 6; pela R1, a direita elegeu 43 (contra 39 em 2018), o centro 4 (9) e a esquerda 7 (6). Em fevereiro de 2027 o PL terá 28 das 81 cadeiras. A esquerda ganhou vaga em BA, MG, PE, RN e perdeu em CE, MA, RS, em relação a 2018.

**Os limiares (alto para a conta, baixo para o significado):** a R1 põe 65 dos 81 senadores na direita, acima de 41, de 49 e de 54, mas essa direita inclui MDB (8), PSD (5) e PSDB (2). O PL sozinho tem 28, abaixo de 41. Campo pela R1 não é bloco de votação e a conta não diz o que o Senado fará.

**O tema STF (opinião, confiança baixa a média):** dos 54 eleitos, 28 constavam como favoráveis ao impeachment de ministros do STF na lista da Gazeta do Povo, 6 como contrários, 14 sem posição ou não localizados e 3 em outra posição; 3 não constavam na lista. **Todos** os 28 favoráveis estão no campo de direita pela R1. Isso mostra que a posição era comum entre os eleitos; **não** mostra que a posição causou o voto (os favoráveis também eram, em geral, de partidos que já ganhavam nesses estados). A lista tem fonte única, e o Senado de 2027 não pode ser contado por ela porque os 27 senadores com mandato até 2031 não entram.

**A leitura da IA (opinião, confiança média):** o Senado de 2026 foi o cargo em que o voto acompanhou mais o voto em Bolsonaro para presidente (Jair pelo PSL em 2018 e pelo PL em 2022, Flávio pelo PL em 2026; correlação municipal de 0,53 em 2018 para 0,70 em 2026). O dado mede **correlação** entre municípios, e ela subiu. "Arrasto do candidato presidencial" é a leitura mais simples, não a única: a mesma correlação apareceria se os eleitores escolhessem os cargos pelo mesmo critério, sem que um puxasse o outro. O que ela não é, por si, é mudança de opinião dos eleitores de cada estado, que o dado não mede.

## Governos estaduais

**Os fatos (alto):** foram decididos 20 governos no 1º turno e 7 vão a 2º turno. Dos 20, 17 são de partidos de direita pela R1 e 3 de esquerda; em 2022 eram 20 de 27 e 4, e em 2018 18 de 27 e 6. 7 dos 20 são o mesmo governador de 2022 e 2 estados trocaram de campo pela R1 (ambos eram de PSB e passaram a PSD ou PP). O voto de direita para governador subiu 3,2 ponto contra 7,6 em 2018→2022. Apoio declarado, pela CNN Brasil (R3): 10 a Flávio, 5 a Lula, 1 a Caiado e 4 sem apoio.

**A leitura da IA (opinião, confiança média):** nos governos não houve troca de lado; houve **continuidade com mais PL**. A direita já tinha a maioria dos governos em 2018 e 2022, e o PL passou a ter 5 dos 20 decididos (2 em 2022). Dos 8 governadores de 2022 que tentaram continuar no cargo, 7 venceram ou foram ao 2º turno.

## As pesquisas

**Os fatos (alto para a conta, médio para a cobertura):** foram analisadas 32 pesquisas de Datafolha e Quaest da véspera, em 27 disputas de governador. O primeiro colocado (o eleito, ou o primeiro dos 7 estados que vão a 2º turno) apareceu abaixo da urna em 26 delas; a margem entre os dois primeiros foi menor na pesquisa que na urna em 23; erro médio do vencedor de 3,0 ponto abaixo; 25 das 32 ficaram fora da margem declarada no vencedor. Em 20 das 27 disputas a maioria das pesquisas mostrou corrida mais apertada que a urna (p = 0,02, teste do sinal).

**O erro tem direção por campo? (opinião, confiança média):** nas disputas em que um candidato era de Flávio e o outro de Lula (R3, 6 disputas) a pesquisa subestimou o lado de Flávio em 2 (p = 0,69); pela R1 (7 disputas), em 2 (p = 0,45). No teste exploratório, definido depois de ver os resultados (um dos dois primeiros alinhado a Flávio, o outro qualquer), foram 6 de 13 (p = 1,00); a média foi de +2,3 ponto de subestimação do lado de Flávio e a mediana de −0,2, ou seja, a média é puxada por cinco disputas (RJ, PR, RR, RS, RO), em que o candidato do PL terminou mais à frente do que as pesquisas mostravam, enquanto em PA (12,2), SC (5,7) pontos as pesquisas deram ao lado de Flávio mais do que a urna deu. Com 6 a 13 disputas, esses testes só acusariam desvios grandes e constantes; **ausência de direção neste teste não é prova de ausência de erro por campo**. **Nenhum teste mostra erro numa direção de campo.** O que os dados sustentam é outro padrão: as pesquisas mostraram corridas mais apertadas do que as urnas deram, para quem terminou em primeiro, **seja qual fosse o campo**. Os maiores erros no vencedor foram no Rio de Janeiro (Datafolha 11,3 pontos abaixo e Quaest 9,3), onde o candidato do PL terminou em primeiro, com mais votos que o previsto, e vai ao 2º turno, e no Amapá (Quaest 9,8 pontos), onde nenhum dos dois finalistas é do PL.

**O que isso não permite dizer:** não há "erro sistemático" no sentido do pré-registro, porque faltam duas coisas: a comparação com 2022 e a separação entre mudança de última hora e erro da pesquisa (não foram coletadas as pesquisas anteriores). O padrão pode ser mudança de última hora, abstenção diferencial ou decisão tardia de quem estava indeciso; os dados não separam. Também só entraram dois institutos.

## O que o eleitor sinalizou

**A leitura da IA (opinião, confiança baixa a média):** juntando H1, H2 e H3: (a) o voto de direita pela R1 ficou estável na Câmara (72,0% → 72,3%), (b) os deputados que tentaram continuar se reelegeram mais que na eleição anterior, e (c) a esquerda pela R1 manteve 20,5% dos votos. **Esse conjunto não combina com "o eleitor quis mudar tudo".** Combina com um eleitorado que manteve a divisão de 2022, concentrou parte do voto de direita no PL (provavelmente puxado pelo candidato presidencial, H8) e pouco mexeu na abstenção (20,8% → 20,9%; com o comparecimento de 2022, o voto de direita seria 72,23%, contra 72,32%). O perfil do município (religião, renda, cor, idade, Bolsa Família) explica pouco da variação do voto: a UF sozinha explica 20%, e o perfil soma 1,4 ponto. **O que não dá para dizer** é como o eleitor se enxerga (autoposicionamento) ou se os casos (Master, STF, INSS, condenação de Bolsonaro) pesaram: não há série de opinião suficiente neste projeto.

## O que o projeto não consegue dizer

1. Em quem cada pessoa votou: tudo aqui é entre municípios.
2. Se os casos (Master e ministros do STF, condenação de Bolsonaro, INSS, tarifaço, PEC da Blindagem) mudaram votos: as séries de opinião capturadas têm menos de duas medições do mesmo instituto antes e depois dos eventos.
3. O efeito de emendas parlamentares e de gasto de campanha: não foram analisados (a prestação de contas final ainda não existe).
4. Se as pesquisas erraram em 2026 mais que em 2022 e se a causa foi mudança de última hora: faltam as pesquisas anteriores e as de 2022. Pesquisas de Senado não foram coletadas.
5. O 2º turno: os 7 estados em disputa estão como "em disputa".
6. Se a classificação de campo de especialistas de 2021 ainda descreve os partidos de 2026: ela põe o PL na posição do antigo PR, e partidos novos ou fundidos herdam a média das origens.
