from flask import Flask, render_template, request, redirect, url_for
from historico_copa import hall_da_fama
from Motor import simular_partida
import os
import json
import time

time.sleep = lambda x: None

app = Flask(__name__)

PASTA_SAVES = "saves"
universo_atual_nome = "universo_base.json"

def carregar_times_atuais():
    caminho = os.path.join(PASTA_SAVES, universo_atual_nome)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        from banco_de_dados import times_copa
        return times_copa

def atualizar_estatisticas_globais(torneio, stats_jogo):
    if "estatisticas_globais" not in torneio:
        torneio["estatisticas_globais"] = {}
        
    for nome, stats in stats_jogo.items():
        if nome not in torneio["estatisticas_globais"]:
            torneio["estatisticas_globais"][nome] = {
                "time": stats["time"], "posicao": stats["posicao"],
                "gols": 0, "assistencias": 0, "notas_soma": 0.0, "jogos": 0,
                "defesas": 0, "clean_sheets": 0
            }
        t = torneio["estatisticas_globais"][nome]
        t["gols"] += stats.get("gols", 0)
        t["assistencias"] += stats.get("assistencias", 0)
        t["notas_soma"] += stats.get("nota", 0)
        t["jogos"] += 1
        t["defesas"] += stats.get("defesas", 0)
        t["clean_sheets"] += stats.get("clean_sheet", 0)

@app.route('/')
def menu_principal():
    return render_template('index.html')

@app.route('/hall_da_fama')
def ver_hall_da_fama():
    return render_template('hall.html', historico=hall_da_fama)

@app.route('/excluir_edicao/<nome_edicao>')
def excluir_edicao(nome_edicao):
    from historico_copa import hall_da_fama
    import pprint
    
    if nome_edicao in hall_da_fama:
        campeao = hall_da_fama[nome_edicao].get("Campeao")
        if campeao and campeao in hall_da_fama.get("Titulos_Totais", {}):
            hall_da_fama["Titulos_Totais"][campeao] -= 1
            if hall_da_fama["Titulos_Totais"][campeao] <= 0:
                del hall_da_fama["Titulos_Totais"][campeao]
                
        del hall_da_fama[nome_edicao]
        
        with open("historico_copa.py", "w", encoding="utf-8") as f:
            f.write("# ==========================================\n")
            f.write("# BANCO DE DADOS - HISTÓRICO DA COPA\n")
            f.write("# ==========================================\n\n")
            f.write("hall_da_fama = " + pprint.pformat(hall_da_fama) + "\n")
            
    return redirect(url_for('ver_hall_da_fama'))

@app.route('/jogo_rapido')
def jogo_rapido():
    times_copa = carregar_times_atuais()
    lista_times = sorted(list(times_copa.keys()))
    return render_template('jogo_rapido.html', times=lista_times)

@app.route('/simular', methods=['POST'])
def simular():
    times_copa = carregar_times_atuais()
    time_casa_nome = request.form['time_casa']
    time_fora_nome = request.form['time_fora']

    if time_casa_nome == time_fora_nome:
        return "<h1>Erro: Você escolheu o mesmo time duas vezes! Volte e arrume.</h1>"

    t_casa = times_copa[time_casa_nome]
    t_fora = times_copa[time_fora_nome]
    
    dados_jogo = simular_partida(t_casa, t_fora)
    
    # 🌟 Melhores e Piores!
    top_3 = sorted(dados_jogo['notas_jogadores'].items(), key=lambda x: x[1], reverse=True)[:3]
    piores_3 = sorted(dados_jogo['notas_jogadores'].items(), key=lambda x: x[1])[:3]

    return render_template('resultado.html', dados=dados_jogo, top_3=top_3, piores_3=piores_3, is_torneio=False)

@app.route('/universos')
def gerenciar_universos():
    if not os.path.exists(PASTA_SAVES):
        os.makedirs(PASTA_SAVES)
        from banco_de_dados import times_copa
        with open(os.path.join(PASTA_SAVES, "universo_base.json"), 'w', encoding='utf-8') as f:
            json.dump(times_copa, f, ensure_ascii=False, indent=4)
    
    arquivos = [f for f in os.listdir(PASTA_SAVES) if f.endswith('.json')]
    lista_universos = []
    
    for arq in arquivos:
        with open(os.path.join(PASTA_SAVES, arq), 'r', encoding='utf-8') as f:
            try:
                dados = json.load(f)
                qtd_times = len(dados)
            except:
                qtd_times = 0
        
        lista_universos.append({
            "nome_arquivo": arq,
            "nome_exibicao": arq.replace('.json', '').replace('_', ' ').upper(),
            "qtd_times": qtd_times,
            "ativo": arq == universo_atual_nome
        })
        
    return render_template('universos.html', universos=lista_universos)

@app.route('/set_universo/<nome_arquivo>')
def set_universo(nome_arquivo):
    global universo_atual_nome
    universo_atual_nome = nome_arquivo
    return redirect(url_for('gerenciar_universos'))

@app.route('/criar_universo', methods=['POST'])
def criar_universo():
    nome_novo = request.form.get('nome_universo').strip().replace(" ", "_")
    if nome_novo:
        caminho = os.path.join(PASTA_SAVES, f"{nome_novo}.json")
        if not os.path.exists(caminho):
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    return redirect(url_for('gerenciar_universos'))

@app.route('/excluir_universo/<nome_arquivo>')
def excluir_universo(nome_arquivo):
    if nome_arquivo != "universo_base.json":
        caminho = os.path.join(PASTA_SAVES, nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
        global universo_atual_nome
        if universo_atual_nome == nome_arquivo:
            universo_atual_nome = "universo_base.json"
    return redirect(url_for('gerenciar_universos'))

@app.route('/editar_universo/<nome_arquivo>')
def editar_universo(nome_arquivo):
    caminho = os.path.join(PASTA_SAVES, nome_arquivo)
    with open(caminho, 'r', encoding='utf-8') as f:
        times = json.load(f)
        
    caminho_base = os.path.join(PASTA_SAVES, "universo_base.json")
    with open(caminho_base, 'r', encoding='utf-8') as f:
        base_times = json.load(f)
        
    times_disponiveis = [t for t in base_times.keys() if t not in times]
    return render_template('editar_universo.html', nome_arquivo=nome_arquivo, times=times, times_disponiveis=times_disponiveis)

@app.route('/importar_time/<nome_arquivo>', methods=['POST'])
def importar_time(nome_arquivo):
    time_importar = request.form.get('time_importar')
    caminho = os.path.join(PASTA_SAVES, nome_arquivo)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        times = json.load(f)
        
    caminho_base = os.path.join(PASTA_SAVES, "universo_base.json")
    with open(caminho_base, 'r', encoding='utf-8') as f:
        base_times = json.load(f)
        
    if time_importar in base_times:
        times[time_importar] = base_times[time_importar]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(times, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('editar_universo', nome_arquivo=nome_arquivo))

@app.route('/remover_time/<nome_arquivo>/<nome_time>')
def remover_time(nome_arquivo, nome_time):
    caminho = os.path.join(PASTA_SAVES, nome_arquivo)
    with open(caminho, 'r', encoding='utf-8') as f:
        times = json.load(f)
        
    if nome_time in times:
        del times[nome_time]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(times, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('editar_universo', nome_arquivo=nome_arquivo))

@app.route('/criar_time/<nome_arquivo>', methods=['GET', 'POST'])
def criar_time(nome_arquivo):
    if request.method == 'POST':
        caminho = os.path.join(PASTA_SAVES, nome_arquivo)
        
        nome_time = request.form['nome_time'].strip()
        tecnico = request.form.get('tecnico', 'Técnico Genérico').strip()
        auxiliar = request.form.get('auxiliar', 'Auxiliar Genérico').strip()
        escudo = request.form.get('escudo', 'https://cdn-icons-png.flaticon.com/512/1041/1041258.png').strip()
        
        ataque = int(request.form['ataque'])
        meio = int(request.form['meio'])
        defesa = int(request.form['defesa'])
        goleiro = int(request.form['goleiro'])

        jogadores = []
        # Agora o loop vai até 16 (11 titulares + 5 reservas)
        for i in range(1, 17):
            nome_j = request.form.get(f'nome_j{i}').strip()
            pos_j = request.form.get(f'pos_j{i}').strip().upper()
            ovr_j = int(request.form.get(f'ovr_j{i}'))
            
            # Define se o cara vai jogar ou vai esquentar o banco
            status_jogador = "Titular" if i <= 11 else "Reserva"
            
            jogadores.append({
                "nome": nome_j, "posicao": pos_j, "ovr": ovr_j, 
                "capitao": (i == 11), "status": status_jogador
            })

        novo_time = {
            "nome": nome_time, "tecnico": tecnico, "auxiliar": auxiliar, "escudo": escudo,
            "ataque": ataque, "meio": meio, "defesa": defesa, "goleiro": goleiro, "jogadores": jogadores
        }

        with open(caminho, 'r', encoding='utf-8') as f:
            times = json.load(f)

        times[nome_time] = novo_time

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(times, f, indent=4, ensure_ascii=False)

        return redirect(url_for('editar_universo', nome_arquivo=nome_arquivo))

    return render_template('criar_time.html', nome_arquivo=nome_arquivo)

@app.route('/editar_time_clube/<nome_arquivo>/<nome_time>', methods=['GET', 'POST'])
def editar_time_clube(nome_arquivo, nome_time):
    caminho = os.path.join(PASTA_SAVES, nome_arquivo)
    with open(caminho, 'r', encoding='utf-8') as f:
        times = json.load(f)
        
    if request.method == 'POST':
        novo_nome = request.form['nome_time'].strip()
        tecnico = request.form.get('tecnico', 'Técnico Genérico').strip()
        escudo = request.form.get('escudo', '').strip()
        
        ataque = int(request.form['ataque'])
        meio = int(request.form['meio'])
        defesa = int(request.form['defesa'])
        goleiro = int(request.form['goleiro'])

        jogadores = []
        for i in range(1, 17):
            nome_j = request.form.get(f'nome_j{i}').strip()
            pos_j = request.form.get(f'pos_j{i}').strip().upper()
            ovr_j = int(request.form.get(f'ovr_j{i}'))
            status_jogador = "Titular" if i <= 11 else "Reserva"
            jogadores.append({"nome": nome_j, "posicao": pos_j, "ovr": ovr_j, "capitao": (i == 11), "status": status_jogador})

        novo_time = {
            "nome": novo_nome, "tecnico": tecnico, "escudo": escudo,
            "ataque": ataque, "meio": meio, "defesa": defesa, "goleiro": goleiro, "jogadores": jogadores
        }

        # Se mudou o nome do time, apaga a chave antiga
        if novo_nome != nome_time:
            del times[nome_time]
            
        times[novo_nome] = novo_time

        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(times, f, indent=4, ensure_ascii=False)

        return redirect(url_for('editar_universo', nome_arquivo=nome_arquivo))

    time_dados = times.get(nome_time)
    return render_template('criar_time.html', nome_arquivo=nome_arquivo, time_edit=time_dados)


@app.route('/iniciar_torneio')
def iniciar_torneio():
    import random
    times_copa = carregar_times_atuais()
    lista_times = list(times_copa.keys())
    
    if len(lista_times) < 8:
        return "<h1 style='color: white; font-family: sans-serif; text-align: center; margin-top: 50px;'>Erro: Precisa de pelo menos 8 equipas.</h1>"
        
    random.shuffle(lista_times)
    num_grupos = max(2, len(lista_times) // 4)
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    grupos = {}
    for i in range(num_grupos):
        grupos[f"Grupo {letras[i]}"] = []
        
    for i, time_nome in enumerate(lista_times):
        nome_grupo = f"Grupo {letras[i % num_grupos]}"
        grupos[nome_grupo].append(time_nome)
        
    tabelas = {}
    for nome_g, times_g in grupos.items():
        tabelas[nome_g] = []
        for t in times_g:
            tabelas[nome_g].append({"Nome": t, "Pts": 0, "J": 0, "V": 0, "E": 0, "D": 0, "GP": 0, "GC": 0, "SG": 0})
            
    def gerar_rodadas(times_do_grupo):
        times = list(times_do_grupo)
        if len(times) % 2 != 0: times.append(None)
        rodadas = []
        n = len(times)
        for i in range(n - 1):
            rodada = []
            for j in range(n // 2):
                casa = times[j]
                fora = times[n - 1 - j]
                if casa is not None and fora is not None:
                    rodada.append((casa, fora))
            times.insert(1, times.pop())
            rodadas.append(rodada)
        return rodadas

    rodadas_por_grupo = {}
    max_rodadas = 0
    for nome_g, times_g in grupos.items():
        rds = gerar_rodadas(times_g)
        rodadas_por_grupo[nome_g] = rds
        max_rodadas = max(max_rodadas, len(rds))

    calendario = []
    for r in range(max_rodadas):
        for nome_g in grupos.keys():
            if r < len(rodadas_por_grupo[nome_g]):
                for casa, fora in rodadas_por_grupo[nome_g][r]:
                    calendario.append({"grupo": nome_g, "casa": casa, "fora": fora})
            
    estado_torneio = {
        "fase_atual": "grupos", "grupos": grupos, "tabelas": tabelas,
        "calendario": calendario, "confrontos_atuais": [],
        "estatisticas_globais": {}
    }
    
    caminho_torneio = os.path.join(PASTA_SAVES, "torneio_atual.json")
    with open(caminho_torneio, 'w', encoding='utf-8') as f:
        json.dump(estado_torneio, f, indent=4, ensure_ascii=False)
        
    return render_template('sorteio_animado.html', grupos=grupos)

@app.route('/central_torneio')
def central_torneio():
    caminho_torneio = os.path.join(PASTA_SAVES, "torneio_atual.json")
    with open(caminho_torneio, 'r', encoding='utf-8') as f:
        torneio = json.load(f)
        
    if torneio["fase_atual"] == "grupos" and len(torneio["calendario"]) == 0:
        torneio["fase_atual"] = "fim_grupos"
        with open(caminho_torneio, 'w', encoding='utf-8') as f:
            json.dump(torneio, f, indent=4, ensure_ascii=False)
            
    proximo_jogo = None
    if torneio["fase_atual"] == "grupos" and len(torneio["calendario"]) > 0:
        proximo_jogo = torneio["calendario"][0]
        proximo_jogo["fase"] = "Fase de Grupos"
        
    elif torneio["fase_atual"] == "mata_mata" and len(torneio["confrontos_atuais"]) > 0:
        jogo = torneio["confrontos_atuais"][0]
        qtd_jogos = len(torneio["confrontos_atuais"])
        if "vencedores_fase" in torneio:
            qtd_jogos += len(torneio["vencedores_fase"])
            
        if qtd_jogos >= 8: nome_fase = "Oitavas de Final"
        elif qtd_jogos == 4: nome_fase = "Quartos de Final"
        elif qtd_jogos == 2 and not torneio.get("is_final_round", False): nome_fase = "Meia-Final"
        elif qtd_jogos == 2 and torneio.get("is_final_round", False):
            nome_fase = "Disputa do 3º Lugar" if "vencedores_fase" not in torneio else "GRANDE FINAL"
        elif qtd_jogos == 1: nome_fase = "GRANDE FINAL"
        else: nome_fase = "Mata-Mata"
        
        proximo_jogo = {"grupo": nome_fase, "casa": jogo[0], "fora": jogo[1], "fase": "Mata-Mata"}
        
    return render_template('central_torneio.html', torneio=torneio, proximo_jogo=proximo_jogo)

@app.route('/simular_jogo_torneio')
def simular_jogo_torneio():
    caminho_torneio = os.path.join(PASTA_SAVES, "torneio_atual.json")
    with open(caminho_torneio, 'r', encoding='utf-8') as f:
        torneio = json.load(f)
        
    times_copa = carregar_times_atuais()
    
    if torneio["fase_atual"] == "grupos" and len(torneio["calendario"]) > 0:
        jogo = torneio["calendario"].pop(0) 
        nome_g = jogo["grupo"]
        t_casa = times_copa[jogo["casa"]]
        t_fora = times_copa[jogo["fora"]]
        
        dados_jogo = simular_partida(t_casa, t_fora)
        gols_c, gols_f = dados_jogo['gols_casa'], dados_jogo['gols_fora']
        
        atualizar_estatisticas_globais(torneio, dados_jogo.get("stats_jogadores", {}))
        
        idx_c = next(i for i, d in enumerate(torneio["tabelas"][nome_g]) if d["Nome"] == jogo["casa"])
        idx_f = next(i for i, d in enumerate(torneio["tabelas"][nome_g]) if d["Nome"] == jogo["fora"])
        
        torneio["tabelas"][nome_g][idx_c]["J"] += 1; torneio["tabelas"][nome_g][idx_c]["GP"] += gols_c; torneio["tabelas"][nome_g][idx_c]["GC"] += gols_f; torneio["tabelas"][nome_g][idx_c]["SG"] += (gols_c - gols_f)
        torneio["tabelas"][nome_g][idx_f]["J"] += 1; torneio["tabelas"][nome_g][idx_f]["GP"] += gols_f; torneio["tabelas"][nome_g][idx_f]["GC"] += gols_c; torneio["tabelas"][nome_g][idx_f]["SG"] += (gols_f - gols_c)
        
        if gols_c > gols_f:
            torneio["tabelas"][nome_g][idx_c]["V"] += 1; torneio["tabelas"][nome_g][idx_c]["Pts"] += 3; torneio["tabelas"][nome_g][idx_f]["D"] += 1
        elif gols_f > gols_c:
            torneio["tabelas"][nome_g][idx_f]["V"] += 1; torneio["tabelas"][nome_g][idx_f]["Pts"] += 3; torneio["tabelas"][nome_g][idx_c]["D"] += 1
        else:
            torneio["tabelas"][nome_g][idx_c]["E"] += 1; torneio["tabelas"][nome_g][idx_c]["Pts"] += 1; torneio["tabelas"][nome_g][idx_f]["E"] += 1; torneio["tabelas"][nome_g][idx_f]["Pts"] += 1
            
        torneio["tabelas"][nome_g] = sorted(torneio["tabelas"][nome_g], key=lambda x: (x['Pts'], x['SG'], x['GP']), reverse=True)
        
        with open(caminho_torneio, 'w', encoding='utf-8') as f:
            json.dump(torneio, f, indent=4, ensure_ascii=False)
            
        top_3 = sorted(dados_jogo['notas_jogadores'].items(), key=lambda x: x[1], reverse=True)[:3]
        piores_3 = sorted(dados_jogo['notas_jogadores'].items(), key=lambda x: x[1])[:3]
        
        return render_template('resultado.html', dados=dados_jogo, top_3=top_3, piores_3=piores_3, is_torneio=True, tem_penaltis=False)
        
    elif torneio["fase_atual"] == "mata_mata" and len(torneio["confrontos_atuais"]) > 0:
        import random
        jogo = torneio["confrontos_atuais"].pop(0)
        t_casa_nome = jogo[0]
        t_fora_nome = jogo[1]
        
        t_casa = times_copa[t_casa_nome]
        t_fora = times_copa[t_fora_nome]
        
        dados_jogo = simular_partida(t_casa, t_fora)
        gols_c = dados_jogo['gols_casa']
        gols_f = dados_jogo['gols_fora']
        
        atualizar_estatisticas_globais(torneio, dados_jogo.get("stats_jogadores", {}))
        
        tem_penaltis = False
        pen_c = 0
        pen_f = 0
        if gols_c == gols_f:
            tem_penaltis = True
            pen_c = random.randint(3, 5)
            pen_f = random.randint(3, 5)
            while pen_c == pen_f:
                pen_c += random.randint(0, 1)
                pen_f += random.randint(0, 1)
                
        vencedor = t_casa_nome if (gols_c > gols_f or (tem_penaltis and pen_c > pen_f)) else t_fora_nome
        perdedor = t_fora_nome if vencedor == t_casa_nome else t_casa_nome
        
        if "vencedores_fase" not in torneio:
            torneio["vencedores_fase"] = []
            torneio["perdedores_fase"] = []
            
        torneio["vencedores_fase"].append(vencedor)
        torneio["perdedores_fase"].append(perdedor)
        
        if len(torneio["confrontos_atuais"]) == 0:
            vencedores = torneio["vencedores_fase"]
            perdedores = torneio["perdedores_fase"]
            proximos_confrontos = []
            
            if len(vencedores) == 2 and not torneio.get("is_final_round", False):
                proximos_confrontos = [[perdedores[0], perdedores[1]], [vencedores[0], vencedores[1]]]
                torneio["is_final_round"] = True
            elif len(vencedores) == 2 and torneio.get("is_final_round", False):
                campeao = vencedores[1]
                vice_campeao = perdedores[1]
                terceiro_lugar = vencedores[0]
                quarto_lugar = perdedores[0]
                
                artilheiro = "Ninguém"
                assistente = "Ninguém"
                melhor_goleiro = "Ninguém"
                melhor_jogador = "Ninguém"
                
                stats_g = torneio.get("estatisticas_globais", {})
                if stats_g:
                    jog_artilheiro = max(stats_g.keys(), key=lambda k: stats_g[k]["gols"])
                    if stats_g[jog_artilheiro]["gols"] > 0:
                        artilheiro = f"{jog_artilheiro} ({stats_g[jog_artilheiro]['gols']} Gols)"
                        
                    jog_assistente = max(stats_g.keys(), key=lambda k: stats_g[k]["assistencias"])
                    if stats_g[jog_assistente]["assistencias"] > 0:
                        assistente = f"{jog_assistente} ({stats_g[jog_assistente]['assistencias']} Assist.)"
                        
                    goleiros = {k: v for k, v in stats_g.items() if v["posicao"] == "GOL"}
                    if goleiros:
                        jog_goleiro = max(goleiros.keys(), key=lambda k: (goleiros[k]["clean_sheets"], goleiros[k]["defesas"]))
                        melhor_goleiro = f"{jog_goleiro} ({goleiros[jog_goleiro]['clean_sheets']} CS)"
                        
                    candidatos_mott = {k: v for k, v in stats_g.items() if v["jogos"] >= 3}
                    if not candidatos_mott: candidatos_mott = stats_g 
                    jog_mott = max(candidatos_mott.keys(), key=lambda k: candidatos_mott[k]["notas_soma"] / candidatos_mott[k]["jogos"])
                    media_mott = round(candidatos_mott[jog_mott]["notas_soma"] / candidatos_mott[jog_mott]["jogos"], 2)
                    melhor_jogador = f"{jog_mott} (Média {media_mott})"
                
                from historico_copa import hall_da_fama
                num_edicao = len([k for k in hall_da_fama.keys() if "Edicao" in k]) + 1
                nome_edicao = f"Edicao_{num_edicao}"
                
                hall_da_fama[nome_edicao] = {
                    "Campeao": campeao, "Vice": vice_campeao,
                    "Terceiro": terceiro_lugar, "Quarto": quarto_lugar,
                    "Melhor_Jogador": melhor_jogador, 
                    "Artilheiro": artilheiro,
                    "Assistente": assistente, 
                    "Melhor_Goleiro": melhor_goleiro
                }
                
                if campeao in hall_da_fama["Titulos_Totais"]: hall_da_fama["Titulos_Totais"][campeao] += 1
                else: hall_da_fama["Titulos_Totais"][campeao] = 1
                    
                import pprint
                with open("historico_copa.py", "w", encoding="utf-8") as f:
                    f.write("# ==========================================\n# BANCO DE DADOS - HISTÓRICO DA COPA\n# ==========================================\n\n")
                    f.write("hall_da_fama = " + pprint.pformat(hall_da_fama) + "\n")
                    
                torneio["campeao"] = campeao
                torneio["fase_atual"] = "encerrado"
            else:
                for i in range(0, len(vencedores), 2):
                    if i + 1 < len(vencedores): proximos_confrontos.append([vencedores[i], vencedores[i+1]])
                        
            torneio["confrontos_atuais"] = proximos_confrontos
            if "vencedores_fase" in torneio: del torneio["vencedores_fase"]
            if "perdedores_fase" in torneio: del torneio["perdedores_fase"]

        with open(caminho_torneio, 'w', encoding='utf-8') as f:
            json.dump(torneio, f, indent=4, ensure_ascii=False)
            
        top_3 = sorted(dados_jogo['notas_jogadores'].items(), key=lambda x: x[1], reverse=True)[:3]
        piores_3 = sorted(dados_jogo['notas_jogadores'].items(), key=lambda x: x[1])[:3]
        
        return render_template('resultado.html', dados=dados_jogo, top_3=top_3, piores_3=piores_3, is_torneio=True, 
                               tem_penaltis=tem_penaltis, pen_c=pen_c, pen_f=pen_f, vencedor_penaltis=vencedor)

    return redirect(url_for('central_torneio'))

@app.route('/simular_grupos_completo')
def simular_grupos_completo():
    caminho_torneio = os.path.join(PASTA_SAVES, "torneio_atual.json")
    with open(caminho_torneio, 'r', encoding='utf-8') as f:
        torneio = json.load(f)
        
    if torneio["fase_atual"] == "grupos" and len(torneio["calendario"]) > 0:
        times_copa = carregar_times_atuais()
        
        for jogo in torneio["calendario"]:
            nome_g = jogo["grupo"]
            t_casa = times_copa[jogo["casa"]]
            t_fora = times_copa[jogo["fora"]]
            
            dados_jogo = simular_partida(t_casa, t_fora)
            gols_c, gols_f = dados_jogo['gols_casa'], dados_jogo['gols_fora']
            
            atualizar_estatisticas_globais(torneio, dados_jogo.get("stats_jogadores", {}))
            
            idx_c = next(i for i, d in enumerate(torneio["tabelas"][nome_g]) if d["Nome"] == jogo["casa"])
            idx_f = next(i for i, d in enumerate(torneio["tabelas"][nome_g]) if d["Nome"] == jogo["fora"])
            
            torneio["tabelas"][nome_g][idx_c]["J"] += 1; torneio["tabelas"][nome_g][idx_c]["GP"] += gols_c; torneio["tabelas"][nome_g][idx_c]["GC"] += gols_f; torneio["tabelas"][nome_g][idx_c]["SG"] += (gols_c - gols_f)
            torneio["tabelas"][nome_g][idx_f]["J"] += 1; torneio["tabelas"][nome_g][idx_f]["GP"] += gols_f; torneio["tabelas"][nome_g][idx_f]["GC"] += gols_c; torneio["tabelas"][nome_g][idx_f]["SG"] += (gols_f - gols_c)
            
            if gols_c > gols_f:
                torneio["tabelas"][nome_g][idx_c]["V"] += 1; torneio["tabelas"][nome_g][idx_c]["Pts"] += 3; torneio["tabelas"][nome_g][idx_f]["D"] += 1
            elif gols_f > gols_c:
                torneio["tabelas"][nome_g][idx_f]["V"] += 1; torneio["tabelas"][nome_g][idx_f]["Pts"] += 3; torneio["tabelas"][nome_g][idx_c]["D"] += 1
            else:
                torneio["tabelas"][nome_g][idx_c]["E"] += 1; torneio["tabelas"][nome_g][idx_c]["Pts"] += 1; torneio["tabelas"][nome_g][idx_f]["E"] += 1; torneio["tabelas"][nome_g][idx_f]["Pts"] += 1
                
        for nome_g in torneio["tabelas"]:
            torneio["tabelas"][nome_g] = sorted(torneio["tabelas"][nome_g], key=lambda x: (x['Pts'], x['SG'], x['GP']), reverse=True)
            
        torneio["calendario"] = []
        torneio["fase_atual"] = "fim_grupos"
        
        with open(caminho_torneio, 'w', encoding='utf-8') as f:
            json.dump(torneio, f, indent=4, ensure_ascii=False)
            
    return redirect(url_for('central_torneio'))

@app.route('/sortear_mata_mata')
def sortear_mata_mata():
    import random
    caminho_torneio = os.path.join(PASTA_SAVES, "torneio_atual.json")
    with open(caminho_torneio, 'r', encoding='utf-8') as f:
        torneio = json.load(f)
        
    if torneio["fase_atual"] == "fim_grupos":
        pote_1 = []; pote_2 = []
        for nome_g, tabela in torneio["tabelas"].items():
            pote_1.append(tabela[0]["Nome"]); pote_2.append(tabela[1]["Nome"])
            
        random.shuffle(pote_1); random.shuffle(pote_2)
        confrontos = []
        for i in range(len(pote_1)): confrontos.append([pote_1[i], pote_2[i]])
            
        torneio["fase_atual"] = "mata_mata"
        torneio["confrontos_atuais"] = confrontos
        torneio["is_final_round"] = False
        
        with open(caminho_torneio, 'w', encoding='utf-8') as f:
            json.dump(torneio, f, indent=4, ensure_ascii=False)
            
    return render_template('sorteio_mata_mata.html', confrontos=confrontos)

if __name__ == '__main__':
    print("🚀 A INICIAR O NOVO SERVIDOR ATUALIZADO...")
    app.run(debug=True, host='127.0.0.1', port=8081)
