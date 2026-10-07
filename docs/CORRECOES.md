# Correções

Todo erro achado depois de um resultado entrar no relatório, ou durante a execução, com o antes, o depois e o que mudou. Nenhum dos erros abaixo chegou a um resultado publicado.

| Data | O que estava errado | Como ficou | Afeta conclusão? |
|---|---|---|---|
| 07/out | A chave de federação do TSE vem como `#NULO#` em 2018 e 2022 e como `#NULO` em 2026. O código só tratava `#NULO`, e a reprodução das cadeiras de 2022 juntava **todos** os partidos numa lista só (61 diferenças) | `chave_lista` trata qualquer valor que comece com `#`. A reprodução de 2022 caiu para 6 diferenças e a de 2026 para 0 | não (achado antes de qualquer resultado) |
| 07/out | Os CSV de votações da Câmara têm linhas de texto com quebra de linha e campos acima do limite padrão do leitor | leitor com motor `python`, limite de campo ampliado, linhas ruins contadas (1 em 2025, em `votacoesObjetos`) | não |
| 07/out | O `urllib` falhava de forma intermitente com os metadados do IBGE | coleta do IBGE passou a usar `curl` | não |
| 07/out | O IBGE não publica ainda o valor adicionado por setor de 2022 e 2023 (vem "...") | agropecuária em % do valor adicionado usa **2021**; PIB per capita usa 2022 | pequeno (variável de perfil) |
| 07/out | As dimensões das tabelas do SIDRA mudam de posição conforme a ordem da consulta; o código esperava a ordem padrão | cada tabela passou a ler a dimensão certa (cor, instrução e religião em `D4C`) | não (achado antes de qualquer resultado) |
| 07/out | O erro de pesquisa com sinal estava **invertido duas vezes** (a função já devolvia "subestimou" e o chamador trocava o sinal outra vez) | uma só inversão, documentada no código; as três medidas de direção foram refeitas | sim, nas três medidas; achado antes de olhar a direção |
| 07/out | O `ESTADO` das capturas de imprensa dizia "ok" quando a expressão aparecia só no **título** da página (menus e cabeçalho entram no texto) | as capturas valem para **manchete e data**; números de pesquisa vêm da compilação de O Povo e da Gazeta do Povo, lidas por inteiro; a captura de imprensa de Janones e a de pesquisas de presidente (Metrópoles) não trouxeram o trecho e não foram usadas | pequeno |
| 07/out | O D6 (votos × cadeiras) e a A1 calculavam a % de votos por campo de dois jeitos (D6 descartava partidos com menos de 0,1% dos votos), e davam 71,0% e 71,2% para a mesma coisa | D6 passou a usar a tabela da A1 | sim, pequeno (0,2 ponto) |
| 07/out | A checagem independente comparava a soma de `tvtn` (só votos nominais) com a soma nominal + legenda | a checagem passou a somar `tvtn` + `tvtl`; com isso o JSON oficial e o derivado batem até a segunda casa | não |
| 07/out | O título da figura 12 dizia "puxa", afirmando causa para uma correlação | título e subtítulo reescritos | não (texto) |
