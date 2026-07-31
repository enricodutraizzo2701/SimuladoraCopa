import random
import time
import sys
import copy

# ==========================================
# BANCO DE NARRAÇÕES (FLAVOR TEXTS)
# ==========================================
frases_perigo = [
    "UUUUH! O chute venenoso de {jogador} passa tirando tinta da trave!",
    "QUE PERIGO! {jogador} arrisca de fora da área e assusta o goleiro adversário!",
    "DEFESAAAAÇA! O goleiro voa bonito pra espalmar a bomba de {jogador}!",
    "NO TRAVESSÃO! A cabeçada de {jogador} carimba o poste superior! Quase!",
    "SALVA EM CIMA DA LINHA! A zaga tira o pão da boca de {jogador} no último segundo!"
]

frases_habilidade = [
    "🪄 MAGIA EM CAMPO! {jogador} dá uma caneta humilhante no marcador. A torcida vai à loucura!",
    "🎩 QUE CLASSE! {jogador} aplica um chapéu maravilhoso no meio-campo!",
    "🌪️ LISO DEMAIS! {jogador} enfileira dois marcadores com uma facilidade absurda.",
    "🔥 TÁ ON FIRE! {jogador} faz um corta-luz espetacular pra enganar a zaga."
]

frases_clima = [
    "🌧️ O tempo fecha e começa a chover forte no gramado!",
    "🗣️ O técnico do {time} tá esbravejando muito com o quarto árbitro na beira do campo!",
    "🥁 A torcida do {time} canta muito alto e empurra a equipe!",
    "😤 Clima tenso! Muito empurra-empurra na área antes da cobrança de escanteio."
]

def sortear_jogador_por_peso(time_jogadores, acao="gol"):
    if not time_jogadores: return "Jogador Genérico"
    nomes = []
    pesos = []
    for jog in time_jogadores:
        nomes.append(jog['nome'])
        if acao == "gol":
            pos = jog['posicao']
            if pos in ['ATA', 'SA']: pesos.append(60)
            elif pos in ['MEI', 'PE', 'PD']: pesos.append(40)
            elif pos in ['MC', 'ME', 'MD']: pesos.append(25)
            elif pos == 'VOL': pesos.append(10)
            elif pos in ['LE', 'LD', 'ZAG']: pesos.append(5)
            elif pos == 'GOL': pesos.append(1)
            else: pesos.append(10)
        elif acao == "falta":
            pos = jog['posicao']
            if pos in ['ATA', 'SA', 'PE', 'PD']: pesos.append(15)
            elif pos in ['MEI', 'MC', 'ME', 'MD', 'VOL']: pesos.append(40)
            elif pos in ['LE', 'LD', 'ZAG']: pesos.append(45)
            elif pos == 'GOL': pesos.append(0)
            else: pesos.append(20)
    return random.choices(nomes, weights=pesos, k=1)[0]

def sortear_assistencia(time_jogadores, autor_gol):
    possiveis = [j for j in time_jogadores if j['nome'] != autor_gol]
    if not possiveis: return "Sem assistência"
    
    nomes = []
    pesos = []
    for jog in possiveis:
        nomes.append(jog['nome'])
        pos = jog['posicao']
        if pos in ['MEI', 'MC', 'ME', 'MD', 'PE', 'PD', 'SA']: pesos.append(50)
        elif pos in ['VOL', 'LE', 'LD']: pesos.append(30)
        elif pos == 'ATA': pesos.append(15)
        elif pos == 'ZAG': pesos.append(5)
        elif pos == 'GOL': pesos.append(1)
        else: pesos.append(10)
        
    nomes.append("Sem assistência")
    pesos.append(20)
    return random.choices(nomes, weights=pesos, k=1)[0]

def calcular_chance_gol(ataque, defesa, goleiro):
    resistencia = (defesa + goleiro) / 2
    ataque_real = ataque + random.randint(-10, 25) 
    vantagem = ataque_real - resistencia
    return max(1.5, 1.8 + (vantagem * 0.12))

# Ensina o motor a entender os setores do campo
def get_setor(pos):
    pos = pos.upper()
    if pos in ['GOL']: return 'GOL'
    if pos in ['ZAG', 'LE', 'LD', 'DEF', 'LAT']: return 'DEF'
    if pos in ['VOL', 'MC', 'MEI', 'ME', 'MD', 'ML']: return 'MEI'
    if pos in ['ATA', 'SA', 'PE', 'PD', 'CA']: return 'ATA'
    return 'MEI' # Se não souber o que é, joga pro meio-campo

# ==========================================
# MOTOR PRINCIPAL DA PARTIDA
# ==========================================
def simular_partida(time_casa_db, time_fora_db):
    time_casa = copy.deepcopy(time_casa_db)
    time_fora = copy.deepcopy(time_fora_db)
    
    for t in [time_casa, time_fora]:
        t['em_campo'] = [j for j in t['jogadores'] if j.get('status', 'Titular') == 'Titular']
        t['banco'] = [j for j in t['jogadores'] if j.get('status') == 'Reserva']
        if len(t['em_campo']) == len(t['jogadores']):
            t['em_campo'] = t['jogadores'][:11]
            t['banco'] = t['jogadores'][11:]
        t['participaram'] = t['em_campo'].copy()
        t['subs_feitas'] = 0

    estado = {
        "gols_casa": 0, "gols_fora": 0,
        "tempo_perdido": 0, "cartoes_amarelos": [], "eventos": []
    }
    
    dados_exportacao = {
        "time_casa": time_casa["nome"], "time_fora": time_fora["nome"],
        "gols_casa": 0, "gols_fora": 0,
        "detalhes_gols": [], "amarelos": [], "vermelhos": [], "clean_sheets": [],
        "notas_jogadores": {}, "eventos": [], "stats_jogadores": {} 
    }

    dados_exportacao["time_casa_escudo"] = time_casa_db.get("escudo", "https://cdn-icons-png.flaticon.com/512/1041/1041258.png")
    dados_exportacao["time_fora_escudo"] = time_fora_db.get("escudo", "https://cdn-icons-png.flaticon.com/512/1041/1041258.png")

    def penalizar_time(time_alvo, infrator_nome):
        try:
            infrator_obj = next(j for j in time_alvo['em_campo'] if j['nome'] == infrator_nome)
            pos = infrator_obj['posicao']
            impacto = 15
            if pos in ['ATA', 'SA', 'PE', 'PD']: time_alvo['ataque'] -= impacto
            elif pos in ['MEI', 'MC', 'ME', 'MD', 'VOL']: time_alvo['meio'] -= impacto
            elif pos in ['LE', 'LD', 'ZAG']: time_alvo['defesa'] -= impacto
            time_alvo['em_campo'] = [j for j in time_alvo['em_campo'] if j['nome'] != infrator_nome]
        except: pass

    def realizar_substituicao(t_alvo, minuto_disp, motivo="tatico"):
        if t_alvo['subs_feitas'] >= 5 or not t_alvo['banco']: return
        
        # Filtra o banco: Goleiro reserva SÓ ENTRA por lesão!
        opcoes_banco = t_alvo['banco']
        if motivo == "tatico":
            opcoes_banco = [j for j in opcoes_banco if j['posicao'] != 'GOL']
        if not opcoes_banco: return # Banco vazio de linha
        
        entra_obj = random.choice(opcoes_banco)
        setor_entra = get_setor(entra_obj['posicao'])
        
        # Procura alguém no campo do MESMO SETOR pra sair
        candidatos_sair = [j for j in t_alvo['em_campo'] if get_setor(j['posicao']) == setor_entra]
        if not candidatos_sair:
            # Se não achou (ex: time teve zagueiros expulsos), tira qualquer um da linha
            candidatos_sair = [j for j in t_alvo['em_campo'] if j['posicao'] != 'GOL']
            
        if not candidatos_sair: return 
        
        sai_obj = random.choice(candidatos_sair)
        
        # Efetua a troca
        t_alvo['em_campo'].remove(sai_obj)
        t_alvo['banco'].remove(entra_obj)
        t_alvo['em_campo'].append(entra_obj)
        t_alvo['participaram'].append(entra_obj)
        t_alvo['subs_feitas'] += 1
        
        if motivo == "lesao":
            estado["eventos"].append({"minuto": minuto_disp, "texto": f"🚑 QUE AZAR! {sai_obj['nome']} sente o joelho, pede pra sair e não dá mais pra ele. {entra_obj['nome']} entra no {t_alvo['nome']}.", "tipo": "narracao"})
            estado["tempo_perdido"] += 1.5
        else:
            if minuto_disp == "Intervalo":
                estado["eventos"].append({"minuto": "45", "texto": f"🔄 O {t_alvo['nome'].upper()} volta do intervalo com mudança: {entra_obj['nome']} na vaga de {sai_obj['nome']}.", "tipo": "narracao"})
            else:
                estado["eventos"].append({"minuto": minuto_disp, "texto": f"🔄 MUDANÇA NO {t_alvo['nome'].upper()}: Sai {sai_obj['nome']} para a entrada de {entra_obj['nome']}.", "tipo": "narracao"})
            estado["tempo_perdido"] += 0.5

    def aplicar_falta(time_infrator, time_vitima, minuto):
        infrator = sortear_jogador_por_peso(time_infrator['em_campo'], "falta")
        vitima = sortear_jogador_por_peso(time_vitima['em_campo'], "gol")
        goleiro_defensor = next((j['nome'] for j in time_infrator['em_campo'] if j['posicao'] == 'GOL'), "Goleiro")
        
        tipo_falta = random.choices(["jogo", "perigosa", "dura", "penalti"], weights=[55, 25, 15, 5])[0]
        
        if tipo_falta == "jogo":
            estado["eventos"].append({"minuto": minuto, "texto": f"✋ Falta marcada pra o {time_vitima['nome']}.", "tipo": "falta"})
            estado["tempo_perdido"] += 0.5
            
        elif tipo_falta == "perigosa":
            estado["eventos"].append({"minuto": minuto, "texto": f"🚨 Falta PERIGOSA marcada a favor do {time_vitima['nome']}!", "tipo": "falta"})
            estado["tempo_perdido"] += 1.5
            
            if random.uniform(0, 100) <= 15:
                estado["eventos"].append({"minuto": minuto, "texto": f"⚽ GOL DE FALTA do {time_vitima['nome']}! ({vitima})", "tipo": "gol", "equipe": time_vitima['nome']})
                gol_info = {"autor": vitima, "assistencia": "Sem assistência", "time": time_vitima['nome']}
                dados_exportacao["detalhes_gols"].append(gol_info)
                if time_vitima['nome'] == time_casa['nome']: estado["gols_casa"] += 1
                else: estado["gols_fora"] += 1
                
                if random.uniform(0, 100) <= 35:
                    estado["eventos"].append({"minuto": minuto, "texto": "📺 OPA! O VAR tá chamando... O árbitro vai checar um empurrão na barreira!", "tipo": "var_analise"})
                    estado["tempo_perdido"] += 2.0
                    if random.uniform(0, 100) <= 50:
                        estado["eventos"].append({"minuto": minuto, "texto": f"❌ GOL ANULADO! A falta foi revertida por agressão.", "tipo": "var_anulado_gol", "equipe": time_vitima['nome']})
                        if time_vitima['nome'] == time_casa['nome']: estado["gols_casa"] -= 1
                        else: estado["gols_fora"] -= 1
                        dados_exportacao["detalhes_gols"].remove(gol_info)
                    else:
                        estado["eventos"].append({"minuto": minuto, "texto": "✅ GOL CONFIRMADO PELO VAR! Tudo limpo!", "tipo": "var_confirmado"})
            else:
                erro_falta = random.choices(["barreira", "defesa", "fora"], weights=[50, 30, 20])[0]
                if erro_falta == "barreira": estado["eventos"].append({"minuto": minuto, "texto": "Bateu pro gol... e a bola explode na barreira!", "tipo": "narracao"})
                elif erro_falta == "defesa": estado["eventos"].append({"minuto": minuto, "texto": f"Bateu colocado... e o {goleiro_defensor} vai buscar! Defesaça!", "tipo": "narracao"})
                else: estado["eventos"].append({"minuto": minuto, "texto": "Bateu forte demais... isolou a bola na arquibancada!", "tipo": "narracao"})
            
        elif tipo_falta == "penalti":
            estado["eventos"].append({"minuto": minuto, "texto": f"🛑 PÊNALTI PARA O {time_vitima['nome'].upper()}!! O juiz aponta a marca da cal!", "tipo": "falta"})
            var_anulou = False
            if random.uniform(0, 100) <= 35:
                estado["eventos"].append({"minuto": minuto, "texto": f"📺 ESPERA AÍ! O VAR chama o árbitro pra checar se a falta foi dentro da área...", "tipo": "var_analise"})
                estado["tempo_perdido"] += 2.0
                if random.uniform(0, 100) <= 50:
                    estado["eventos"].append({"minuto": minuto, "texto": f"❌ PÊNALTI ANULADO! O árbitro marca a falta fora da área. Segue o jogo!", "tipo": "var_anulado"})
                    var_anulou = True
                else:
                    estado["eventos"].append({"minuto": minuto, "texto": "✅ PÊNALTI CONFIRMADO! Pode botar a bola na marca da cal!", "tipo": "var_confirmado"})
            
            if not var_anulou:
                pos_batedor = next((j['posicao'] for j in time_vitima['em_campo'] if j['nome'] == vitima), 'DEF')
                chance_base = 82 if pos_batedor in ['ATA','SA'] else 72 if pos_batedor in ['MEI','PE','PD'] else 55
                chance_final = chance_base + ((time_vitima['ataque'] - time_infrator['goleiro']) * 0.3)
                
                if random.uniform(0, 100) <= min(95, max(15, chance_final)):
                    estado["eventos"].append({"minuto": minuto, "texto": f"⚽ GOL DE PÊNALTI do {time_vitima['nome']}! ({vitima}) bateu com estilo!", "tipo": "gol", "equipe": time_vitima['nome']})
                    if time_vitima['nome'] == time_casa['nome']: estado["gols_casa"] += 1
                    else: estado["gols_fora"] += 1
                    dados_exportacao["detalhes_gols"].append({"autor": vitima, "assistencia": "Sem assistência", "time": time_vitima['nome']})
                else:
                    estado["eventos"].append({"minuto": minuto, "texto": f"❌ PÊNALTI PERDIDO por {vitima}! Decepção total!", "tipo": "falta"})
            estado["tempo_perdido"] += 2
            
        elif tipo_falta == "dura":
            tipo_cartao = random.choices(["amarelo", "vermelho_direto"], weights=[75, 25])[0]
            is_segundo_amarelo = infrator in estado["cartoes_amarelos"]
            
            if tipo_cartao == "amarelo" and not is_segundo_amarelo:
                estado["eventos"].append({"minuto": minuto, "texto": f"🟨 AMARELO pra {infrator}.", "tipo": "cartao", "jogador": infrator, "cor": "amarelo"})
                estado["cartoes_amarelos"].append(infrator)
                dados_exportacao["amarelos"].append({"jogador": infrator, "time": time_infrator["nome"]})
                estado["tempo_perdido"] += 1
            else:
                texto_expulsao = f"🟥 VERMELHO DIRETO! {infrator} foi pro chuveiro mais cedo!" if tipo_cartao == "vermelho_direto" else f"🟨🟥 SEGUNDO AMARELO! {infrator} foi expulso!"
                estado["eventos"].append({"minuto": minuto, "texto": texto_expulsao, "tipo": "cartao", "jogador": infrator, "cor": "vermelho"})
                
                if random.uniform(0, 100) <= 40:
                    estado["eventos"].append({"minuto": minuto, "texto": f"📺 ESPERA AÍ! O VAR chama o árbitro pra revisar a expulsão de {infrator}...", "tipo": "var_analise"})
                    estado["tempo_perdido"] += 2.5
                    if random.uniform(0, 100) <= 50:
                        if is_segundo_amarelo:
                            estado["eventos"].append({"minuto": minuto, "texto": f"🟨 O árbitro volta atrás e anula a falta! {infrator} escapou do segundo amarelo de boa!", "tipo": "var_anulado"})
                        else:
                            estado["eventos"].append({"minuto": minuto, "texto": f"🟨 O árbitro volta atrás, retira o vermelho direto e dá só AMARELO pra {infrator}.", "tipo": "var_anulado"})
                            estado["cartoes_amarelos"].append(infrator)
                            dados_exportacao["amarelos"].append({"jogador": infrator, "time": time_infrator["nome"]})
                    else:
                        estado["eventos"].append({"minuto": minuto, "texto": "✅ DECISÃO MANTIDA PELO VAR! Rua pra ele!", "tipo": "var_confirmado"})
                        dados_exportacao["vermelhos"].append({"jogador": infrator, "time": time_infrator["nome"]})
                        penalizar_time(time_infrator, infrator)
                else:
                    dados_exportacao["vermelhos"].append({"jogador": infrator, "time": time_infrator["nome"]})
                    penalizar_time(time_infrator, infrator)
                    estado["tempo_perdido"] += 2

    def simular_periodo(inicio, fim, is_acrescimo=False):
        for minuto in range(inicio, fim + 1):
            minuto_disp = f"{inicio - 1}+{minuto - inicio + 1}" if is_acrescimo else str(minuto)
            
            # 🕒 REGRA REALISTA DE SUBSTITUIÇÃO
            for t_alvo in [time_casa, time_fora]:
                if t_alvo['subs_feitas'] >= 5 or not t_alvo['banco']: continue
                
                fazer_sub = False
                motivo = "tatico"
                
                if minuto <= 44:
                    if random.randint(1, 1000) <= 3: # 0.3% de chance: SÓ LESÃO
                        fazer_sub = True; motivo = "lesao"
                elif 46 <= minuto <= 64:
                    if random.randint(1, 1000) <= 2: # 0.2% lesão
                        fazer_sub = True; motivo = "lesao"
                    elif random.randint(1, 100) <= 2: # 2% tático adiantado
                        fazer_sub = True
                elif 65 <= minuto <= 80:
                    if random.randint(1, 100) <= 12: # 12% A HORA DO RUSH DAS MUDANÇAS
                        fazer_sub = True
                else: # 81 pra cima
                    if random.randint(1, 100) <= 3: # 3% retranca final
                        fazer_sub = True
                        
                if fazer_sub:
                    realizar_substituicao(t_alvo, minuto_disp, motivo)
            
            if random.randint(1, 100) <= 4:
                t_infrator = random.choice([time_casa, time_fora])
                t_vitima = time_fora if t_infrator == time_casa else time_casa
                aplicar_falta(t_infrator, t_vitima, minuto_disp)
                continue 
            
            dom_casa = time_casa['meio'] + random.randint(-25, 25)
            dom_fora = time_fora['meio'] + random.randint(-25, 25)
            dado = random.uniform(0, 100)
            teve_gol = False
            
            if dom_casa > dom_fora:
                chance = calcular_chance_gol(time_casa['ataque'], time_fora['defesa'], time_fora['goleiro'])
                if dado <= chance and time_casa['em_campo']:
                    autor = sortear_jogador_por_peso(time_casa['em_campo'], "gol")
                    assistente = sortear_assistencia(time_casa['em_campo'], autor)
                    txt_assist = f" (Assist.: {assistente})" if assistente != "Sem assistência" else ""
                    
                    estado["eventos"].append({"minuto": minuto_disp, "texto": f"⚽ GOL do {time_casa['nome']}! ({autor}){txt_assist}", "tipo": "gol", "equipe": time_casa['nome']})
                    estado["gols_casa"] += 1
                    gol_info = {"autor": autor, "assistencia": assistente, "time": time_casa['nome']}
                    dados_exportacao["detalhes_gols"].append(gol_info)
                    
                    if random.uniform(0, 100) <= 35:
                        estado["eventos"].append({"minuto": minuto_disp, "texto": "📺 OPA! O árbitro põe a mão no ouvido! O VAR tá revisando o lance...", "tipo": "var_analise"})
                        estado["tempo_perdido"] += 2.5
                        if random.uniform(0, 100) <= 50: 
                            estado["eventos"].append({"minuto": minuto_disp, "texto": f"❌ GOL ANULADO! O juiz aponta impedimento de {autor}.", "tipo": "var_anulado_gol", "equipe": time_casa['nome']})
                            estado["gols_casa"] -= 1 
                            dados_exportacao["detalhes_gols"].remove(gol_info)
                        else:
                            estado["eventos"].append({"minuto": minuto_disp, "texto": "✅ GOL CONFIRMADO! Tudo legal, pode comemorar!", "tipo": "var_confirmado"})
                    estado["tempo_perdido"] += 1.5
                    teve_gol = True

            elif dom_fora >= dom_casa:
                chance = calcular_chance_gol(time_fora['ataque'], time_casa['defesa'], time_casa['goleiro'])
                if dado <= chance and time_fora['em_campo']:
                    autor = sortear_jogador_por_peso(time_fora['em_campo'], "gol")
                    assistente = sortear_assistencia(time_fora['em_campo'], autor)
                    txt_assist = f" (Assist.: {assistente})" if assistente != "Sem assistência" else ""
                    
                    estado["eventos"].append({"minuto": minuto_disp, "texto": f"⚽ GOL do {time_fora['nome']}! ({autor}){txt_assist}", "tipo": "gol", "equipe": time_fora['nome']})
                    estado["gols_fora"] += 1
                    gol_info = {"autor": autor, "assistencia": assistente, "time": time_fora['nome']}
                    dados_exportacao["detalhes_gols"].append(gol_info)
                    
                    if random.uniform(0, 100) <= 35:
                        estado["eventos"].append({"minuto": minuto_disp, "texto": "📺 OPA! O árbitro põe a mão no ouvido! O VAR tá revisando o lance...", "tipo": "var_analise"})
                        estado["tempo_perdido"] += 2.5
                        if random.uniform(0, 100) <= 50:
                            estado["eventos"].append({"minuto": minuto_disp, "texto": f"❌ GOL ANULADO! Foi pego um impedimento claro de {autor}.", "tipo": "var_anulado_gol", "equipe": time_fora['nome']})
                            estado["gols_fora"] -= 1
                            dados_exportacao["detalhes_gols"].remove(gol_info)
                        else:
                            estado["eventos"].append({"minuto": minuto_disp, "texto": "✅ GOL CONFIRMADO! Segue o jogo, tudo limpo!", "tipo": "var_confirmado"})
                    estado["tempo_perdido"] += 1.5
                    teve_gol = True
            
            if not teve_gol and random.randint(1, 100) <= 3:
                tipo_evento = random.choice(["perigo", "habilidade", "clima"])
                time_atacando = time_casa if dom_casa > dom_fora else time_fora
                jogador_evento = sortear_jogador_por_peso(time_atacando['em_campo'], "gol") if time_atacando['em_campo'] else "Jogador"
                
                if tipo_evento == "perigo": texto = random.choice(frases_perigo).format(jogador=jogador_evento)
                elif tipo_evento == "habilidade": texto = random.choice(frases_habilidade).format(jogador=jogador_evento)
                else: texto = random.choice(frases_clima).format(time=time_atacando['nome'])
                
                estado["eventos"].append({"minuto": minuto_disp, "texto": texto, "tipo": "narracao"})

    # Roda 1º Tempo
    simular_periodo(1, 45)
    acrescimos_1t = min(6, max(1, int(estado["tempo_perdido"])))
    estado["eventos"].append({"minuto": "45", "texto": f"⏱️ FIM DO 1º TEMPO! ({estado['gols_casa']} x {estado['gols_fora']})", "tipo": "intervalo"})
    estado["tempo_perdido"] = 0 
    
    # Avalia substituições no Intervalo (15% de chance de mexer cedo)
    for t_alvo in [time_casa, time_fora]:
        if random.randint(1, 100) <= 15:
            realizar_substituicao(t_alvo, "Intervalo", "tatico")

    # Roda 2º Tempo
    simular_periodo(46, 90)
    acrescimos_2t = min(10, max(1, int(estado["tempo_perdido"])))
    simular_periodo(91, 90 + acrescimos_2t, is_acrescimo=True)
    estado["eventos"].append({"minuto": f"90+{acrescimos_2t}", "texto": "🏁 FIM DE JOGO!", "tipo": "fim"})

    # Geração de Estatísticas Gerais
    total_meio = time_casa_db['meio'] + time_fora_db['meio']
    posse_casa = int((time_casa_db['meio'] / total_meio) * 100) + random.randint(-8, 8)
    posse_casa = max(25, min(75, posse_casa))
    posse_fora = 100 - posse_casa
    
    chutes_c = estado["gols_casa"] + random.randint(3, 10) + (time_casa_db['ataque'] // 15)
    chutes_f = estado["gols_fora"] + random.randint(3, 10) + (time_fora_db['ataque'] // 15)
    
    cgol_c = estado["gols_casa"] + random.randint(0, max(0, chutes_c - estado["gols_casa"] - 1))
    cgol_f = estado["gols_fora"] + random.randint(0, max(0, chutes_f - estado["gols_fora"] - 1))

    defesas_c = max(0, cgol_f - estado["gols_fora"])
    defesas_f = max(0, cgol_c - estado["gols_casa"])

    escanteios_c = random.randint(2, 9)
    escanteios_f = random.randint(2, 9)
    impedimentos_c = random.randint(0, 5)
    impedimentos_f = random.randint(0, 5)

    passes_tot_c = int(posse_casa * random.uniform(7.5, 9.5))
    passes_cert_c = int(passes_tot_c * random.uniform(0.78, 0.91))
    passes_tot_f = int(posse_fora * random.uniform(7.5, 9.5))
    passes_cert_f = int(passes_tot_f * random.uniform(0.78, 0.91))

    faltas_c = random.randint(5, 16)
    faltas_f = random.randint(5, 16)
    cobrancas_falta_c = faltas_f + impedimentos_f
    cobrancas_falta_f = faltas_c + impedimentos_c

    dados_exportacao["estatisticas"] = {
        "posse_casa": posse_casa, "posse_fora": posse_fora,
        "chutes_casa": chutes_c, "chutes_fora": chutes_f,
        "chutes_gol_casa": cgol_c, "chutes_gol_fora": cgol_f,
        "defesas_casa": defesas_c, "defesas_fora": defesas_f,
        "passes_certos_casa": passes_cert_c, "passes_totais_casa": passes_tot_c,
        "passes_certos_fora": passes_cert_f, "passes_totais_fora": passes_tot_f,
        "escanteios_casa": escanteios_c, "escanteios_fora": escanteios_f,
        "impedimentos_casa": impedimentos_c, "impedimentos_fora": impedimentos_f,
        "faltas_casa": faltas_c, "faltas_fora": faltas_f,
        "cobrancas_falta_casa": cobrancas_falta_c, "cobrancas_falta_fora": cobrancas_falta_f
    }

    def calcular_notas_equipe(time_dados, is_casa):
        for jog in time_dados['participaram']:
            nome = jog['nome']
            pos = jog['posicao']
            fator_ovr = (jog['ovr'] - 70) / 20.0 
            
            nota = random.uniform(5.5, 6.5) + fator_ovr
            
            gols_feitos = sum(1 for g in dados_exportacao['detalhes_gols'] if g['autor'] == nome)
            assists = sum(1 for g in dados_exportacao['detalhes_gols'] if g['assistencia'] == nome)
            
            nota += (gols_feitos * 1.5)
            nota += (assists * 1.0)
            
            if nome in estado['cartoes_amarelos']: nota -= 0.5
            if any(v['jogador'] == nome for v in dados_exportacao['vermelhos']): nota -= 1.5
            
            clean_sheet = False
            if (is_casa and estado['gols_fora'] == 0) or (not is_casa and estado['gols_casa'] == 0):
                if pos in ['GOL', 'ZAG', 'LE', 'LD', 'VOL']: nota += 0.8
                clean_sheet = True
            
            defesas_feitas = 0
            if pos == 'GOL':
                defesas_feitas = defesas_c if is_casa else defesas_f
                nota += (defesas_feitas * 0.3)
            
            if gols_feitos == 0 and assists == 0:
                limite = 7.5
                if pos in ['ZAG', 'LE', 'LD']:
                    if clean_sheet: limite = 8.2
                elif pos == 'GOL':
                    limite = min(10.0, 7.5 + (defesas_feitas * 0.4))
                nota = min(nota, limite)
            
            nota_final = round(max(3.0, min(10.0, nota)), 1)
            dados_exportacao['notas_jogadores'][nome] = nota_final
            
            dados_exportacao["stats_jogadores"][nome] = {
                "time": time_dados["nome"], "posicao": pos,
                "gols": gols_feitos, "assistencias": assists, "nota": nota_final,
                "defesas": defesas_feitas, "clean_sheet": 1 if (pos == 'GOL' and clean_sheet) else 0
            }

    calcular_notas_equipe(time_casa, is_casa=True)
    calcular_notas_equipe(time_fora, is_casa=False)

    dados_exportacao["gols_casa"] = estado["gols_casa"]
    dados_exportacao["gols_fora"] = estado["gols_fora"]
    dados_exportacao["eventos"] = estado["eventos"]
    
    return dados_exportacao
