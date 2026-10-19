# rede neural artificial

Uma malha neural (ou Rede Neural Artificial) é um sistema computacional estruturado em grafos ponderados, projetado para reconhecer padrões imitando vagamente a arquitetura sináptica biológica.
Analogia Mental
Pense numa central de distribuição logística interligada por rodovias. Cada armazém (neurônio) recebe pacotes de várias origens, verifica a urgência, decide quanto material repassar e envia por estradas específicas. Algumas estradas têm pedágio alto ou trânsito lento (pesos baixos), enquanto outras são rotas principais (pesos altos). Com o tempo, a central aprende quais rotas priorizar com base nos erros de entrega passados.
Funcionamento Técnico
Uma malha neural opera através de operações matriciais e fluxo de dados direcionado:
 * O Neurônio Artificial (Nó):
   Recebe um vetor de entradas x = [x_1, x_2, \dots, x_n], multiplica cada entrada pelo seu respectivo peso sináptico w = [w_1, w_2, \dots, w_n], soma um termo de viés (bias) b, e aplica uma função de ativação não linear f:
   
 * Topologia em Malha (Camadas):
   * Camada de Entrada (Input): Recebe os dados brutos (ex: tokens de texto, pixels de imagem).
   * Camadas Ocultas (Hidden Layers): Realizam a extração progressiva de características abstratas. Numa malha densamente conectada (Fully Connected), cada neurônio de uma camada está ligado a todos os neurônios da camada seguinte.
   * Camada de Saída (Output): Produz o resultado final (classificação, probabilidade ou vetor gerado).
 * Propagação Direta (Forward Propagation):
   Os dados fluem da entrada para a saída através de multiplicações matriciais sucessivas (W \cdot X + B). Cada camada transforma o espaço vetorial de entrada para aproximar a função desejada.
 * Aprendizado e Retropropagação (Backpropagation):
   * Função de Perda (Loss Function): Mede o erro entre a saída gerada pela malha e o valor real esperado.
   * Gradiente Descendente (Gradient Descent): Utiliza o cálculo de derivadas parciais (regra da cadeia) para propagar o erro de trás para frente, ajustando iterativamente os pesos (w) e vieses (b) para minimizar a perda nas próximas iterações.
