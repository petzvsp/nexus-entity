#!/data/data/com.termux/files/usr/bin/bash

echo ""
echo "  ╔════════════════════════════════════════════════════╗"
echo "  ║   ⚠️  RESET TOTAL DE MEMÓRIA DO NEXUS              ║"
echo "  ╚════════════════════════════════════════════════════╝"
echo ""
echo "  Isso vai apagar:"
echo "  - Todas as memórias (arquivos .md)"
echo "  - Todas as sinapses e pesos (conhecimento.json)"
echo "  - Históricos de chat"
echo "  - Logs de background"
echo ""
echo "  O código, a interface e o modelo não serão afetados."
echo ""

# Confirmação de segurança
read -p "  Tem certeza que deseja apagar tudo? (digite SIM para confirmar): " confirm
if [ "$confirm" != "SIM" ]; then
    echo ""
    echo "  ❌ Operação cancelada. Nada foi apagado."
    echo ""
    exit 1
fi

echo ""
echo "  [1/4] Parando processos..."
pkill -9 -f sinapse.py 2>/dev/null
pkill -9 -f nexus_tui.py 2>/dev/null

echo "  [2/4] Apagando arquivos de memória e histórico..."
rm -f ~/nexus-system/memoria/topicos/*.md
rm -f ~/nexus-system/memoria/indice.json
rm -f ~/nexus-system/cerebro/conhecimento.json
rm -f ~/nexus-system/cerebro/log_aprendizado.jsonl
rm -f ~/nexus-system/logs/sinapse.log
rm -f ~/nexus-system/logs/auditoria.jsonl
rm -f ~/nexus-system/.ultimo_chat.json

echo "  [3/4] Recriando arquivos base vazios..."
echo '{"itens": [], "mapa": {}}' > ~/nexus-system/memoria/indice.json
echo '{"conceitos": {}, "total_aprovacoes": 0, "total_expansoes": 0}' > ~/nexus-system/cerebro/conhecimento.json
mkdir -p ~/nexus-system/logs

echo "  [4/4] Reset concluído."
echo ""
echo "  ✅ Sistema limpo com sucesso!"
echo "  O cérebro está vazio, pronto para aprender de novo."
echo ""
echo "  Para iniciar a entidade limpa, digite:"
echo "    nexus-entity"
echo ""
