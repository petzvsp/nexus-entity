# teoria de inteligencia artificial

# Teoria de LLMs e Processamento de Linguagem

## 1. Como o Modelo Pensa (Inferência)
O NEXUS não "pensa" como um humano. Ele é um modelo autorregressivo. Ele lê o contexto (seu prompt) e calcula probabilisticamente qual é o próximo "token" (pedaço de palavra) mais provável.

## 2. Limitações Físicas
- **Context Window (2048 tokens):** O modelo tem memória de curto prazo. Conversas muito longas fazem ele "esquecer" o início.
- **Alucinação:** Quando o modelo inventa fatos por falta de contexto. É por isso que usamos o RAG (para dar contexto real).
- **Temperatura:** Controla a criatividade. Temperaturas baixas (0.1) geram respostas lógicas e repetitivas. Temperaturas altas (0.8) geram respostas criativas e imprevisíveis.

## 3. RAG vs Fine-Tuning
- **Fine-tuning:** Ensinar a IA mudando os pesos dela (caro, pesado, impossível no celular).
- **RAG (Retrieval-Augmented Generation):** Dar um "livro" (nossos arquivos Markdown) para a IA ler na hora da prova. É o método usado no NEXUS.

## 4. Embeddings e Busca
Diferente dos LLMs gigantes que buscam por significado matemático (vetores), o NEXUS busca por **palavras-chave exatas** (keywords) para economizar processamento.
