# Pré-registro: os testes e os critérios, escritos antes das análises

**Estado:** versão 1, de 07/out/2026 (manhã). **Este arquivo é gravado em commit antes de qualquer análise**, e o relatório cita o hash desse commit.

**Regra de mudança:** depois do commit, um critério só muda com uma entrada na §15, com o antes, o depois, o motivo e a declaração de se a mudança foi feita **antes ou depois** de ver o resultado. Mudança depois de ver o resultado vai para o relatório com o mesmo destaque do resultado.

---

## 0. O que já foi visto antes deste registro (declaração)

Diferente do vídeo 5, o resultado desta eleição é público e foi manchete. Antes de escrever este arquivo, foram vistos:

- as bancadas eleitas por partido na Câmara (PL 121, PT 70, União 46, PSD 43, PP 41, Republicanos 41, MDB 36, Podemos 27 e as demais), lidas no JSON oficial das 27 UFs;
- os três deputados mais votados (Nikolas Ferreira, Lucas Pavanato, Erika Hilton);
- os senadores eleitos por partido (PL 19, MDB 7, PT 6, …) e os governadores eleitos no 1º turno e os que foram a 2º turno, por nome e partido;
- matérias de imprensa com: renovação de ~35% da Câmara; a situação de Marina Silva e André Janones; erro de institutos na disputa de governador de SP; aprovação do governo e confiança no STF em pesquisas de 2025 e 2026; o caso Banco Master e as ligações noticiadas com ministros do STF; a condenação de Bolsonaro;
- o resultado do vídeo 5 (P6: 19 senadores do PL em estados onde Flávio liderou).

**Não foi calculado nem visto:** nenhuma régua de campo (R1, R2, R3) aplicada; nenhum número de cadeiras por campo; nenhuma variação municipal; nenhum cruzamento com IBGE; nenhum erro de pesquisa calculado por nós; nenhuma série de opinião montada; nenhum resultado de incumbente por votação no plenário; nenhum contrafactual de puxador.

---

## 1. As réguas de campo

### R1 · Ideologia do partido (especialistas)

- **Fonte:** a escala publicada de especialistas mais recente que cubra os partidos de 2026, capturada com trecho (candidato principal: Bolognesi, Ribeiro e Codato, *Dados*, 2023). Se a escala não puder ser capturada na íntegra na Fase 1, R1 sai do relatório e isso é dito.
- **Corte** (escala de 0, esquerda, a 10, direita): **esquerda < 4,0 · centro 4,0 a 6,0 · direita > 6,0**. Sensibilidade com os cortes deslocados 0,5 ponto para cada lado.
- Partido criado ou fundido depois da escala: herda a nota do partido de origem só se a fusão for de partidos com nota e a nota for a média ponderada pelas cadeiras de 2022; sem isso, *"sem classificação"*.

### R2 · Comportamento no plenário (Câmara)

- **Fonte:** `votacoesVotos-AAAA.csv` e `votacoesOrientacoes-AAAA.csv` da Câmara, de 01/02/2023 a 30/09/2026.
- **Medida:** % dos votos *Sim* ou *Não* de cada deputado iguais à orientação do **Governo** nas votações nominais em que o Governo orientou *Sim* ou *Não* (orientação *Liberado* e votos *Abstenção*, *Obstrução* e ausência ficam fora).
- **Corte:** **governista ≥ 70% · independente entre 40% e 70% · oposição ≤ 40%**. Sensibilidade com 65% e 45%. Deputado com menos de 50 votações válidas: *"sem classificação"*.
- **Partido:** a mediana dos seus deputados em exercício em 30/09/2026.
- **Para os eleitos de 2026 sem mandato anterior:** a régua de partido.

### R3 · Apoio declarado e coligação

- **Governador e senador:** apoio declarado a candidato a presidente no 1º turno de 2026, com fonte capturada, nas categorias Flávio · Lula · outro · sem apoio. Duas fontes; se divergem, as duas versões rodam (como no vídeo 5).
- **Deputado:** a **coligação formal** do seu partido na eleição de presidente (registro no TSE): coligação de Flávio · coligação de Lula · outra · nenhuma.
- ⚠️ R3 mede alinhamento com um candidato, não ideologia. O relatório usa as palavras *"alinhado a"*, não *"de direita"*, quando a régua é R3.

**Robustez:** uma conclusão sobre campo é **robusta** se o sinal e a ordem de grandeza valem nas três réguas; **dependente da régua** se não.

---

## 2. A1 · Câmara

- **Bases de comparação:** (a) a eleição de 2022; (b) a eleição de 2018; (c) a **bancada na véspera**: partido de cada deputado em exercício em 30/09/2026, pelo histórico da API da Câmara.
- **Medidas:** cadeiras e % de cadeiras por partido, federação e campo; votos e % de votos válidos por campo; volatilidade de Pedersen em cadeiras e em votos (2018→2022 e 2022→2026); número efetivo de partidos.
- **"O campo X cresceu"** só se escreve se a % de cadeiras do campo subiu contra a base nomeada, com o tamanho. **"De onde veio o ganho"**: matriz de transição por partido e campo, cadeira a cadeira, entre a bancada na véspera e a eleita.
- **"Mudança maior que a de 2018"** só se a volatilidade de 2022→2026 for maior que a de 2014→2018 em cadeiras **e** em votos.

## 3. A2 · Senado

- **Vaga que trocou de campo:** campo do senador eleito em 2018 para a vaga (e, separadamente, do ocupante em 30/09/2026) contra o do eleito em 2026, nas réguas R1 e R3.
- **Composição de fev/2027:** os 27 senadores com mandato até 2031 (eleitos em 2022, ou quem os substituiu) mais os 54 eleitos.
- **Limiares:** 41 (maioria absoluta), 49 (3/5) e 54 (2/3), com o que cada um decide capturado de fonte legal (Constituição e Regimento do Senado). O texto descreve o que a aritmética permite, ⛔ nunca o que o Senado *vai* fazer.

## 4. A3 · Governos

- Eleitos no 1º turno, em 2º turno, reeleitos, e troca de campo (R3, e R1 pelo partido) contra o governador eleito em 2022 e o em exercício em 30/09/2026.
- 2º turno: *"em disputa"*, sem previsão.

## 5. A4 · Renovação e derrotados notáveis

- **Renovação:** % dos 513 eleitos que não estavam em exercício em 30/09/2026 e % que nunca tiveram mandato de deputado federal; contra 2018 e 2022 pelo mesmo critério.
- **Notável** (o mesmo critério para todos os campos), quem disputou qualquer cargo em 2026 e se enquadra em pelo menos um: (a) ministro ou ex-ministro dos governos Bolsonaro ou Lula 3; (b) líder de partido ou de bancada na Câmara ou no Senado em 2025 ou 2026; (c) entre os 30 deputados federais mais votados do país em 2022; (d) senador em fim de mandato que tentou a reeleição; (e) governador que tentou a reeleição.
- A tabela sai com **eleitos e não eleitos** de cada campo, ordenada por nome, ⛔ nunca só os derrotados de um lado.
- **Queda de votos de reeleito:** razão votos 2026 ÷ votos 2022 para todos os reeleitos; a lista dos 20 maiores em queda e dos 20 maiores em alta, de todos os partidos.

## 6. A5 · Puxadores

- **Concentração:** votos do 1º colocado ÷ votos nominais da lista (partido ou federação) na UF.
- **Cadeiras puxadas,** duas versões: (1) o voto do puxador reduzido ao quociente eleitoral (ele continua eleito, só o excedente sai); (2) o voto dele retirado. Em cada uma, a distribuição completa é refeita e as cadeiras que mudam de lista são listadas.
- **Regra de distribuição:** a que reproduzir **513 de 513** sobre o dado oficial. As variantes testadas são a do Código Eleitoral com a Lei 14.211/2021 e a interpretação do STF nas ADIs 7228, 7263 e 7325, com a fonte legal capturada. Se nenhuma reproduzir 513, A5 não roda e o relatório diz.
- **Série:** a mesma conta para os recordistas de 2018 e 2022 (e os anteriores, se o dado estiver no mesmo formato).

## 7. D2 · A linha do tempo

**Os eventos**, com a data a confirmar por ato oficial e duas reportagens independentes:

| # | Evento | Data a confirmar |
|---|---|---|
| E1 | INSS: operação da PF e CGU sobre descontos em benefícios | abr/2025 |
| E2 | IOF: decreto do governo e derrubada pelo Congresso | mai a jun/2025 |
| E3 | Tarifa dos EUA sobre produtos brasileiros e sanções da Lei Magnitsky ao ministro Alexandre de Moraes | jul/2025 |
| E4 | Condenação de Jair Bolsonaro pela 1ª Turma do STF | set/2025 |
| E5 | PEC da Blindagem e urgência da anistia na Câmara, e os protestos | set/2025 |
| E6 | Início do cumprimento de pena de Bolsonaro | nov/2025 |
| E7 | Liquidação do Banco Master pelo Banco Central | nov/2025 |
| E8 | Contrato do escritório da esposa do ministro Alexandre de Moraes com o Banco Master | a confirmar |
| E9 | Mensagens entre Daniel Vorcaro e o ministro Alexandre de Moraes divulgadas a partir de material da PF | a confirmar, 2026 |
| E10 | Menções ao ministro Dias Toffoli no caso Master | a confirmar |
| E11 | Nova tarifa dos EUA | a confirmar, 2026 |
| E12 | Fim das sanções da Lei Magnitsky ao ministro | a confirmar, 2026 |

- **Simetria:** a lista tem eventos que, pela leitura de imprensa, pesaram contra o governo (E1, E2, E7 a E10) e contra a oposição (E3, E4, E5, E6, E11). Evento novo só entra pela §15, dizendo se foi antes ou depois de ver as séries.
- **Linguagem:** cada pessoa aparece como o ato oficial a descreve (*investigado*, *citado*, *denunciado*, *condenado*), com a resposta pública dela quando houver.
- **Teste de cada evento contra as séries da D1:** a medição do mesmo instituto imediatamente antes e a primeira depois, se a distância entre as duas for de até 45 dias. O evento **coincide com movimento** da série se a mudança passa da **maior variação entre duas medições seguidas** daquela série fora de todas as janelas de evento. Senão, *"a série não se moveu além do normal"*. Eventos a menos de 30 dias um do outro são testados juntos e ditos juntos.

## 8. D3 · Exposição no plenário

**As votações** (nominais na Câmara; ID conferido na Fase 1; a que não existir como nominal sai, registrada):

| # | Votação | Data |
|---|---|---|
| V1 | PEC da Blindagem, 1º turno | set/2025 |
| V2 | Urgência do projeto de anistia | set/2025 |
| V3 | Derrubada do decreto do IOF | jun/2025 |
| V4 | Aumento do número de deputados | 2025 |
| V5 | Licenciamento ambiental | jul/2025 |
| **P** | **Placebo:** isenção do IR até R$ 5 mil (votação quase unânime) | out/2025 |

- **Universo:** deputados em exercício na votação que disputaram deputado federal em 2026.
- **Resultados:** (1) eleito ou não; (2) log(votos 2026 ÷ votos 2022), para quem disputou deputado federal nas duas.
- **Modelo:** voto *Sim* = 1, *Não* = 0 (ausência e abstenção fora), efeito fixo de partido em 2026 × UF, controle do log dos votos de 2022. Erro padrão por UF. Benjamini-Hochberg a 5% entre V1 a V5.
- **Leitura:** *"associado a"* com o tamanho. O **placebo** tem que dar nada; se der, o desenho não separa e o resultado das outras votações é dito como fraco.

## 9. C · As pesquisas

- **Universo:** pesquisas registradas no TSE para governador e senador de 2026, com campo terminado entre **26/set e 03/out**; por instituto, UF e cargo, a **última**. Para a tendência, a anterior do mesmo instituto, com campo terminado entre 05/set e 25/set. O mesmo para 2022 (campo entre 24/set e 01/out de 2022).
- **Resultado da pesquisa:** do relatório do instituto; sem ele, de duas reportagens independentes com o mesmo número; sem isso, a pesquisa sai e a contagem do que saiu vai para o relatório.
- **Votos válidos:** se a pesquisa só publica o total, converte-se tirando branco, nulo e indeciso proporcionalmente; sensibilidade com os indecisos divididos igualmente entre os dois primeiros.
- **Medidas:** E1 = erro no vencedor (pontos); **E2 = erro na margem entre os dois primeiros, com sinal no sentido do campo** (positivo quando a pesquisa subestimou o candidato do campo R3 "alinhado a Flávio"; o mesmo cálculo com R1); E3 = erro absoluto médio dos três primeiros.
- **Fora da margem:** |erro na proporção| > margem declarada; |E2| > 2 × margem declarada. Sensibilidade com efeito de desenho de 1,5.
- **Disputa direcional:** só entram em E2 as disputas em que os dois primeiros são de campos diferentes. As outras são contadas à parte.
- **Decomposição (C3):** tendência = última − anterior do mesmo instituto; a parte do erro **consistente com mudança de última hora** é a extrapolação linear da tendência até o dia da eleição, limitada ao próprio erro. Abstenção: correlação do erro da UF com a variação de comparecimento da UF contra 2022 (dito como fraco: 27 estados). O que sobra é o **resíduo**.
- **Erro com direção (C4):** teste binomial bicaudal do sinal do resíduo de E2 entre disputas (média dos institutos por disputa), α = 5%; por instituto, média do resíduo com sinal com intervalo, só para instituto com 8 ou mais disputas; contra 2022 pelo mesmo cálculo.
- **O que se escreve:** *"erro sistemático na mesma direção"* só se (a) o binomial rejeita, (b) o efeito aparece em mais de um instituto, (c) é maior que o de 2022 e (d) sobra depois da decomposição. Se só (a) a (c): *"erro na mesma direção, que a abstenção e a mudança de última hora explicam em parte"*. Se só um instituto: *"efeito do instituto X"*. Senão: *"o erro não tem direção que se sustente"*. ⛔ Nunca *tendenciosa*, *manipulada*, *comprada* ou qualquer palavra de intenção.
- **Contratante:** comparação descritiva do erro entre pesquisas pagas por veículo de imprensa, por partido ou candidato e pelo próprio instituto; sem teste se algum grupo tiver menos de 8 pesquisas.

## 10. D8 · O tema STF no Senado

- **Posição declarada sobre impeachment de ministro do STF** dos candidatos ao Senado: dois mapeamentos públicos de imprensa, capturados. Divergência entre eles: as duas versões rodam.
- **Medidas:** quantos dos 54 eleitos tinham a posição favorável, contrária ou sem posição; o mesmo para os 27 de mandato até 2031 se houver fonte; a conta contra 41, 49 e 54.
- **Desempenho:** entre candidatos competitivos (3 primeiros de cada UF), a diferença de votação entre favoráveis e não favoráveis **dentro do mesmo campo**, descritiva. ⛔ Sem afirmar que a posição causou o voto.

## 11. D5 e D6 · Incumbentes e eficiência

- **D5:** para governadores, senadores e deputados em exercício em 30/09/2026 que disputaram o mesmo cargo: % que se elegeu, por campo (três réguas), contra 2018 e 2022. **Anti-incumbência** se a taxa caiu em todos os campos; **campo** se caiu num e não no outro.
- **D6:** % de cadeiras ÷ % de votos por campo; candidatos por cadeira; listas de federação contra partido isolado.

## 12. B · Geografia e abstenção

- **Unidade:** município (5.570), ponderado pelo eleitorado. Exterior fora.
- **Variável explicada:** variação da % de votos válidos do campo (R1) para deputado federal, senador (soma dos dois votos ÷ 2) e governador, 2022 → 2026; a mesma de 2018 → 2022 como **placebo de estabilidade** (relação que já existia antes não é novidade de 2026).
- **Variáveis do Censo 2022** (tabelas do SIDRA conferidas na Fase 1): renda domiciliar per capita, % com ensino superior, % evangélicos, % católicos, % pretos e pardos, % com 60 anos ou mais, % urbana; mais Bolsa Família por habitante (MDS, set/2026 ou o mês mais recente), PIB per capita e % do valor adicionado da agropecuária (IBGE, ano mais recente).
- **Modelo:** variação ~ variáveis padronizadas + efeito fixo de UF; erro padrão por UF; I de Moran dos resíduos. *"Acompanha"* só se o intervalo de 95% exclui zero **e** o coeficiente difere do de 2018 → 2022.
- **Abstenção (B3):** 1 − comparecimento ÷ aptos, por município, em 2018, 2022 e 2026. **Contrafactual:** os votos de cada município reponderados pelo comparecimento de 2022, mantidas as proporções de voto do município; se a % nacional do campo muda menos de 0,5 ponto, *"a abstenção não muda o retrato"*.
- **Arrasto (B4):** correlação municipal, ponderada, entre a % do presidente e a % do campo em cada cargo, por UF, em 2018, 2022 e 2026.

## 13. O veredito

- **Status de cada hipótese** em cada arena: **consistente** (as previsões da hipótese aparecem nos testes nomeados), **inconsistente** (aparece o contrário), **não testável** (o dado não alcança). Uma hipótese pode ser consistente em uma arena e não em outra.
- **Grau de confiança:** **alto** = robusto nas três réguas, nos dois caminhos e com placebo limpo; **médio** = duas dessas três; **baixo** = o resto.
- O veredito é escrito **depois** da revisão adversarial e passa pelo teste do espelho frase a frase.

## 14. Palavras que não entram no relatório

*fraude, manipulada, comprada, encomendada, tendenciosa (como conclusão), golpe (fora do nome da ação penal), massacre, humilhação, lavada, varrida, mentiu, mentira, corrupto (sem condenação), culpado (sem condenação)*.

## 15. Emendas a este registro

| Data | O quê | Antes | Depois | Motivo | Antes ou depois de ver o resultado |
|---|---|---|---|---|---|
| | | | | | |
