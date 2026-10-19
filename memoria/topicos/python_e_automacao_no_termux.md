# python e automacao no termux

# Python e Automação no Ambiente Termux

## 1. O Ambiente
O NEXUS roda em um smartphone via Termux (Linux ARM). A gestão de recursos é crítica. O modelo de IA consome muita RAM.

## 2. Bibliotecas Padrão Essenciais (Sem pip install)
- `os` e `sys`: Interação com o sistema operacional (limpar tela, sair do programa).
- `json`: Salvar e carregar o Cérebro e o índice do RAG.
- `urllib.request`: Fazer requisições HTTP para APIs externas (Wikipedia) e para o Ollama local.
- `pathlib`: Manipulação segura de caminhos de arquivos (evita erros de sistema).
- `subprocess`: Executar comandos no terminal (ex: checar se o Ollama está rodando com `pgrep`).

## 3. Técnicas de Automação no Android
- **Wake-Lock:** O comando `termux-wake-lock` impede que o Android mate o processo quando a tela apaga.
- **Execução em Background:** Uso de `nohup` e `&` para rodar o script de Sinapse sem travar o terminal principal.
- **Shell Scripting:** O `boot_entity.py` chama o Ollama e o `nexus_tui.py`, gerenciando o ciclo de vida do sistema.

## 4. Boas Práticas no Código
- Evitar loops infinitos sem `time.sleep()` para não queimar a bateria.
- Tratar exceções (`try/except`) em todas as chamadas de rede.
- Salvar arquivos de forma atômica para evitar corrupção de dados.
