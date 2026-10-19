# mecanismo atencao

O Mecanismo de Atenção (Attention Mechanism) resolve a limitação das redes recorrentes tradicionais ao permitir que o modelo relacione diretamente qualquer token de uma sequência com qualquer outro, independentemente da distância entre eles.

Analogia Mental

Pense em estar a ler uma frase técnica longa. Para entender o significado do último termo, os seus olhos não dão o mesmo peso a todas as palavras anteriores; você foca seletivamente nos termos-chave que carregam o contexto crítico e descarta o ruído irrelevante.

Funcionamento Técnico

A arquitetura baseia-se em três vetores gerados por multiplicações matriciais das entradas por matrizes de pesos aprendidos: Queries (Q), Keys (K) e Values (V).

Projeções Lineares: A partir da matriz de entrada X, o sistema projeta três representações distintas: Q = XW_Q, \quad K = XW_K, \quad V = XW_V 

Atenção Produto Escalar Escalada (Scaled Dot-Product Attention): A relevância entre as consultas e as chaves é calculada pelo produto escalar normalizado, seguido por uma função \text{softmax} que transforma os valores em distribuições de probabilidade (pesos de atenção): \text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V Onde d_k é a dimensão dos vetores de chave, usada como fator de escala para evitar gradientes instáveis.

Atenção de Múltiplas Cabeças (Multi-Head Attention): Em vez de calcular a atenção apenas uma vez, o modelo divide as dimensões em h "cabeças" paralelas. Cada cabeça aprende a focar em aspetos diferentes da sequência em simultâneo (ex: uma cabeça foca na sintaxe gramatical, outra na correlação semântica de longo alcance). Os resultados são concatenados e projetados de volta à dimensão original.
