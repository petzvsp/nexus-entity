#!/usr/bin/env python3
import os, sys, time

class C:
    R="\033[0m"; B="\033[1m"; CY="\033[96m"; GR="\033[92m"
    YL="\033[93m"; RD="\033[91m"; MG="\033[95m"; GY="\033[90m"

def clear(): os.system('clear')

def tela_iniciar():
    clear()
    print(f"""
{C.CY}{C.B}
    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
    ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
    ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
{C.R}
{C.GY}    Organismo Cognitivo Digital · v14.0{C.R}
{C.CY}    ────────────────────────────────────────{C.R}
""")
    print(f"  {C.GR}[ ENTER ]{C.R} Iniciar Sistema")
    print(f"  {C.RD}[  0   ]{C.R} Sair\n")
    esc = input(f"  {C.CY}❯{C.R} ")
    return esc

def tela_carregar():
    clear()
    print(f"""
{C.CY}{C.B}  ┌──────────────────────────────────────────────┐
  │             SELEÇÃO DE MEMÓRIA               │
  └──────────────────────────────────────────────┘{C.R}
""")
    # Dados fictícios de progresso
    saves = [
        ("Perfil 01 (Principal)", "82%", "1.2 MB", C.GR),
        ("Perfil 02 (Testes)",    "34%", "400 KB", C.YL),
        ("Perfil 03 (Backup)",    "100%", "2.5 MB", C.CY),
    ]
    
    for i, (nome, prog, size, cor) in enumerate(saves, 1):
        print(f"  {C.GY}[{i}]{C.R} {nome:<22} {cor}{prog:>4}{C.R} {C.GY}({size}){C.R}")
    
    print(f"\n  {C.GY}[0]{C.R} Voltar\n")
    esc = input(f"  {C.CY}Selecione o perfil:{C.R} ")
    return esc

def painel_principal():
    clear()
    print(f"""
{C.CY}{C.B}  ╔══════════════════════════════════════════════╗
  ║              PAINEL PRINCIPAL                ║
  ╚══════════════════════════════════════════════╝{C.R}
""")
    print(f"  {C.CY}1{C.R} · {C.B}💬 Conversar com o NEXUS{C.R}")
    print(f"  {C.CY}2{C.R} · {C.B}🧠 Gerenciar Cérebro{C.R}")
    print(f"  {C.CY}3{C.R} · {C.B}📚 Repositório de Memórias (RAG){C.R}")
    print(f"  {C.CY}4{C.R} · {C.B}⚙️  Controle Autônomo (Sinapses){C.R}")
    print(f"  {C.CY}5{C.R} · {C.B}🌐 Acesso à Rede (APIs){C.R}")
    print(f"  {C.CY}6{C.R} · {C.B}📖 Documentação do Sistema{C.R}")
    print(f"\n  {C.RD}0{C.R} · Desligar\n")
    esc = input(f"  {C.CY}❯{C.R} ")
    return esc

def sub_painel_cerebro():
    clear()
    print(f"""
{C.MG}{C.B}  ┌──────────────────────────────────────────────┐
  │              CENTRAL DO CÉREBRO              │
  └──────────────────────────────────────────────┘{C.R}
""")
    print(f"  {C.GY}Status:{C.R} {C.GR}ONLINE{C.R} | {C.GY}Peso Total:{C.R} {C.YL}12.5{C.R}\n")
    print(f"  {C.MG}1{C.R} · Visualizar Sinapses Cruzadas")
    print(f"  {C.MG}2{C.R} · Auditar Conceitos Aprendidos")
    print(f"  {C.MG}3{C.R} · Excluir Memória Específica")
    print(f"\n  {C.GY}0{C.R} · Voltar ao Painel Principal\n")
    esc = input(f"  {C.MG}❯{C.R} ")
    return esc

def main():
    state = "START"
    
    while True:
        if state == "START":
            esc = tela_iniciar()
            if esc == "0": break
            state = "LOAD"
            
        elif state == "LOAD":
            esc = tela_carregar()
            if esc == "0": 
                state = "START"
            elif esc in ["1", "2", "3"]:
                # Simula um carregamento rápido
                print(f"\n  {C.GY}Carregando dados neurais...{C.R}")
                time.sleep(1)
                state = "MAIN"
                
        elif state == "MAIN":
            esc = painel_principal()
            if esc == "0": break
            elif esc == "2": 
                state = "SUB_CEREBRO"
            elif esc in ["1", "3", "4", "5", "6"]:
                print(f"\n  {C.RD}Módulo em construção. Voltando...{C.R}")
                time.sleep(1)
                state = "MAIN"
                
        elif state == "SUB_CEREBRO":
            esc = sub_painel_cerebro()
            if esc == "0":
                state = "MAIN"
            else:
                print(f"\n  {C.GR}Ação executada. Pressione ENTER.{C.R}")
                input()
                state = "SUB_CEREBRO"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.RD}Sistema abortado.{C.R}\n")
