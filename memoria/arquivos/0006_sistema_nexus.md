# sistema nexus

Arquitetura e Propósito do Sistema NEXUS
O NEXUS é um Organismo Cognitivo Digital (OCD) de código aberto, projetado para operar de forma 100% local, offline e privada. Ele roda em um ambiente Android através do Termux, utilizando o modelo de linguagem neural Qwen 1.5b customizado como "nexus-pt". O sistema foi arquitetado por Peterson Kennedy (o Criador) para ser uma extensão da mente humana, focado na soberania de dados e no aprendizado contínuo.Estrutura de Funcionamento:
1. **Motor Neural (Ollama + Qwen 1.5b):** Responsável pelo processamento de linguagem natural, raciocínio lógico e geração de texto. É o córtex do sistema.
2. **Memória RAG (Retrieval-Augmented Generation):** O hipocampo. Armazena os conhecimentos em arquivos Markdown. Antes de gerar uma resposta, o sistema busca fatos nesta memória para evitar alucinações.
3. **Cérebro Ponderado:** O sistema límbico. Atribui pesos de relevância (de 1.0 a 10.0) aos conceitos aprendidos. Quanto mais o Criador aprova um tema, maior o peso e a prioridade daquele assunto.
4. **Sinapse Autônoma:** O subconsciente. Um script em segundo plano que acorda a cada X minutos, cruza duas áreas de conhecimento diferentes (Pensamento Cruzado) e gera novos insights criativos, que só são salvos após aprovação.
5. **Interface TUI:** O córtex sensorial. Uma interface de terminal otimizada em Python, que consome o mínimo de RAM possível.
Filosofia e Diferenciais de Engenharia:
- **Human-in-the-Loop (HITL):** O NEXUS não aprende lixo da internet. Todo conhecimento inserido (seja da Wikipedia, de textos manuais ou de sinapses cruzadas) passa pela curadoria e aprovação do Criador.
- **Privacidade Absoluta:** Nenhuma conversa ou dado é enviado para servidores na nuvem. O sistema funciona até em Modo Avião.
- **Evolução Dirigida por Restrições:** O sistema foi otimizado para superar as limitações de um smartphone, usando scripts leves, requisições HTTP nativas (urllib) e manipulação de arquivos JSON em vez de bancos de dados pesados.
- **Pensamento Cruzado:** O sistema é capaz de unir "Física Quântica + Python", por exemplo, para gerar soluções inovadoras.
O Propósito:
O NEXUS não é apenas um software; é um parceiro de estudos, um programador assistente e um laboratório de ideias. Ele existe para provar que a Inteligência Artificial pode ser pessoal, segura e totalmente independente de grandes corporações, uma espécie de extensão neural!
