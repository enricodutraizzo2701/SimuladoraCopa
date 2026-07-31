import os
import json
import shutil
import sys

try:
    from banco_de_dados import times_copa
except ImportError:
    times_copa = {}

PASTA_SAVES = "saves"

def inicializar_saves():
    """Garante que a pasta de saves e o Universo Base existam."""
    if not os.path.exists(PASTA_SAVES):
        os.makedirs(PASTA_SAVES)
    
    caminho_base = os.path.join(PASTA_SAVES, "universo_base.json")
    if not os.path.exists(caminho_base):
        with open(caminho_base, 'w', encoding='utf-8') as f:
            json.dump(times_copa, f, indent=4, ensure_ascii=False)

def listar_universos():
    """Lista todos os arquivos .json na pasta de saves."""
    return [f for f in os.listdir(PASTA_SAVES) if f.endswith('.json')]

def gerenciar_universos():
    """Menu principal do Sistema de Multiversos."""
    inicializar_saves()
    
    while True:
        print("\n" + "="*50)
        print(" 🌌 GERENCIADOR DE UNIVERSOS (DATASAVES) 🌌")
        print("="*50)
        print("1 - Carregar Universo Existente (Jogar)")
        print("2 - Criar Novo Universo")
        print("3 - Editar um Universo (CRUD)")
        print("4 - Excluir Universo")
        print("5 - Voltar ao Menu Principal")
        print("6 - ❌ Sair do Programa")
        print("="*50)
        
        escolha = input("\nDigite sua escolha: ")
        
        if escolha == '1':
            universos = listar_universos()
            print("\n--- UNIVERSOS DISPONÍVEIS ---")
            for i, u in enumerate(universos, 1):
                print(f"{i} - {u.replace('.json', '')}")
            
            try:
                sel = int(input("\nDigite o número do Universo que deseja carregar: "))
                if 1 <= sel <= len(universos):
                    caminho = os.path.join(PASTA_SAVES, universos[sel-1])
                    with open(caminho, 'r', encoding='utf-8') as f:
                        dados_universo = json.load(f)
                    print(f"\n✅ Universo '{universos[sel-1]}' carregado com sucesso!")
                    return dados_universo, universos[sel-1].replace('.json', '')
                else:
                    print("❌ Opção inválida.")
            except ValueError:
                print("❌ Digite um número válido.")
                
        elif escolha == '2':
            nome_novo = input("\nDigite o nome do seu Novo Universo (ex: copa_anime): ").strip().replace(" ", "_")
            if not nome_novo:
                continue
            
            caminho_novo = os.path.join(PASTA_SAVES, f"{nome_novo}.json")
            if os.path.exists(caminho_novo):
                print("❌ Esse universo já existe!")
            else:
                with open(caminho_novo, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                print(f"\n✅ Universo '{nome_novo}' criado! Abrindo painel de edição para você adicionar times...")
                menu_crud_times(f"{nome_novo}.json")

        elif escolha == '3':
            universos = listar_universos()
            print("\n--- EDITAR UNIVERSO ---")
            for i, u in enumerate(universos, 1):
                print(f"{i} - {u.replace('.json', '')}")
                
            try:
                sel = int(input("\nQual universo deseja editar? "))
                if 1 <= sel <= len(universos):
                    nome_arquivo = universos[sel-1]
                    if nome_arquivo == "universo_base.json":
                        print("❌ O Universo Base não pode ser editado. Crie um novo baseado nele!")
                    else:
                        menu_crud_times(nome_arquivo)
                else:
                    print("❌ Opção inválida.")
            except ValueError:
                print("❌ Digite um número válido.")

        elif escolha == '4':
            universos = listar_universos()
            print("\n--- EXCLUIR UNIVERSO ---")
            for i, u in enumerate(universos, 1):
                print(f"{i} - {u.replace('.json', '')}")
                
            try:
                sel = int(input("\nQual universo deseja EXCLUIR? "))
                if 1 <= sel <= len(universos):
                    nome_arquivo = universos[sel-1]
                    if nome_arquivo == "universo_base.json":
                        print("❌ O Universo Base NUNCA pode ser excluído.")
                    else:
                        confirmacao = input(f"⚠️ Tem certeza que deseja DELETAR '{nome_arquivo}'? (s/n): ").lower()
                        if confirmacao == 's':
                            os.remove(os.path.join(PASTA_SAVES, nome_arquivo))
                            print(f"\n🗑️ Universo {nome_arquivo} excluído com sucesso!")
                else:
                    print("❌ Opção inválida.")
            except ValueError:
                print("❌ Digite um número válido.")
                
        elif escolha == '5':
            return None, None
            
        elif escolha == '6':
            print("\n👋 Encerrando o programa diretamente do Gerenciador de Universos...\n")
            sys.exit(0)

def menu_crud_times(nome_arquivo):
    """Menu para adicionar, remover ou importar times dentro de um Universo."""
    caminho = os.path.join(PASTA_SAVES, nome_arquivo)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        
    caminho_base = os.path.join(PASTA_SAVES, "universo_base.json")
    with open(caminho_base, 'r', encoding='utf-8') as f_base:
        banco_base = json.load(f_base)
        
    while True:
        print(f"\n🛠️ EDITANDO: {nome_arquivo} (Times atuais: {len(dados)})")
        print("1 - Listar Times e Overalls do seu Universo")
        print("2 - Criar Time do Zero (com Elenco)")
        print("3 - 📥 Importar Time do Universo Base")
        print("4 - Remover Time")
        print("5 - Salvar e Voltar")
        
        opc = input("Escolha: ")
        
        if opc == '1':
            print("\n--- TIMES NO UNIVERSO ---")
            if len(dados) == 0:
                print("Nenhum time adicionado ainda.")
            for time, info in dados.items():
                # CORRIGIDO AQUI: info.get('meio', 0) em vez de 'meio_campo'
                print(f"[{time}] - Ataque: {info.get('ataque', 0)} | Meio: {info.get('meio', 0)} | Defesa: {info.get('defesa', 0)} | Goleiro: {info.get('goleiro', 0)}")
                
        elif opc == '2':
            nome_time = input("\nNome do Time (ex: Real Madrid): ").strip()
            ataque = int(input("Força do Ataque (1-99): "))
            meio = int(input("Força do Meio-Campo (1-99): "))
            defesa = int(input("Força da Defesa (1-99): "))
            goleiro = int(input("Força do Goleiro (1-99): "))
            
            jogadores = []
            print("\n--- MONTANDO O ELENCO ---")
            print("Digite as informações dos jogadores. Quando quiser parar, digite 'fim' no nome.")
            
            while True:
                nome_j = input("\nNome do Jogador (ou 'fim' para terminar): ").strip()
                if nome_j.lower() == 'fim':
                    if len(jogadores) == 0:
                        print("⚠️ Você precisa adicionar pelo menos 1 jogador!")
                        continue
                    break
                    
                pos_j = input("Posição (ex: ATA, MEI, DEF, GOL): ").strip().upper()
                
                try:
                    ovr_j = int(input("Overall do Jogador (1-99): "))
                except ValueError:
                    print("❌ Valor inválido. Digite um número para o Overall.")
                    continue
                
                jogadores.append({"nome": nome_j, "posicao": pos_j, "ovr": ovr_j})
                print(f"✅ Jogador '{nome_j}' adicionado ao {nome_time}!")
            
            dados[nome_time] = {
                "nome": nome_time, # Adicionado o nome dentro do dicionário para compatibilidade com o motor
                "ataque": ataque,
                "meio": meio,      # CORRIGIDO AQUI TAMBÉM
                "defesa": defesa,
                "goleiro": goleiro,
                "jogadores": jogadores
            }
            print(f"\n✅ Time '{nome_time}' completo com {len(jogadores)} jogador(es) salvo na memória!")
            
        elif opc == '3':
            print("\n--- 📥 VITRINE DO UNIVERSO BASE ---")
            lista_base = list(banco_base.keys())
            for i, t in enumerate(lista_base, 1):
                status = "✅ (Já no seu universo)" if t in dados else ""
                print(f"{i} - {t} {status}")
                
            escolha_time = input("\nDigite o número do time que deseja importar (ou '0' para cancelar): ")
            try:
                idx = int(escolha_time)
                if 1 <= idx <= len(lista_base):
                    nome_time_escolhido = lista_base[idx-1]
                    if nome_time_escolhido in dados:
                        print(f"⚠️ O time '{nome_time_escolhido}' já está no seu Universo!")
                    else:
                        dados[nome_time_escolhido] = banco_base[nome_time_escolhido]
                        print(f"✅ O time '{nome_time_escolhido}' e todo o seu elenco foram importados com sucesso!")
                elif idx != 0:
                    print("❌ Número inválido.")
            except ValueError:
                print("❌ Entrada inválida.")
                
        elif opc == '4':
            nome_time = input("\nNome exato do Time a remover: ").strip()
            if nome_time in dados:
                del dados[nome_time]
                print("🗑️ Time removido!")
            else:
                print("❌ Time não encontrado.")
                
        elif opc == '5':
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print("💾 Universo salvo com sucesso!")
            break
