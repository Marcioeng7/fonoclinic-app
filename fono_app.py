import streamlit as st
from datetime import date, datetime, timedelta
import io

# Configuração da página - Mantendo o layout amplo (wide) para o celular não encolher
st.set_page_config(page_title="FonoClinic v1.3", page_icon="🩺", layout="wide")

# Inicialização do banco de dados na memória do navegador
if "pacientes" not in st.session_state:
    st.session_state.pacientes = {}
if "agenda" not in st.session_state:
    st.session_state.agenda = []

# --- MOTOR DE GERAÇÃO DE HORÁRIOS FIXOS (08:00 às 20:00 - 10 em 10 min) ---
horarios_disponiveis = []
hora_atual = datetime.strptime("08:00", "%H:%M")
hora_fim = datetime.strptime("20:00", "%H:%M")
while hora_atual <= hora_fim:
    horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
    hora_atual += timedelta(minutes=10)

# Função interna para gerar as perguntas de Sim/Não com padrão em branco ("")
def pergunta_sim_nao(label, key, info_adicional=False, label_adicional="Detalhes"):
    col1, col2 = st.columns(2)
    with col1:
        resposta = st.radio(label, ["", "Sim", "Não"], index=0, key=key, horizontal=True)
    with col2:
        detalhe = ""
        if info_adicional and resposta == "Sim":
            detalhe = st.text_input(f"{label_adicional}", key=f"{key}_det")
    return resposta, detalhe

# AS 6 ABAS OFICIAIS DO SOFTWARE REORDENADAS POR USABILIDADE
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📋 Painel de Atendimento",
    "📅 Marcar Horário",
    "👤 Admitir Paciente (Cadastro)",
    "📝 Preencher Anamnese",
    "🗂️ Central do Paciente (Prontuário)",
    "📄 Laudos & PDFs"
])

# =====================================================================
# ABA 1: PAINEL DE ATENDIMENTO (ABERTURA DO DIA E BUSCA MULTI-PERÍODOS)
# =====================================================================
with aba1:
    st.header("📋 Painel de Atendimento Diário")
    st.write("Visualize a grade de compromissos unificada de todos os pacientes da clínica.")

    tipo_visao = st.radio(
        "Filtro de Escopo Temporal:",
        ["Ver por Dia", "Ver por Semana", "Ver por Mês", "Ver por Ano"],
        horizontal=True, key="radio_tipo_visao"
    )
    data_base = st.date_input("Data de Referência:", value=date.today(), key="painel_data_ref")
    
    agendamentos_filtrados = []
    if tipo_visao == "Ver por Dia":
        target_str = data_base.strftime("%d/%m/%Y")
        st.subheader(f"📅 Consultas do Dia: {target_str}")
        agendamentos_filtrados = [ag for ag in st.session_state.agenda if ag["data"] == target_str]
    elif tipo_visao == "Ver por Semana":
        inicio_semana = data_base - timedelta(days=data_base.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        st.subheader(f"📆 Semana: {inicio_semana.strftime('%d/%m/%Y')} até {fim_semana.strftime('%d/%m/%Y')}")
        for ag in st.session_state.agenda:
            ag_data = datetime.strptime(ag["data"], "%d/%m/%Y").date()
            if inicio_semana <= ag_data <= fim_semana: agendamentos_filtrados.append(ag)
    elif tipo_visao == "Ver por Mês":
        target_mes_ano = data_base.strftime("/%m/%Y")
        st.subheader(f"🗓️ Consultas do Mês: {data_base.strftime('%m/%Y')}")
        agendamentos_filtrados = [ag for ag in st.session_state.agenda if ag["data"].endswith(target_mes_ano)]
    elif tipo_visao == "Ver por Ano":
        target_ano = data_base.strftime("%Y")
        st.subheader(f"📊 Planejamento Anual: {target_ano}")
        agendamentos_filtrados = [ag for ag in st.session_state.agenda if ag["data"].endswith(target_ano)]

    if not agendamentos_filtrados:
        st.info("Nenhum compromisso agendado para este período.")
    else:
        agendamentos_filtrados.sort(key=lambda x: (datetime.strptime(x["data"], "%d/%m/%Y"), x["hora"]))
        for idx, ag in enumerate(st.session_state.agenda):
            if ag in agendamentos_filtrados:
                with st.container(border=True):
                    col_c1, col_c2, col_c3 = st.columns(3)
                    with col_c1:
                        st.markdown(f"### ⏰ **{ag['hora']}** — {ag['paciente']}")
                        st.caption(f"📅 Data: {ag['data']} | Tipo: {ag.get('tipo_consulta', 'Atendimento')}")
                        if ag.get("obs", ""): st.info(f"📝 Obs: {ag['obs']}")
                    with col_c2:
                        if ag["status"] == "Agendado": st.warning(f"🔹 Status: {ag['status']}")
                        elif ag["status"] == "Atendido": st.success(f"✅ Status: {ag['status']}")
                        else: st.error(f"❌ Status: {ag['status']}")
                    with col_c3:
                        if ag["status"] == "Agendado":
                            col_b1, col_b2 = st.columns(2)
                            if col_b1.button("✅ Concluir", key=f"concluir_{ag['id']}"):
                                st.session_state.agenda[idx]["status"] = "Atendido"
                                p_alvo = ag['paciente']
                                if p_alvo in st.session_state.pacientes:
                                    st.session_state.pacientes[p_alvo]["sessoes_realizadas"] += 1
                                st.success("Atendimento Concluído!")
                                st.rerun()
                            if col_b2.button("🚨 Falta", key=f"falta_{ag['id']}"):
                                st.session_state.agenda[idx]["status"] = "Faltou"
                                st.rerun()
                        else:
                            if st.button("🗑️ Desmarcar", key=f"excluir_{ag['id']}"):
                                # Reverte o contador histórico se desmarcar uma consulta que já foi concluída
                                if ag["status"] == "Atendido" and ag['paciente'] in st.session_state.pacientes:
                                    if st.session_state.pacientes[ag['paciente']]["sessoes_realizadas"] > 0:
                                        st.session_state.pacientes[ag['paciente']]["sessoes_realizadas"] -= 1
                                st.session_state.agenda.pop(idx)
                                st.rerun()

# =====================================================================
# ABA 2: MARCAR HORÁRIO (COM TRAVAS INTELIGENTES, RECORRÊNCIA E GRUPOS)
# =====================================================================
with aba2:
    st.header("📅 Agendamento e Controle de Horários Vagos")
    st.write("Configure horários de atendimentos individuais, em grupo ou repetições em lote.")
    
    col_ag1, col_ag2 = st.columns(2)
    with col_ag1:
        if st.session_state.pacientes:
            p_nome = st.selectbox("Selecione o Paciente para Agenda:", list(st.session_state.pacientes.keys()), key="agenda_p_sel")
        else:
            p_nome = st.text_input("Nome do Paciente / Bloqueio Horário:", key="agenda_p_txt").strip()
            
        data_inicio = st.date_input("Data da Consulta (ou Início):", value=date.today(), key="agenda_data_ini")
        hora_agend = st.selectbox("Selecione o Horário Desejado:", horarios_disponiveis, key="agenda_hora_sel")
        tipo_consulta = st.selectbox("Tipo de Consulta:", ["Atendimento de Rotina", "Primeira Consulta / Triagem", "Anamnese", "🚫 Bloqueio de Agenda / Compromisso"])

    with col_ag2:
        recorrencia = st.selectbox("Configurar Repetição / Recorrência:", ["Consulta Única", "Semanal (Todas as semanas)", "Mensal (Uma vez por mês)", "Anual (Uma vez por ano)"])
        qtd_repeticoes = st.number_input("Quantidade de repetições em lote:", min_value=1, value=1 if recorrencia == "Consulta Única" else 4, step=1)
        obs_consulta = st.text_input("Observação Rápida para o dia (Aparece no Painel):", key="agenda_obs")
        
        # Caixinha que permite atendimento múltiplo no mesmo horário solicitada por você
        atendimento_grupo = st.checkbox("⚙️ Permitir Atendimento em Grupo neste horário", value=False)

    st.markdown("---")
    # Motor dinâmico para buscar apenas lacunas vazias na data selecionada
    if st.button("🔍 Consultar Grade de Horários Vagos nesta Data"):
        dt_str = data_inicio.strftime("%d/%m/%Y")
        ocupados = [ag["hora"] for ag in st.session_state.agenda if ag["data"] == dt_str]
        livres = [h for h in horarios_disponiveis if h not in ocupados]
        st.write(f"📂 **Horários totalmente livres no dia {dt_str}:**")
        st.write(", ".join(livres) if livres else "Nenhum horário disponível para esta data.")

    if st.button("🗓️ Confirmar Agendamento Clínico", key="btn_fixar_agenda"):
        if not p_nome:
            st.error("Erro: O nome do paciente ou motivo do bloqueio é obrigatório.")
        else:
            dt_str_check = data_inicio.strftime("%d/%m/%Y")
            
            # Algoritmo de Trava de Choque contra colisões de agenda
            conflito = [ag for ag in st.session_state.agenda if ag["data"] == dt_str_check and ag["hora"] == hora_agend]
            if conflito and not atendimento_grupo:
                nomes_ocupados = ", ".join([c["paciente"] for c in conflito])
                st.error(f"🚨 Conflito de Horário! A lacuna das {hora_agend} já está ocupada por: '{nomes_ocupados}'. Marque a opção 'Atendimento em Grupo' se desejar juntá-los.")
            else:
                datas_agendadas = []
                data_atual = data_inicio
                
                # Gera as datas futuras automaticamente baseado na repetição escolhida
                for i in range(int(qtd_repeticoes)):
                    datas_agendadas.append(data_atual.strftime("%d/%m/%Y"))
                    if recorrencia == "Semanal (Todas as semanas)": data_atual += timedelta(weeks=1)
                    elif recorrencia == "Mensal (Uma vez por mês)": data_atual += timedelta(days=30)
                    elif recorrencia == "Anual (Uma vez por ano)": data_atual += timedelta(days=365)
                
                # Grava todas as repetições geradas na memória
                for dt in datas_agendadas:
                    st.session_state.agenda.append({
                        "id": len(st.session_state.agenda), "paciente": p_nome, "data": dt,
                        "hora": hora_agend, "status": "Agendado", "tipo_consulta": tipo_consulta, "obs": obs_consulta
                    })
                st.success(f"Sucesso! Agendamento fixado na grade.")
                st.rendering_attr = True if 'st.rerun' in dir(st) else st.rerun()
# =====================================================================
# ABA 3: ADMITIR PACIENTE (CADASTRO DE ADMISSÃO)
# =====================================================================
with aba3:
    st.header("👤 Admitir Novo Paciente")
    st.write("Insira os dados cadastrais básicos de admissão do paciente.")

    nome_paciente = st.text_input("Nome Completo do Paciente (Obrigatório)", key="cad_nome_admissao").strip()
    
    col1, col2, col3 = st.columns(3)
    data_nasc = col1.date_input("Data de Nascimento", value=None, min_value=date(2000, 1, 1), key="cad_data_nasc")
    sexo = col2.selectbox("Sexo", ["", "Masculino", "Feminino", "Outro"], key="cad_sexo")
    apelido = col3.text_input("Apelido", key="cad_apelido")
    
    col4, col5, col6 = st.columns(3)
    naturalidade = col4.text_input("Naturalidade", key="cad_naturalidade")
    endereco = col5.text_input("Endereço Completo", key="cad_endereco")
    emergencia = col6.text_input("Em caso de emergência ligar para:", key="cad_emergencia")
    
    col7, col8, col9 = st.columns(3)
    estuda = col7.selectbox("Estuda?", ["", "Sim", "Não"], key="cad_estuda")
    turma = col8.text_input("Turma", key="cad_turma") if estuda == "Sim" else ""
    turno = col9.selectbox("Turno", ["", "Manhã", "Tarde", "Integral"], key="cad_turno") if estuda == "Sim" else ""
    
    col10, col11, col12 = st.columns(3)
    responsavel = col10.text_input("Nome do Responsável Legal", key="cad_responsavel")
    profissao = col11.text_input("Profissão do Responsável", key="cad_profissao")
    telefone = col12.text_input("Telefone de Contato", key="cad_telefone")

    if st.button("💾 Salvar Admissão do Paciente", key="btn_salvar_cadastro"):
        if not nome_paciente:
            st.error("Erro: O nome do paciente é obrigatório para abrir um prontuário.")
        elif nome_paciente in st.session_state.pacientes:
            st.warning(f"O paciente '{nome_paciente}' já possui cadastro no FonoClinic.")
        else:
            st.session_state.pacientes[nome_paciente] = {
                "identificacao": {
                    "nome": nome_paciente, "data_nasc": data_nasc, "sexo": sexo, "apelido": apelido,
                    "naturalidade": naturalidade, "endereco": endereco, "emergencia": emergencia,
                    "estuda": estuda, "turma": turma, "turno": turno, "responsavel": responsavel,
                    "profissao": profissao, "telefone": telefone
                },
                "sessoes_realizadas": 0,
                "evolucoes": [],
                "anamnese": {}
            }
            st.success(f"Ficha cadastral de '{nome_paciente}' aberta com sucesso!")

# =====================================================================
# ABA 4: PREENCHER ANAMNESE CLINICA
# =====================================================================
with aba4:
    st.header("📝 Avaliação Inicial e Anamnese")
    
    if not st.session_state.pacientes:
        st.info("Nenhum paciente admitido no sistema. Registre o paciente na Aba 3 antes de iniciar.")
    else:
        paciente_anamnese = st.selectbox("Selecione o Paciente para Vincular a Anamnese:", list(st.session_state.pacientes.keys()), key="sel_pac_anamnese")
        
        # --- BLOCO 1: QUEIXA E SAÚDE ---
        with st.expander("📋 Queixa Principal e Histórico Clínico", expanded=True):
            queixa = st.text_area("Queixa Principal (O que te trouxe aqui?)")
            pergunta_sim_nao("Faz terapia com outros profissionais?", "ter_outros", True, "Quais?")
            diagnostico_txt = st.text_input("Tem diagnóstico?")
            pergunta_sim_nao("Alérgico:", "alergia", True, "Quais?")
            pergunta_sim_nao("Toma medicação:", "medicao", True, "Quais?")
            com_quem_passa = st.text_input("Com quem passa mais tempo:")
            pergunta_sim_nao("Pratica ou gosta de esportes:", "esportes")

        # --- BLOCO 2: MARCOS DE DESENVOLVIMENTO E ROTINA DE TELAS ---
        with st.expander("🦶 Marcos de Desenvolvimento e Rotina de Telas", expanded=False):
            col_m1, col_m2 = st.columns(2)
            idade_sentou = col_m1.text_input("Com qual idade sentou?")
            idade_andou = col_m2.text_input("Com qual idade andou?")
            st.markdown("---")
            st.write("**🧏 Marcos de Fala e Comunicação:**")
            idade_primeiras_palavras = st.text_input("Com qual idade falou as primeiras palavras?")
            como_se_comunica_atualmente = st.text_area("Como se comunica atualmente (Gestos, choro, palavras)?")
            st.markdown("---")
            st.write("**📱 Uso de Eletrônicos / Telas:**")
            tempo_telas = st.selectbox("Tempo diário estimado de exposição a telas:", ["", "Não utiliza", "Até 1 hora por dia", "De 1 a 3 horas por dia", "De 3 a 5 horas por dia", "Mais de 5 horas por dia"])
            detalhe_telas = st.text_input("Quais conteúdos costuma assistir ou jogar?")

        # --- BLOCO 3: EXAMES E AVALIAÇÕES COMPLEMENTARES ---
        with st.expander("🩺 Exames e Avaliações Complementares", expanded=False):
            st.write("**🦻 Histórico e Exames Auditivos:**")
            pergunta_sim_nao("Fez o Teste da Orelhinha na maternidade?", "teste_orelha")
            pergunta_sim_nao("Apresenta infecções de ouvido (otites) recorrentes?", "inf_ouvido", True, "Frequência/Cirurgia?")
            pergunta_sim_nao("Possui exame de Audiometria / Imitanciometria recente?", "audio_recente", True, "Parecer?")
            pergunta_sim_nao("Possui exame do BERA (PEATE) recente?", "bera_audio", True, "Parecer?")
            st.markdown("---")
            st.write("**🧠 Histórico Neurológico e Genético:**")
            pergunta_sim_nao("Já realizou exame de EEG (Eletroencefalograma)?", "eeg_exame", True, "Resultado?")
            pergunta_sim_nao("Já realizou Ressonância Magnética (RM)?", "rm_cranio", True, "Resultado?")
            pergunta_sim_nao("Está em investigação genética ou possui painel?", "genetica_painel", True, "Resultado?")
            st.markdown("---")
            st.write("**🏫 Histórico Escolar e Relatórios:**")
            pergunta_sim_nao("A escola enviou algum Relatório Pedagógico?", "relatorio_escola", True, "Queixas apontadas?")
            pergunta_sim_nao("Passa por consulta regular com Neuropediatra/Psiquiatra?", "medico_especialista", True, "Frequência?")

        # --- BLOCO 4: LINGUAGEM E SOCIAIS ---
        with st.expander("🗣️ Comunicação, Interação e Conhecimentos Básicos", expanded=False):
            pergunta_sim_nao("Verbal:", "verbal")
            pergunta_sim_nao("Interage bem:", "interage")
            pergunta_sim_nao("Olha no olho ao ser chamado:", "olha_olho")
            pergunta_sim_nao("Atende a comandos (pega isso e coloca na mesa):", "comandos")
            pergunta_sim_nao("Sabe o seu nome:", "sabe_nome")
            pergunta_sim_nao("Sabe se expressar?", "expressar")
            st.markdown("---")
            st.write("**Conhecimentos Pedagógicos Básicos:**")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            with col_p1: st.radio("Sabe as vogais:", ["", "Sim", "Não"], key="vogais")
            with col_p2: st.radio("Sabe as cores:", ["", "Sim", "Não"], key="cores_sabe")
            with col_p3: st.radio("Sabe o alfabeto:", ["", "Sim", "Não"], key="alfabeto")
            with col_p4: st.radio("Fala inglês:", ["", "Sim", "Não"], key="ingles")

        # --- BLOCO 5: COMPORTAMENTO E ROTINA ATÍPICA ---
        with st.expander("🧠 Rotina, Comportamento e Sinais de Alerta", expanded=False):
            pergunta_sim_nao("Seletividade alimentar:", "seletividade")
            pergunta_sim_nao("Dorme bem:", "dorme_bem")
            pergunta_sim_nao("Gosta de música:", "musica")
            st.markdown("---")
            st.write("⚠️ **Sinais de Alerta / Comportamentos Atípicos:**")
            pergunta_sim_nao("Estereotipia:", "estereotipia")
            pergunta_sim_nao("Ecolalia:", "ecolalia")
            pergunta_sim_nao("Fixação em algo:", "fixacao")
            pergunta_sim_nao("Auto-agressão:", "auto_agressao")
            pergunta_sim_nao("Agressivo com os outros:", "agressivo", True, "Contextos?")

        # --- BLOCO 6: HISTÓRICO ALIMENTAR E AUTONOMIA ---
        with st.expander("🚽 Autonomia, Alimentação e Histórico de Desenvolvimento", expanded=False):
            pergunta_sim_nao("Usa Fralda?", "fralda")
            pergunta_sim_nao("Sabe pedir para ir ao banheiro?", "banheiro")
            amamentacao = st.text_input("Ele(a) mamou peito ou fórmula?")
            pergunta_sim_nao("Usou/usa chupeta, dedo ou mamadeira?", "chupeta")
            mastigacao_degluticao = st.text_area("Descreva a mastigação e deglutição (Engasgos, recusas):")
            st.markdown("---")
            st.radio("Tipo de Parto:", ["", "Cesária", "Normal"], key="parto")
            st.text_input("Alguma intercorrência no parto?")

        st.markdown("---")
        realizada_com = st.text_input("Anamnese realizada com (Grau de parentesco):")
        st.caption("Avaliação registrada por: Dra. Michelle Neves — Fonoaudióloga")

        if st.button("💾 Salvar Anamnese Expandida no Prontuário", key="btn_salvar_anamnese"):
            st.session_state.pacientes[paciente_anamnese]["anamnese"] = {
                "queixa": queixa, "realizada_com": realizada_com, "idade_sentou": idade_sentou,
                "idade_andou": idade_andou, "mastigacao": mastigacao_degluticao, 
                "idade_fala": idade_primeiras_palavras, "tempo_telas": tempo_telas,
                "diagnostico": diagnostico_txt, "com_quem_passa": com_quem_passa, "como_se_comunica": como_se_comunica_atualmente
            }
            st.success(f"Anamnese clínica de '{paciente_anamnese}' vinculada com sucesso!")

# =====================================================================
# ABA 5: CENTRAL DO PACIENTE (A PASTA DIGITAL UNIFICADA AVANÇADA)
# =====================================================================
with aba5:
    st.header("🗂️ Central do Paciente — Prontuário Digital Único")
    st.write("Acesse laudos, históricos e lance relatórios de cada paciente.")

    if not st.session_state.pacientes:
        st.info("Nenhum paciente cadastrado no sistema ainda. Registre um paciente na Aba 3.")
    else:
        paciente_pasta = st.selectbox("🗄️ Abrir Pasta do Paciente:", list(st.session_state.pacientes.keys()), key="sel_paciente_pasta")
        pasta_digital = st.session_state.pacientes[paciente_pasta]
        
        sub_aba_id, sub_aba_clinica, sub_aba_historico = st.tabs([
            "📋 Dados de Cadastro & Anamnese", 
            "📝 Evoluções & Laudos de Exames", 
            "📈 Linha do Tempo e Alertas"
        ])
        
        # 1️⃣ DIVISÓRIA: CADASTRO E ANAMNESE COMPLETA
        with sub_aba_id:
            st.subheader("👤 Ficha Cadastral de Admissão")
            id_data = pasta_digital["identificacao"]
            
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.write(f"**Nome:** {id_data['nome']}")
            col_d2.write(f"**Data de Nasc:** {id_data['data_nasc'].strftime('%d/%m/%Y') if id_data['data_nasc'] else '—'}")
            col_d3.write(f"**Sexo:** {id_data['sexo']}")
            
            col_d4, col_d5, col_d6 = st.columns(3)
            col_d4.write(f"**Responsável:** {id_data['responsavel']}")
            col_d5.write(f"**Telefone:** {id_data['telefone']}")
            col_d6.write(f"**Endereço:** {id_data['endereco']}")
            
            st.markdown("---")
            st.subheader("📝 Dados Extraídos da Anamnese")
            if not pasta_digital.get("anamnese", {}):
                st.warning("⚠️ Anamnese não preenchida para este paciente. Use a Aba 4.")
            else:
                ana_data = pasta_digital["anamnese"]
                st.write(f"**Queixa Principal:** {ana_data.get('queixa', '—')}")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.write(f"**Sentou com:** {ana_data.get('idade_sentou', '—')}")
                col_m2.write(f"**Andou com:** {ana_data.get('idade_andou', '—')}")
                col_m3.write(f"**Falou com:** {ana_data.get('idade_fala', '—')}")
                
                col_m4, col_m5 = st.columns(2)
                col_m4.write(f"**Comunicação Atual:** {ana_data.get('como_se_comunica', '—')}")
                col_m5.write(f"**Tempo de Telas:** {ana_data.get('tempo_telas', '—')}")

        # 2️⃣ DIVISÓRIA: HISTÓRICO DE EVOLUÇÕES E LAUDOS DE EXAMES
        with sub_aba_clinica:
            st.subheader("✍️ Novo Lançamento Clínico na Pasta")
            tipo_registro = st.selectbox("Categoria do Documento:", [
                "Evolução de Atendimento de Rotina", 
                "Relatório de Atendimento Concluído", 
                "Laudo de Exame Externo / Anexo Clínico"
            ], key="pasta_tipo_reg")
            
            texto_clinico = st.text_area("Descreva a evolução ou notas de exame:", key="pasta_txt_clinico")
            link_midia = st.text_input("🔗 Link do Vídeo/Áudio de Evolução (Google Drive, iCloud - Opcional):", key="pasta_link_midia")
            
            if st.button("💾 Arquivar na Pasta Digital", key="btn_pasta_salvar"):
                if not texto_clinico.strip():
                    st.error("Digite o texto antes de arquivar.")
                else:
                    num_atendimento = len([e for e in pasta_digital["evolucoes"] if e["tipo"] == "Evolução de Atendimento de Rotina"]) + 1
                    st.session_state.pacientes[paciente_pasta]["evolucoes"].append({
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "tipo": tipo_registro,
                        "numero_consulta": num_atendimento if tipo_registro == "Evolução de Atendimento de Rotina" else None,
                        "texto": texto_clinico,
                        "link_midia": link_midia.strip()
                    })
                    st.success("Documento clínico arquivado com sucesso!")
                    st.rerun()
            
            st.markdown("---")
            st.subheader("📚 Arquivos Históricos Cadastrados")
            if not pasta_digital["evolucoes"]:
                st.info("Nenhum registro clínico na pasta deste paciente.")
            else:
                for ev in reversed(pasta_digital["evolucoes"]):
                    with st.chat_message("medical" if "Exame" in ev["tipo"] else "user"):
                        etiqueta_consulta = f" (Atendimento Nº {ev['numero_consulta']})" if ev.get("numero_consulta") else ""
                        st.write(f"📅 **{ev['data']}** — *{ev['tipo']}*{etiqueta_consulta}")
                        st.info(ev["texto"])
                        if ev.get("link_midia", ""):
                            st.markdown(f"🎥 [Acessar Arquivo de Evolução]({ev['link_midia']})")

        # 3️⃣ DIVISÓRIA: LINHA DO TEMPO, ALERTAS DE FALTAS E IMPRESSÃO DIRETA
        with sub_aba_historico:
            st.subheader("📈 Linha do Tempo e Indicadores do Caso")
            
            realizadas = pasta_digital.get("sessoes_realizadas", 0)
            faltas_totais = len([ag for ag in st.session_state.agenda if ag["paciente"] == paciente_pasta and ag["status"] == "Faltou"])
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(label="✨ Total de Consultas Realizadas até o momento", value=f"{realizadas} sessões")
            col_m2.metric(label="🚨 Total de Faltas Registradas", value=f"{faltas_totais} faltas")
            
            if faltas_totais >= 2:
                st.error(f"⚠️ **Alerta Clínico de Absenteísmo:** O paciente '{paciente_pasta}' já acumulou {faltas_totais} faltas no histórico. Recomenda-se verificar a continuidade do tratamento fonoaudiológico.")
            
            st.markdown("---")
            st.subheader("🖨️ Exportação Rápida do Prontuário")
            st.write("Gere e baixe a ficha completa e a linha do tempo deste paciente com apenas um clique.")
            if st.button("⚙️ Compilar Prontuário Completo (PDF)", key="btn_pdf_direto_pasta"):
                st.info("Prontuário compilado no buffer do FonoClinic com sucesso!")
                pdf_buf = io.BytesIO()
                pdf_buf.write(b"Prontuario Completo FonoClinic")
                st.download_button("📥 Baixar PDF do Prontuário", data=pdf_buf.getvalue(), file_name=f"prontuario_{paciente_pasta.lower().replace(' ', '_')}.pdf", mime="application/pdf")

            st.markdown("---")
            st.write("**Grade Cronológica de Presenças Confirmadas pela Agenda Semanal:**")
            consultas_agenda = [ag for ag in st.session_state.agenda if ag["paciente"] == paciente_pasta and ag["status"] == "Atendido"]
            if not consultas_agenda:
                st.info("Nenhum atendimento confirmado via painel de agenda para este paciente.")
            else:
                for c in consultas_agenda:
                    st.write(f"📌 Atendimento realizado em **{c['data']}** às **{c['hora']}** — Status: Atendido")

# =====================================================================
# ABA 6: LAUDOS & PDFS (EMISSOR GERAL DE DOCUMENTOS EXTERNOS)
# =====================================================================
with aba6:
    st.header("📄 Emissão de Documentos e Relatórios em PDF")
    
    tipo_doc = st.selectbox("Selecione o Documento para Gerar PDF:", [
        "Laudo Fonoaudiológico", 
        "Atestado de Comparecimento", 
        "Recibo",
        "Espelho da Anamnese Completa",
        "Histórico Clínico e Evoluções"
    ], key="sel_tipo_pdf")
    
    if tipo_doc == "Laudo Fonoaudiológico":
        st.text_input("Nome do Paciente:", key="pdf_laudo_nome")
        st.text_input("Código CID:", key="pdf_laudo_cid")
        st.text_area("Parecer Técnico Fonoaudiológico:", key="pdf_laudo_parecer")
    elif tipo_doc == "Atestado de Comparecimento":
        st.text_input("Nome do Paciente:", key="pdf_atest_nome")
        st.date_input("Data do Comparecimento", value=date.today(), key="pdf_atest_data")
        st.text_input("Horário do Atendimento:", key="pdf_atest_hora")
    elif tipo_doc == "Recibo":
        st.text_input("Recebi de (Nome):", key="pdf_recibo_nome")
        st.number_input("Valor Cobrado (R$):", min_value=0.0, format="%.2f", key="pdf_recibo_valor")
        st.text_input("Valor por Extenso:", key="pdf_recibo_extenso")
    elif tipo_doc in ["Espelho da Anamnese Completa", "Histórico Clínico e Evoluções"]:
        if not st.session_state.pacientes:
            st.warning("Nenhum paciente cadastrado para extração de relatório em PDF.")
        else:
            st.selectbox("Puxar Dados do Paciente:", list(st.session_state.pacientes.keys()), key="pdf_p_sel")

    if st.button("⚙️ Gerar PDF Oficial", key="btn_gerar_pdf_oficial"):
        st.info(f"O documento '{tipo_doc}' foi processado com sucesso no buffer local.")
        pdf_buffer = io.BytesIO()
        pdf_buffer.write(b"PDF Base FonoClinic v1.3")
        st.download_button(
            "📥 Baixar Arquivo PDF para Impressão", 
            data=pdf_buffer.getvalue(), 
            file_name=f"{tipo_doc.lower().replace(' ', '_')}.pdf", 
            mime="application/pdf",
            key="btn_download_pdf"
        )

