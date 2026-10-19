#!/data/data/com.termux/files/usr/bin/bash
DATA=$(date +"%Y%m%d_%H%M%S")
ARQUIVO="nexus_backup_$DATA.tar.gz"
DESTINO="$HOME/storage/shared/Documents"

echo ""
echo "Iniciando backup do NEXUS..."
pkill -9 -f sinapse.py 2>/dev/null
echo "Processos pausados."

tar -czf "$DESTINO/$ARQUIVO" -C ~ nexus-system

if [ -f "$DESTINO/$ARQUIVO" ]; then
    echo "BACKUP CONCLUIDO COM SUCESSO!"
    echo "Salvo em: Documents/$ARQUIVO"
else
    echo "ERRO: O backup falhou."
fi

nohup python ~/nexus-system/sinapse.py > /dev/null 2>&1 &
echo "Processos do NEXUS reiniciados."
echo ""
