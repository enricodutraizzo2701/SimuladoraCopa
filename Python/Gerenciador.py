import csv
import os
import random
import time
from Motor import simular_partida
from historico_copa import hall_da_fama
from sistema_saves import gerenciar_universos

# Variáveis globais para armazenar o universo atual
estatisticas_jogadores = {}
times_copa_atual = {}
nome_universo_atual = ""
grupos_copa = {}

def inicializar_estatisticas():
    estatisticas_jogadores.clear() 
    for nome_time, dados_time in times_copa_atual.items():
        for jogador in dados_time['jogadores']:
            estatisticas_jogadores[jogador['nome']] = {
                "Time": nome_time,
                "Posicao": jogador['posicao'],
                "Jogos": 0, "Gols": 0, "Assistencias": 0,
                "Amarelos": 0, "Vermelhos": 0, "Clean_Sheets": 0,
                "Soma_Notas": 0.0 
            }

def carregar_estatisticas_salvas():
    inicializar_estatisticas()
    nome_arquivo = 'estatisticas_copa.csv'
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, mode='r', encoding='utf-8') as arquivo_csv:
            leitor = csv.DictReader(arquivo_csv)
            for linha in leitor:
                nome = linha['Nome']
                if nome in estatisticas_jogadores:
                    estatisticas_jogadores[nome]['Jogos'] = int(linha['Jogos'])
                    estatisticas_jogadores[nome]['Gols'] = int(linha['Gols'])
                    estatisticas_jogadores[nome]['Assistencias'] = int(linha['Assistencias'])
                    estatisticas_jogadores[nome]['Amarelos'] = int(linha['Amarelos'])
                    estatisticas_jogadores[nome]['Vermelhos'] = int(linha['Vermelhos'])
                    estatisticas_jogadores[nome]['Clean_Sheets'] = int(linha['Clean_Sheets'])
                    estatisticas_jogadores[nome]['Soma_Notas'] = float(linha.get('Soma_Notas', 0.0))

def atualizar_estatisticas(dados_jogo):
    for jogador in times_copa_atual[dados_jogo['time_casa']]['jogadores']:
        estatisticas_jogadores[jogador['nome']]['Jogos'] += 1
    for jogador in times_copa_atual[dados_jogo['time_fora']]['jogadores']:
        estatisticas_jogadores[jogador['nome']]['Jogos'] += 1

    for gol in dados_jogo['detalhes_gols']:
        autor = gol['autor']
        assistencia = gol['assistencia']
        if autor in estatisticas_jogadores:
            estatisticas_jogadores[autor]['Gols'] += 1
        if assistencia not in ["Sem assistência", "Sem assistência (Pênalti)", "Sem assistência (Falta Direta)"]:
            if assistencia in estatisticas_jogadores:
                estatisticas_jogadores[assistencia]['Assistencias'] += 1

    for amarelo in dados_jogo['amarelos']:
        nome_jogador = amarelo['jogador']
        if nome_jogador in estatisticas_jogadores:
            estatisticas_jogadores[nome_jogador]['Amarelos'] += 1
            
    for vermelho in dados_jogo['vermelhos']:
        nome_jogador = vermelho['jogador']
        if nome_jogador in estatisticas_jogadores:
            estatisticas_jogadores[nome_jogador]['Vermelhos'] += 1
            
    for cs in dados_jogo['clean_sheets']:
        nome_gk = cs['jogador']
        if nome_gk in estatisticas_jogadores:
            estatisticas_jogadores[nome_gk]['Clean_Sheets'] += 1
            
    if 'notas_jogadores' in dados_jogo:
        for nome_jogador, nota in dados_jogo['notas_jogadores'].items():
            if nome_jogador in estatisticas_jogadores:
                estatisticas_jogadores[nome_jogador]['Soma_Notas'] += nota

def gerar_planilha_csv():
    nome_arquivo = 'estatisticas_copa.csv'
    with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['Nome', 'Time', 'Posicao', 'Jogos', 'Gols', 'Assistencias', 'Amarelos', 'Vermelhos', 'Clean_Sheets', 'Soma_Notas', 'Media_Nota']
        escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
        escritor.writeheader()
        for nome, stats in estatisticas_jogadores.items():
            if stats['Jogos'] > 0:
                linha = {'Nome': nome}
                linha.update(stats)
                linha['Media_Nota'] = round(stats['Soma_Notas'] / stats['Jogos'], 2)
                escritor.writerow(linha)

def exibir_tabela_classificao(tabela_grupo):
    print("\n" + "="*70)
    print(f" 📊 TABELA DE CLASSIFICAÇÃO FINAL DO GRUPO ")
    print("="*70)
    print(f"{'Pos':<4} | {'Equipe':<20} | {'Pts':<4} | {'J':<3} | {'V':<3} | {'E':<3} | {'D':<3} | {'GP':<3} | {'GC':<3} | {'SG':<3}")
    print("-" * 70)
    tabela_ordenada = sorted(tabela_grupo.values(), key=lambda x: (x['Pts'], x['SG'], x['GP']), reverse=True)
    for idx, t in enumerate(tabela_ordenada, 1):
        print(f"{idx:<4} | {t['Nome']:<20} | {t['Pts']:<4} | {t['J']:<3} | {t['V']:<3} | {t['E']:<3} | {t['D']:<3} | {t['GP']:<3} | {t['GC']:<3} | {t['SG']:<3}")
    print("="*70 + "\n")
    return tabela_ordenada

def exibir_hall_da_fama():
    print("\n" + "="*55)
    print(" 🏛️ HALL DA FAMA - COPA DO MUNDO DE PARÓDIA 🏛️")
    print("="*55)
    for edicao, dados in hall_da_fama.items():
        if edicao != "Titulos_Totais":
            print(f"[{edicao}]")
            print(f" 🥇 Campeão: {dados.get('Campeao', 'Não registrado')}")
            print(f" 🥈 Vice:    {dados.get('Vice', 'Não registrado')}")
            print(f" 🌟 Bola de Ouro (MOTT): {dados.get('Melhor_Jogador', 'Não registrado')}")
            print(f" ⚽ Artilheiro: {dados.get('Artilheiro', 'Não registrado')}")
            print(f" 👟 Rei das Assistências: {dados.get('Assistente', 'Não registrado')}")
            print(f" 🧤 Luva de Ouro (Clean Sheets): {dados.get('Melhor_Goleiro', 'Não registrado')}")
            print("-" * 55)

def simular_fase_de_grupos(nome_grupo):
    times_do_grupo = grupos_copa[nome_grupo]
    tabela_grupo = {}
    for nome_t in times_do_grupo:
        tabela_grupo[nome_t] = {"Nome": nome_t, "Pts": 0, "J": 0, "V": 0, "E": 0, "D": 0, "GP": 0, "GC": 0, "SG": 0}

    print(f"\n🏆 INICIANDO A SIMULAÇÃO DO {nome_grupo.upper()} 🏆\n")
    print(f"Equipes participantes: {', '.join(times_do_grupo)}\n")
    time.sleep(2)
    
    for i in range(len(times_do_grupo)):
        for j in range(i + 1, len(times_do_grupo)):
            nome_time_casa = times_do_grupo[i]
            nome_time_fora = times_do_grupo[j]
            time_casa = times_copa_atual[nome_time_casa]
            time_fora = times_copa_atual[nome_time_fora]
            
            dados_jogo = simular_partida(time_casa, time_fora)
            atualizar_estatisticas(dados_jogo)
            
            gols_c = dados_jogo['gols_casa']
            gols_f = dados_jogo['gols_fora']
            
            tabela_grupo[nome_time_casa]['J'] += 1
            tabela_grupo[nome_time_fora]['J'] += 1
            tabela_grupo[nome_time_casa]['GP'] += gols_c
            tabela_grupo[nome_time_casa]['GC'] += gols_f
            tabela_grupo[nome_time_fora]['GP'] += gols_f
            tabela_grupo[nome_time_fora]['GC'] += gols_c
            tabela_grupo[nome_time_casa]['SG'] = tabela_grupo[nome_time_casa]['GP'] - tabela_grupo[nome_time_casa]['GC']
            tabela_grupo[nome_time_fora]['SG'] = tabela_grupo[nome_time_fora]['GP'] - tabela_grupo[nome_time_fora]['GC']
            
            if gols_c > gols_f:
                tabela_grupo[nome_time_casa]['V'] += 1
                tabela_grupo[nome_time_casa]['Pts'] += 3
                tabela_grupo[nome_time_fora]['D'] += 1
            elif gols_f > gols_c:
                tabela_grupo[nome_time_fora]['V'] += 1
                tabela_grupo[nome_time_fora]['Pts'] += 3
                tabela_grupo[nome_time_casa]['D'] += 1
            else:
                tabela_grupo[nome_time_casa]['E'] += 1
                tabela_grupo[nome_time_casa]['Pts'] += 1
                tabela_grupo[nome_time_fora]['E'] += 1
                tabela_grupo[nome_time_fora]['Pts'] += 1

            print("\n" + "="*55)
            continuar = input("➡️ Pressione ENTER para simular o próximo jogo (ou digite 'sair'): ")
            if continuar.lower() == 'sair':
                print("\nSimulação interrompida pelo usuário.\n")
                return None

    tabela_ordenada = exibir_tabela_classificao(tabela_grupo)
    return [tabela_ordenada[0]['Nome'], tabela_ordenada[1]['Nome']]


# ==========================================
# NOVO: MOTOR DE DISPUTA DE PÊNALTIS
# ==========================================
def disputa_de_penaltis(time_a_dict, time_b_dict):
    print("\n" + "="*50)
    print(" ⚽ DISPUTA DE PÊNALTIS ⚽")
    print("="*50)
    time.sleep(2)
    
    placar = {time_a_dict['nome']: 0, time_b_dict['nome']: 0}
    cobrancas = {time_a_dict['nome']: 0, time_b_dict['nome']: 0}
    
    # Sorteia a ordem dos cobradores (tirando os goleiros, que só batem em último caso)
    batedores_a = [j['nome'] for j in time_a_dict['jogadores'] if j['posicao'] != 'GOL']
    batedores_b = [j['nome'] for j in time_b_dict['jogadores'] if j['posicao'] != 'GOL']
    random.shuffle(batedores_a)
    random.shuffle(batedores_b)
    
    goleiro_a = next((j['nome'] for j in time_a_dict['jogadores'] if j['posicao'] == 'GOL'), "Goleiro A")
    goleiro_b = next((j['nome'] for j in time_b_dict['jogadores'] if j['posicao'] == 'GOL'), "Goleiro B")
    
    # Adiciona os goleiros no final da lista, caso vá longe demais nas alternadas
    batedores_a.append(goleiro_a)
    batedores_b.append(goleiro_b)
    
    def cobrar_um_penalti(time_batedor_nome, batedor, goleiro_defensor, time_batedor_dict, time_defensor_dict):
        print(f"\n[{time_batedor_nome}] - {batedor} ajeita a bola...")
        time.sleep(1.5)
        print("Correu, partiu, bateu...")
        time.sleep(1.5)
        
        chance = 75 + ((time_batedor_dict['ataque'] - time_defensor_dict['goleiro']) * 0.5)
        chance = max(20, min(95, chance))
        
        if random.uniform(0, 100) <= chance:
            print(f"⚽ GOOOOOOOOLLLL!!! {batedor} guarda no fundo da rede!")
            return True
        else:
            erro = random.choices(["defesa", "trave", "fora"], weights=[60, 20, 20])[0]
            if erro == "defesa":
                print(f"🧤 ESPALMAAAA {goleiro_defensor}!!! Defesa espetacular!")
            elif erro == "trave":
                print("💥 NA TRAVE!!! A bola explode no poste!")
            else:
                print("❌ ISOLOU!!! Mandou lá na arquibancada!")
            return False

    rodada = 1
    idx_batedor = 0
    
    # FASE 1: 5 COBRANÇAS NORMAIS
    while rodada <= 5:
        print(f"\n--- {rodada}ª RODADA ---")
        time.sleep(1)
        
        # Cobrança do Time A
        if cobrar_um_penalti(time_a_dict['nome'], batedores_a[idx_batedor % len(batedores_a)], goleiro_b, time_a_dict, time_b_dict):
            placar[time_a_dict['nome']] += 1
        cobrancas[time_a_dict['nome']] += 1
        print(f"📊 Placar: {time_a_dict['nome']} {placar[time_a_dict['nome']]} x {placar[time_b_dict['nome']]} {time_b_dict['nome']}")
        time.sleep(1.5)
        
        # Verifica se B já não pode mais alcançar A matematicamente
        restantes_b = 5 - cobrancas[time_b_dict['nome']]
        if placar[time_a_dict['nome']] > placar[time_b_dict['nome']] + restantes_b:
            break
            
        # Cobrança do Time B
        if cobrar_um_penalti(time_b_dict['nome'], batedores_b[idx_batedor % len(batedores_b)], goleiro_a, time_b_dict, time_a_dict):
            placar[time_b_dict['nome']] += 1
        cobrancas[time_b_dict['nome']] += 1
        print(f"📊 Placar: {time_a_dict['nome']} {placar[time_a_dict['nome']]} x {placar[time_b_dict['nome']]} {time_b_dict['nome']}")
        time.sleep(1.5)
        
        # Verifica se A já não pode mais alcançar B matematicamente
        restantes_a = 5 - cobrancas[time_a_dict['nome']]
        if placar[time_b_dict['nome']] > placar[time_a_dict['nome']] + restantes_a:
            break
            
        rodada += 1
        idx_batedor += 1
        
    # FASE 2: COBRANÇAS ALTERNADAS (MORTE SÚBITA)
    if placar[time_a_dict['nome']] == placar[time_b_dict['nome']]:
        print("\n" + "="*50)
        print(" 😱 EMPATE! VAMOS PARA AS COBRANÇAS ALTERNADAS (MORTE SÚBITA)! ")
        print("="*50)
        time.sleep(2)
        
        while placar[time_a_dict['nome']] == placar[time_b_dict['nome']]:
            print(f"\n--- MORTE SÚBITA ---")
            
            # Cobrança A
            if cobrar_um_penalti(time_a_dict['nome'], batedores_a[idx_batedor % len(batedores_a)], goleiro_b, time_a_dict, time_b_dict):
                placar[time_a_dict['nome']] += 1
            
            # Cobrança B
            if cobrar_um_penalti(time_b_dict['nome'], batedores_b[idx_batedor % len(batedores_b)], goleiro_a, time_b_dict, time_a_dict):
                placar[time_b_dict['nome']] += 1
                
            print(f"📊 Placar: {time_a_dict['nome']} {placar[time_a_dict['nome']]} x {placar[time_b_dict['nome']]} {time_b_dict['nome']}")
            time.sleep(1.5)
            idx_batedor += 1

    print("\n" + "="*50)
    print(" 🏁 FIM DA DISPUTA DE PÊNALTIS! 🏁")
    print(f" PLACAR FINAL: {time_a_dict['nome']} {placar[time_a_dict['nome']]} x {placar[time_b_dict['nome']]} {time_b_dict['nome']}")
    print("="*50)
    
    vencedor = time_a_dict['nome'] if placar[time_a_dict['nome']] > placar[time_b_dict['nome']] else time_b_dict['nome']
    return vencedor


def simular_jogo_mata_mata(nome_time_a, nome_time_b, fase_nome):
    print(f"\n🔥 {fase_nome.upper()} 🔥")
    time_a = times_copa_atual[nome_time_a]
    time_b = times_copa_atual[nome_time_b]
    
    dados_jogo = simular_partida(time_a, time_b)
    atualizar_estatisticas(dados_jogo)
    
    gols_a = dados_jogo['gols_casa']
    gols_b = dados_jogo['gols_fora']
    
    # 🧠 Lógica para a mensagem correta no fim de jogo
    is_final = "final" in fase_nome.lower() and fase_nome.lower() not in ["oitavas de final", "quartas de final", "semifinal", "oitavos de final", "quartos de final"]
    mensagem_vitoria = "É CAMPEÃO DO TORNEIO! 🏆" if is_final else "avança de fase! 🚀"
    
    if gols_a != gols_b:
        vencedor = nome_time_a if gols_a > gols_b else nome_time_b
        print(f"🎯 Fim do tempo regulamentar! Vencedor do confronto: **{vencedor}**")
        print(f"🎯 **{vencedor}** {mensagem_vitoria}\n")
        return vencedor
    else:
        print(f"\n⚖️ EMPATE EM {gols_a}x{gols_b}! A partida vai para a DISPUTA DE PÊNALTIS!\n")
        time.sleep(2)
        
        # Chama a nova função super emocionante
        vencedor = disputa_de_penaltis(time_a, time_b)
        
        print(f"\n🎯 **{vencedor}** {mensagem_vitoria}\n")
        return vencedor

def iniciar_torneio_completo():
    lista_equipas = list(times_copa_atual.keys())
    if len(lista_equipas) < 8:
        print("\n❌ Você precisa de pelo menos 8 equipes no seu Universo para realizar um torneio em condições!\n")
        return

    print("\n" + "="*50)
    print(" 🎲 SORTEIO OFICIAL DA COPA DO MUNDO 🎲")
    print("="*50)
    time.sleep(1.5)

    random.shuffle(lista_equipas)
    
    num_grupos = max(2, len(lista_equipas) // 4)
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    global grupos_copa
    grupos_copa = {}
    for i in range(num_grupos):
        grupos_copa[f"Grupo {letras[i]}"] = []

    for i, equipa in enumerate(lista_equipas):
        nome_grupo = f"Grupo {letras[i % num_grupos]}"
        grupos_copa[nome_grupo].append(equipa)

    for nome_g, equipas_g in grupos_copa.items():
        print(f"\n{nome_g}: {', '.join(equipas_g)}")
        time.sleep(0.8)

    input("\n➡️ Pressione ENTER para começar a Fase de Grupos! ")

    classificados = {}
    for nome_g in grupos_copa.keys():
        vencedores = simular_fase_de_grupos(nome_g)
        if not vencedores: return 
        classificados[nome_g] = vencedores
        gerar_planilha_csv()

    print("\n" + "="*50)
    print(" 🏆 FASE DE GRUPOS CONCLUÍDA! AVANÇANDO PARA O MATA-MATA... ")
    print("="*50)
    input("➡️ Pressione ENTER para iniciar o Sorteio e os confrontos! ")

    pote_1 = [classificados[g][0] for g in classificados]
    pote_2 = [classificados[g][1] for g in classificados]
    random.shuffle(pote_1)
    random.shuffle(pote_2)

    confrontos_atuais = []
    for i in range(len(pote_1)):
        confrontos_atuais.append((pote_1[i], pote_2[i]))

    while len(confrontos_atuais) > 0:
        qtd_jogos = len(confrontos_atuais)
        if qtd_jogos >= 8: nome_fase = "Oitavas de Final"
        elif qtd_jogos >= 4: nome_fase = "Quartas de Final"
        elif qtd_jogos == 2: nome_fase = "Semifinal"
        elif qtd_jogos == 1: nome_fase = "GRANDE FINAL"
        else: nome_fase = f"Mata-Mata ({qtd_jogos} jogos)"

        print("\n" + "="*50)
        print(f" 🔥 INICIANDO A FASE: {nome_fase.upper()} 🔥")
        print("="*50)
        time.sleep(1.5)

        proxima_fase = []
        for i in range(0, len(confrontos_atuais), 2):
            t1, t2 = confrontos_atuais[i]
            
            if qtd_jogos == 1:
                campeao = simular_jogo_mata_mata(t1, t2, nome_fase)
                vice = t2 if campeao == t1 else t1
                gerar_planilha_csv()
                print("\n🎉 O TORNEIO TERMINOU! 🎉")
                input("➡️ Pressione ENTER para iniciar a Cerimônia de Encerramento... ")
                encerrar_copa_e_salvar_historico(campeao, vice)
                return 
            
            vencedor1 = simular_jogo_mata_mata(t1, t2, nome_fase)
            gerar_planilha_csv()

            if i + 1 < len(confrontos_atuais):
                t3, t4 = confrontos_atuais[i+1]
                vencedor2 = simular_jogo_mata_mata(t3, t4, nome_fase)
                gerar_planilha_csv()
                proxima_fase.append((vencedor1, vencedor2))
            else:
                proxima_fase.append((vencedor1, "Time Fantasma"))

        confrontos_atuais = proxima_fase
        input(f"\n➡️ Pressione ENTER para avançar para a próxima fase! ")

def encerrar_copa_e_salvar_historico(campeao_auto=None, vice_auto=None):
    print("\n--- 🏆 CERIMÔNIA DE ENCERRAMENTO 🏆 ---")
    
    if campeao_auto and vice_auto:
        campeao = campeao_auto
        vice = vice_auto
    else:
        campeao = input("Digite o nome exato do time CAMPEÃO: ")
        vice = input("Digite o nome exato do time VICE-CAMPEÃO: ")

    artilheiro, max_gols = "Ninguém", 0
    assistente, max_assist = "Ninguém", 0
    melhor_goleiro, max_cs = "Ninguém", -1
    melhor_jogador, max_media = "Ninguém", 0.0

    for nome, stats in estatisticas_jogadores.items():
        if stats['Gols'] > max_gols:
            max_gols = stats['Gols']
            artilheiro = nome
        if stats['Assistencias'] > max_assist:
            max_assist = stats['Assistencias']
            assistente = nome
        if stats['Posicao'] == 'GOL' and stats['Clean_Sheets'] > max_cs:
            max_cs = stats['Clean_Sheets']
            melhor_goleiro = nome
            
        if stats['Jogos'] >= 3:
            media = round(stats['Soma_Notas'] / stats['Jogos'], 2)
            if media > max_media:
                max_media = media
                melhor_jogador = nome

    if melhor_jogador == "Ninguém":
        for nome, stats in estatisticas_jogadores.items():
            if stats['Jogos'] > 0:
                media = round(stats['Soma_Notas'] / stats['Jogos'], 2)
                if media > max_media:
                    max_media = media
                    melhor_jogador = nome

    txt_artilheiro = f"{artilheiro} ({max_gols} Gols)" if max_gols > 0 else "Ninguém"
    txt_assistente = f"{assistente} ({max_assist} Assistências)" if max_assist > 0 else "Ninguém"
    txt_goleiro = f"{melhor_goleiro} ({max_cs} Clean Sheets)" if max_cs >= 0 else "Ninguém"
    txt_melhor_jogador = f"{melhor_jogador} (Média: {max_media})" if max_media > 0 else "Ninguém"

    num_edicao = len([k for k in hall_da_fama.keys() if "Edicao" in k]) + 1
    nome_edicao = f"Edicao_{num_edicao}"

    hall_da_fama[nome_edicao] = {
        "Campeao": campeao, "Vice": vice,
        "Melhor_Jogador": txt_melhor_jogador,
        "Artilheiro": txt_artilheiro, "Assistente": txt_assistente, "Melhor_Goleiro": txt_goleiro
    }

    if campeao in hall_da_fama["Titulos_Totais"]:
        hall_da_fama["Titulos_Totais"][campeao] += 1
    else:
        hall_da_fama["Titulos_Totais"][campeao] = 1

    import pprint
    with open("historico_copa.py", "w", encoding="utf-8") as f:
        f.write("# ==========================================\n")
        f.write("# BANCO DE DADOS - HISTÓRICO DA COPA\n")
        f.write("# ==========================================\n\n")
        f.write("hall_da_fama = " + pprint.pformat(hall_da_fama) + "\n")

    print("\n🏆 COPA ENCERRADA E DADOS GUARDADOS NO HALL DA FAMA COM SUCESSO! 🏆")
    print(f"🥇 Campeão: {campeao}")
    print(f"🥈 Vice: {vice}")
    print(f"🌟 Bola de Ouro: {txt_melhor_jogador}")
    print(f"⚽ Artilheiro: {txt_artilheiro}")
    print(f"👟 Assistente: {txt_assistente}")
    print(f"🧤 Luva de Ouro: {txt_goleiro}\n")

def resetar_historico_copa():
    confirmacao = input("\n⚠️ TEM CERTEZA que deseja apagar todo o Hall da Fama? (s/n): ").strip().lower()
    if confirmacao == 's':
        conteudo_zerado = """# ==========================================
# BANCO DE DADOS - HISTÓRICO DA COPA
# ==========================================

hall_da_fama = {
    "Titulos_Totais": {}
}
"""
        with open("historico_copa.py", "w", encoding="utf-8") as f:
            f.write(conteudo_zerado)
        print("🧹 HISTÓRICO RESETADO COM SUCESSO! O Hall da Fama está limpo para a Edição 1 oficial.\n")
        hall_da_fama.clear()
        hall_da_fama["Titulos_Totais"] = {}
    else:
        print("Operação de reset cancelada.\n")

# ==========================================
# FLUXO PRINCIPAL DO GERENCIADOR
# ==========================================
if __name__ == "__main__":
    print("🏆 BEM-VINDO AO GERENCIADOR DA COPA DE PARÓDIA 🏆\n")
    
    while True:
        times_copa_atual, nome_universo_atual = gerenciar_universos()
        if times_copa_atual is not None:
            break
        print("\nVocê precisa carregar um universo para poder jogar!\n")
    
    print(f"\n🌌 SISTEMA INICIADO NO MULTIVERSO: {nome_universo_atual} 🌌\n")
    
    limpar = input("Deseja apagar os dados de artilharia anteriores e zerar a planilha CSV? (s/n): ").strip().lower()
    if limpar == 's':
        if os.path.exists('estatisticas_copa.csv'):
            os.remove('estatisticas_copa.csv')
            print("🗑️ Dados anteriores apagados com sucesso! Começando do zero.\n")
            
    carregar_estatisticas_salvas()
            
    while True:
        print("\n" + "="*50)
        print(f" MODO DE OPERAÇÃO (Universo: {nome_universo_atual})")
        print("="*50)
        print("1 - 🎲 Iniciar Torneio Completo (Sorteio Automático e Chaveamento)")
        print("2 - Simular Jogo Único de Mata-Mata (Manual)")
        print("3 - Ver Hall da Fama (Histórico de Campeões)")
        print("4 - 🏆 Encerrar a Copa Manualmente")
        print("5 - 🧹 Resetar o Hall da Fama (Começar do Zero)")
        print("6 - 🌌 Trocar de Universo / Editar Times")
        print("7 - ❌ Sair do Gerenciador")
        print("="*50)
        
        escolha = input("\nDigite o número da sua escolha: ")
        
        if escolha == '1':
            iniciar_torneio_completo()
                
        elif escolha == '2':
            print("\n--- MODO MATA-MATA (MANUAL) ---")
            time1 = input("Digite o nome exato do Time 1: ")
            time2 = input("Digite o nome exato do Time 2: ")
            fase = input("Digite o nome da fase (Ex: Amistoso, Final): ")
            
            if time1 in times_copa_atual and time2 in times_copa_atual:
                simular_jogo_mata_mata(time1, time2, fase)
                gerar_planilha_csv()
            else:
                print(f"\n❌ ERRO: Um dos times não foi encontrado no {nome_universo_atual}.\n")
                
        elif escolha == '3':
            exibir_hall_da_fama()
            
        elif escolha == '4':
            encerrar_copa_e_salvar_historico()
            
        elif escolha == '5':
            resetar_historico_copa()
            
        elif escolha == '6':
            novo_times, novo_nome = gerenciar_universos()
            if novo_times:
                times_copa_atual = novo_times
                nome_universo_atual = novo_nome
                print(f"\n🔄 Universo trocado para: {nome_universo_atual}\n")
                
        elif escolha == '7':
            print("\n👋 Encerrando o Gerenciador... Até a próxima Copa!\n")
            break
            
        else:
            print("\n❌ Opção inválida. Tente novamente.\n")
