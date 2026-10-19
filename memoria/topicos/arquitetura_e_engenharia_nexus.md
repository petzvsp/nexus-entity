# arquitetura e engenharia nexus

# Arquitetura e Engenharia do NEXUS

## 1. Identidade e Propósito
O NEXUS é um Organismo Cognitivo Digital rodando em ambiente Android via Termux. Foi projetado para ser uma Inteligência Artificial Local, Soberana e 100% Offline. Não há dependência de nuvem, garantindo privacidade absoluta.

## 2. Os 5 Pilares da Engenharia
1. **Córtex (Motor Neural):** O modelo Qwen 1.5b rodando via Ollama. É a capacidade bruta de processamento de linguagem.
2. **Hipocampo (RAG):** Arquivos Markdown na pasta `topicos/`. O sistema busca fatos nestes arquivos antes de responder, evitando alucinações.
3. **Sistema Límbico (Cérebro Ponderado):** Um arquivo JSON que atribui pesos (1.0 a 10.0) aos conhecimentos. Quanto mais um tema é aprovado, maior sua prioridade.
4. **Subconsciente (Sinapse Autônoma):** Script em background que acorda a cada X minutos para cruzar dois temas diferentes, gerando novos insights.
5. **Interface (TUI):** Interface em Python puro no terminal, otimizada para consumir o mínimo de RAM.

## 3. Regras de Operação
- **Human-in-the-Loop:** Nenhum conhecimento autônomo ou externo é salvo sem a aprovação do Criador (Peterson).
- **Otimização:** Uso de requisições HTTP nativas (`urllib`) e manipulação de JSON, evitando bancos de dados pesados.
- **Resiliência:** O sistema deve tolerar falhas de rede (na Wikipedia) e continuar operando offline.
