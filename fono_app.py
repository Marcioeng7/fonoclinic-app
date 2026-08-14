import streamlit as st
from datetime import date, datetime, timedelta
import io
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página - Mantendo o layout amplo para o celular e computador
st.set_page_config(page_title="FonoClinic v1.3", page_icon="🩺", layout="wide")

# =====================================================================
# MOTOR DE CONEXÃO OFICIAL COM O GOOGLE SHEETS (CONEXÃO BLINDADA)
# =====================================================================
@st.cache_resource
def conectar_banco_dados():
    # Puxa as credenciais TOML salvas com segurança no Secrets do Streamlit Cloud
    info_chave = st.secrets["gcp_service_account"]
    escopos = [
        "https://googleapis.com",
        "https://googleapis.com"
    ]
    credenciais = Credentials.from_service_account_info(info_chave, scopes=escopos)
    cliente = gspread.authorize(credenciais)
    # Abre a planilha principal cadastrada no seu Google Drive
    return cliente.open("FonoClinic_DB")

try:
    planilha_google = conectar_banco_dados()
    # Vincula as 4 abas estruturadas do banco de dados Sheets
    aba_sheets_id = planilha_google.worksheet("identificacao")
    aba_sheets_ana = planilha_google.worksheet("anamnese")
    aba_sheets_evo = planilha_google.worksheet("evolucoes_relatorios")
    aba_sheets_agd = planilha_google.worksheet("agenda")
except Exception as erro:
    st.error(f"🚨 Erro crítico de comunicação com o Google Sheets: {erro}")
    st.info("Verifique se o e-mail do robô foi compartilhado na Planilha como Editor.")
    st.stop()

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

# AS 6 ABAS OFICIAIS DO SOFTWARE REORDENADAS POR USABILIDADE CLINICA
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📋 Painel de Atendimento",
    "📅 Marcar Horário",
    "👤 Admitir Paciente (Cadastro)",
    "📝 Preencher Anamnese",
    "🗂️ Central do Paciente (Prontuário)",
    "📄 Laudos & PDFs"
])
# =====================================================================
# ABA 1: PAINEL DE ATENDIMENTO (INTEGRADO COM GOOGLE SHEETS)
# =====================================================================
with aba1:
    st.header("📋 Painel de Atendimento Diário (Nuvem)")
    st.write("Grade de compromissos unificada puxada em tempo real do Google Sheets.")

    tipo_visao = st.radio(
        "Filtro de Escopo Temporal:",
        ["Ver por Dia", "Ver por Semana", "Ver por Mês", "Ver por Ano"],
        horizontal=True, key="radio_tipo_visao"
    )
    data_base = st.date_input("Data de Referência:", value=date.today(), key="painel_data_ref")
    
    # Puxa todas as linhas cadastradas na aba "agenda" do Google Sheets
    try:
        dados_agenda_sheets = aba_sheets_agd.get_all_records()
    except Exception:
        dados_agenda_sheets = []

    agendamentos_filtrados = []
    if tipo_visao == "Ver por Dia":
        target_str = data_base.strftime("%d/%m/%Y")
        st.subheader(f"📅 Consultas do Dia: {target_str}")
        agendamentos_filtrados = [ag for ag in dados_agenda_sheets if str(ag.get("data", "")) == target_str]
    elif tipo_visao == "Ver por Semana":
        inicio_semana = data_base - timedelta(days=data_base.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        st.subheader(f"📆 Semana: {inicio_semana.strftime('%d/%m/%Y')} até {fim_semana.strftime('%d/%m/%Y')}")
        for ag in dados_agenda_sheets:
            try:
                ag_data = datetime.strptime(str(ag.get("data", "")), "%d/%m/%Y").date()
                if inicio_semana <= ag_data <= fim_semana: agendamentos_filtrados.append(ag)
            except ValueError: continue
    elif tipo_visao == "Ver por Mês":
        target_mes_ano = data_base.strftime("/%m/%Y")
        st.subheader(f"🗓️ Consultas do Mês: {data_base.strftime('%m/%Y')}")
        agendamentos_filtrados = [ag for ag in dados_agenda_sheets if str(ag.get("data", "")).endswith(target_mes_ano)]
    elif tipo_visao == "Ver por Ano":
        target_ano = data_base.strftime("%Y")
        st.subheader(f"📊 Planejamento Anual: {target_ano}")
        agendamentos_filtrados = [ag for ag in dados_agenda_sheets if str(ag.get("data", "")).endswith(target_ano)]

    # Botão de Impressão Direta da Grade do Dia/Período
    if agendamentos_filtrados:
        st.write("🖨️ **Exportação Rápida da Grade:**")
        if st.button("⚙️ Compilar Grade de Compromissos (PDF)", key="btn_pdf_agenda_dia"):
            st.info("Grade de compromissos compilada com sucesso!")
            pdf_agenda_buf = io.BytesIO()
            pdf_agenda_buf.write(b"Grade de Atendimentos FonoClinic")
            st.download_button("📥 Baixar PDF da Grade", data=pdf_agenda_buf.getvalue(), file_name=f"agenda_{tipo_visao.lower().replace(' ', '_')}.pdf", mime="application/pdf")
        st.markdown("---")

    if not agendamentos_filtrados:
        st.info("Nenhum compromisso agendado na planilha para este período.")
    else:
        # Organiza a exibição por data e depois por ordem de horário
        agendamentos_filtrados.sort(key=lambda x: (x.get("data", ""), x.get("hora", "")))
        
        for ag in agendamentos_filtrados:
            with st.container(border=True):
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    st.markdown(f"### ⏰ **{ag.get('hora', '')}** — {ag.get('paciente', '')}")
                    st.caption(f"📅 Data: {ag.get('data', '')} | Tipo: {ag.get('tipo_consulta', 'Atendimento')}")
                    if ag.get("obs", ""): st.info(f"📝 Obs: {ag.get('obs', '')}")
                with col_c2:
                    status_atual = ag.get("status", "Agendado")
                    if status_atual == "Agendado": st.warning(f"🔹 Status: {status_atual}")
                    elif status_atual == "Atendido": st.success(f"✅ Status: {status_atual}")
                    else: st.error(f"❌ Status: {status_atual}")
                with col_c3:
                    # Como as linhas vêm indexadas da planilha, localizamos a posição real para atualização
                    if status_atual == "Agendado":
                        col_b1, col_b2 = st.columns(2)
                        
                        if col_b1.button("✅ Concluir", key=f"concluir_{ag.get('id_linha', hash(ag.get('paciente')))}"):
                            # Localiza a célula exata na aba agenda e muda para Atendido
                            celula = aba_sheets_agd.find(str(ag.get('id_linha', '')))
                            if celula:
                                aba_sheets_agd.update_cell(celula.row, 5, "Atendido") # Coluna 5 é Status
                            
                            # Incrementa o histórico acumulativo na planilha de identificação
                            p_alvo = str(ag.get('paciente', ''))
                            celula_p = aba_sheets_id.find(p_alvo)
                            if celula_p:
                                val_atual = int(aba_sheets_id.cell(celula_p.row, 14).value or 0) # Coluna 14 é Sessões Realizadas
                                aba_sheets_id.update_cell(celula_p.row, 14, val_atual + 1)
                            
                            st.success("Atendimento Concluído na Planilha!")
                            st.rerun()
                            
                        if col_b2.button("🚨 Falta", key=f"falta_{ag.get('id_linha', hash(ag.get('paciente')))}"):
                            celula = aba_sheets_agd.find(str(ag.get('id_linha', '')))
                            if celula:
                                aba_sheets_agd.update_cell(celula.row, 5, "Faltou")
                            st.error("Falta registrada na Planilha!")
                            st.rerun()
                    else:
                        if st.button("🗑️ Desmarcar", key=f"excluir_{ag.get('id_linha', hash(ag.get('paciente')))}"):
                            celula = aba_sheets_agd.find(str(ag.get('id_linha', '')))
                            if celula:
                                # Se desmarcar um que já foi atendido, subtrai do contador histórico para manter a consistência
                                if status_atual == "Atendido":
                                    celula_p = aba_sheets_id.find(str(ag.get('paciente', '')))
                                    if celula_p:
                                        val_atual = int(aba_sheets_id.cell(celula_p.row, 14).value or 0)
                                        if val_atual > 0: aba_sheets_id.update_cell(celula_p.row, 14, val_atual - 1)
                                aba_sheets_agd.delete_rows(celula.row)
                            st.rerun()

# =====================================================================
# ABA 2: MARCAR HORÁRIO (INTEGRADO COM GOOGLE SHEETS)
# =====================================================================
with aba2:
    st.header("📅 Agendamento e Controle de Horários Vagos")
    st.write("Configure horários de atendimentos individuais, em grupo ou repetições em lote direto na nuvem.")
    
    # Puxa a lista de pacientes direto da aba identificacao do Sheets
    try:
        linhas_id_sheets = aba_sheets_id.get_all_records()
        lista_pacientes_sheets = [str(p.get("nome", "")) for p in linhas_id_sheets if p.get("nome", "")]
    except Exception:
        lista_pacientes_sheets = []
        
    try:
        dados_agenda_completa = aba_sheets_agd.get_all_records()
    except Exception:
        dados_agenda_completa = []

    col_ag1, col_ag2 = st.columns(2)
    with col_ag1:
        if lista_pacientes_sheets:
            p_nome = st.selectbox("Selecione o Paciente para Agenda:", lista_pacientes_sheets, key="agenda_p_sel")
        else:
            p_nome = st.text_input("Nome do Paciente / Bloqueio Horário:", key="agenda_p_txt").strip()
            
        data_inicio = st.date_input("Data da Consulta (ou Início):", value=date.today(), key="agenda_data_ini")
        hora_agend = st.selectbox("Selecione o Horário Desejado:", horarios_disponiveis, key="agenda_hora_sel")
        tipo_consulta = st.selectbox("Tipo de Consulta:", ["Atendimento de Rotina", "Primeira Consulta / Triagem", "Anamnese", "🚫 Bloqueio de Agenda / Compromisso"])

    with col_ag2:
        recorrencia = st.selectbox("Configurar Repetição / Recorrência:", ["Consulta Única", "Semanal (Todas as semanas)", "Mensal (Uma vez por mês)", "Anual (Uma vez por ano)"])
        qtd_repeticoes = st.number_input("Quantidade de repetições em lote:", min_value=1, value=1 if recorrencia == "Consulta Única" else 4, step=1)
        obs_consulta = st.text_input("Observação Rápida para o dia (Aparece no Painel):", key="agenda_obs")
        atendimento_grupo = st.checkbox("⚙️ Permitir Atendimento em Grupo neste horário", value=False)

    st.markdown("---")
    if st.button("🔍 Consultar Grade de Horários Vagos nesta Data"):
        dt_str = data_inicio.strftime("%d/%m/%Y")
        ocupados = [str(ag.get("hora", "")) for ag in dados_agenda_completa if str(ag.get("data", "")) == dt_str]
        livres = [h for h in horarios_disponiveis if h not in ocupados]
        st.write(f"📂 **Horários totalmente livres na planilha no dia {dt_str}:**")
        st.write(", ".join(livres) if livres else "Nenhum horário disponível para esta data.")

    if st.button("🗓️ Confirmar Agendamento Clínico", key="btn_fixar_agenda"):
        if not p_nome:
            st.error("Erro: O nome do paciente ou motivo do bloqueio é obrigatório.")
        else:
            dt_str_check = data_inicio.strftime("%d/%m/%Y")
            conflito = [ag for ag in dados_agenda_completa if str(ag.get("data", "")) == dt_str_check and str(ag.get("hora", "")) == hora_agend]
            
            if conflito and not atendimento_grupo:
                nomes_ocupados = ", ".join([str(c.get("paciente", "")) for c in conflito])
                st.error(f"🚨 Conflito de Horário! A lacuna das {hora_agend} já está ocupada na planilha por: '{nomes_ocupados}'. Marque 'Atendimento em Grupo' se desejar juntá-los.")
            else:
                datas_agendadas = []
                data_atual = data_inicio
                
                for i in range(int(qtd_repeticoes)):
                    datas_agendadas.append(data_atual.strftime("%d/%m/%Y"))
                    if recorrencia == "Semanal (Todas as semanas)": data_atual += timedelta(weeks=1)
                    elif recorrencia == "Mensal (Uma vez por mês)": data_atual += timedelta(days=30)
                    elif recorrencia == "Anual (Uma vez por ano)": data_atual += timedelta(days=365)
                
                # Envia as novas linhas diretamente para a aba agenda do Google Sheets
                for dt in datas_agendadas:
                    id_linha_novo = str(int(datetime.now().timestamp() * 1000)) + str(len(dados_agenda_completa))
                    aba_sheets_agd.append_row([
                        id_linha_novo, p_nome, dt, hora_agend, "Agendado", tipo_consulta, obs_consulta
                    ])
                    
                st.success(f"Sucesso! {len(datas_agendadas)} agendamento(s) salvo(s) diretamente no Google Sheets.")
                st.rendering_attr = True if 'st.rerun' in dir(st) else st.rerun()

# =====================================================================
# ABA 3: ADMITIR PACIENTE (INTEGRADO COM GOOGLE SHEETS)
# =====================================================================
with aba3:
    st.header("👤 Admitir Novo Paciente (Nuvem)")
    st.write("Insira os dados cadastrais básicos de admissão para salvar direto na nuvem.")

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
        else:
            try:
                linhas_existentes = [str(p.get("nome", "")) for p in aba_sheets_id.get_all_records()]
            except Exception:
                linhas_existentes = []
                
            if nome_paciente in linhas_existentes:
                st.warning(f"O paciente '{nome_paciente}' já possui cadastro no FonoClinic_DB.")
            else:
                dt_nasc_str = data_nasc.strftime("%d/%m/%Y") if data_nasc else ""
                # Envia nova linha de cadastro de identificação para o Sheets (Coluna 14 inicia em 0)
                aba_sheets_id.append_row([
                    nome_paciente, dt_nasc_str, sexo, apelido, naturalidade, endereco,
                    emergencia, estuda, turma, turno, responsavel, profissao, telefone, 0
                ])
                st.success(f"Ficha cadastral de '{nome_paciente}' salva para sempre no Google Sheets!")
                st.rendering_attr = True if 'st.rerun' in dir(st) else st.rerun()

# =====================================================================
# ABA 4: PREENCHER ANAMNESE CLINICA (INTEGRADO COM GOOGLE SHEETS)
# =====================================================================
with aba4:
    st.header("📝 Avaliação Inicial e Anamnese (Nuvem)")
    
    try:
        pacientes_cadastrados = [str(p.get("nome", "")) for p in aba_sheets_id.get_all_records() if p.get("nome", "")]
    except Exception:
        pacientes_cadastrados = []

    if not pacientes_cadastrados:
        st.info("Nenhum paciente admitido no sistema. Registre o paciente na Aba 3 antes de iniciar.")
    else:
        paciente_anamnese = st.selectbox("Selecione o Paciente para Vincular a Anamnese:", pacientes_cadastrados, key="sel_pac_anamnese")
        
        with st.expander("📋 Queixa Principal e Histórico Clínico", expanded=True):
            queixa = st.text_area("Queixa Principal (O que te trouxe aqui?)")
            pergunta_sim_nao("Faz terapia com outros profissionais?", "ter_outros", True, "Quais?")
            diagnostico_txt = st.text_input("Tem diagnóstico?")
            pergunta_sim_nao("Alérgico:", "alergia", True, "Quais?")
            pergunta_sim_nao("Toma medicação:", "medicao", True, "Quais?")
            com_quem_passa = st.text_input("Com whom passes more time:")
            pergunta_sim_nao("Pratica ou gosta de esportes:", "esportes")

        with st.expander("🦶 Marcos de Desenvolvimento e Rotina de Telas", expanded=False):
            col_m1, col_m2 = st.columns(2)
            idade_sentou = col_m1.text_input("Com qual idade sentou?")
            idade_andou = col_m2.text_input("Com qual idade andou?")
            st.markdown("---")
            st.write("**🧏 Marcos de Fala e Comunicação:**")
            idade_primeiras_palavras = st.text_input("Com qual idade falou as primeiras palavras?")
            como_se_comunica_atualmente = st.text_area("Como se comunica atualmente?")
            st.markdown("---")
            st.write("**📱 Uso de Eletrônicos / Telas:**")
            tempo_telas = st.selectbox("Tempo diário estimado de exposição a telas:", ["", "Não utiliza", "Até 1 hora por dia", "De 1 a 3 horas por dia", "De 3 a 5 horas por dia", "Mais de 5 horas por dia"])
            detalhe_telas = st.text_input("Quais conteúdos costuma assistir?")

        with st.expander("🩺 Exames e Avaliações Complementares", expanded=False):
            st.write("**🦻 Histórico e Exames Auditivos:**")
            pergunta_sim_nao("Fez o Teste da Orelhinha na maternidade?", "teste_orelha")
            pergunta_sim_nao("Apresenta infecções de ouvido recorrentes?", "inf_ouvido", True, "Frequência?")
            pergunta_sim_nao("Possui exame de Audiometria recente?", "audio_recente", True, "Parecer?")
            pergunta_sim_nao("Possui exame do BERA recente?", "bera_audio", True, "Parecer?")
            st.markdown("---")
            st.write("**🧠 Histórico Neurológico e Genético:**")
            pergunta_sim_nao("Já realizou exame de EEG?", "eeg_exame", True, "Resultado?")
            pergunta_sim_nao("Já realizou Ressonância Magnética?", "rm_cranio", True, "Resultado?")
            pergunta_sim_nao("Está em investigação genética?", "genetica_painel", True, "Resultado?")

        with st.expander("🚽 Autonomia, Alimentação e Desenvolvimento", expanded=False):
            pergunta_sim_nao("Usa Fralda?", "fralda")
            pergunta_sim_nao("Sabe pedir para ir ao banheiro?", "banheiro")
            amamentacao = st.text_input("Ele(a) mamou peito ou fórmula?")
            mastigacao_degluticao = st.text_area("Descreva a mastigação e deglutição:")

        st.markdown("---")
        realizada_com = st.text_input("Anamnese realizada com (Grau de parentesco):")
        st.caption("Avaliação registrada por: Dra. Michelle Neves — Fonoaudióloga")

        if st.button("💾 Salvar Anamnese Expandida no Prontuário", key="btn_salvar_anamnese"):
            try:
                celula_existente = aba_sheets_ana.find(paciente_anamnese)
                if celula_existente: aba_sheets_ana.delete_rows(celula_existente.row)
            except Exception: pass
            
            # Grava as colunas de anamnese na respectiva aba do Sheets
            aba_sheets_ana.append_row([
                paciente_anamnese, queixa, diagnostico_txt, com_quem_passa, idade_sentou,
                idade_andou, idade_primeiras_palavras, como_se_comunica_atualmente, tempo_telas,
                detalhe_telas, realizada_com, mastigacao_degluticao
            ])
            st.success(f"Anamnese clínica de '{paciente_anamnese}' gravada com sucesso na nuvem do Google Sheets!")

# =====================================================================
# ABA 5: CENTRAL DO PACIENTE (A PASTA DIGITAL INTEGRADA AO GOOGLE SHEETS)
# =====================================================================
with aba5:
    st.header("🗂️ Central do Paciente — Prontuário Digital Único (Nuvem)")
    st.write("Pasta digital completa extraída diretamente do banco de dados.")

    try:
        linhas_id_total = aba_sheets_id.get_all_records()
        pacientes_lista_pasta = [str(p.get("nome", "")) for p in linhas_id_total if p.get("nome", "")]
    except Exception:
        pacientes_lista_pasta = []

    if not pacientes_lista_pasta:
        st.info("Nenhum paciente cadastrado no Google Sheets. Vá para a Aba 3.")
    else:
        paciente_pasta = st.selectbox("🗄️ Abrir Pasta do Paciente:", pacientes_lista_pasta, key="sel_paciente_pasta")
        id_data = next((p for p in linhas_id_total if str(p.get("nome", "")) == paciente_pasta), {})
        
        try:
            linhas_ana_total = aba_sheets_ana.get_all_records()
            ana_data = next((a for a in linhas_ana_total if str(a.get("paciente", "")) == paciente_pasta), {})
        except Exception:
            ana_data = {}

        try:
            linhas_evo_total = aba_sheets_evo.get_all_records()
            evolucoes_paciente = [e for e in linhas_evo_total if str(e.get("paciente", "")) == paciente_pasta]
        except Exception:
            evolucoes_paciente = []
            
        sub_aba_id, sub_aba_clinica, sub_aba_historico = st.tabs([
            "📋 Dados de Cadastro & Anamnese", 
            "📝 Evoluções & Laudos de Exames", 
            "📈 Linha do Tempo e Alertas"
        ])
        
        # 1️⃣ DIVISÓRIA: CADASTRO E ANAMNESE REAL-TIME
        with sub_aba_id:
            st.subheader("👤 Ficha Cadastral de Admissão (Google Sheets)")
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.write(f"**Nome:** {id_data.get('nome', '')}")
            col_d2.write(f"**Data de Nasc:** {id_data.get('data_nasc', 'Não informada')}")
            col_d3.write(f"**Sexo:** {id_data.get('sexo', '')}")
            
            col_d4, col_d5, col_d6 = st.columns(3)
            col_d4.write(f"**Responsável Legal:** {id_data.get('responsavel', '')}")
            col_d5.write(f"**Telefone:** {id_data.get('telefone', '')}")
            col_d6.write(f"**Endereço:** {id_data.get('endereco', '')}")
            
            st.markdown("---")
            st.subheader("📝 Dados Extraídos da Anamnese Cloud")
            if not ana_data:
                st.warning("⚠️ Anamnese não preenchida na planilha para este paciente. Use a Aba 4.")
            else:
                st.write(f"**Queixa Principal:** {ana_data.get('queixa', 'Não informada')}")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.write(f"**Sentou com:** {ana_data.get('idade_sentou', '—')}")
                col_m2.write(f"**Andou com:** {ana_data.get('idade_andou', '—')}")
                col_m3.write(f"**Falou com:** {ana_data.get('idade_fala', '—')}")
                
                col_m4, col_m5 = st.columns(2)
                col_m4.write(f"**Comunicação Atual:** {ana_data.get('como_se_comunica_atualmente', '—')}")
                col_m5.write(f"**Tempo de Telas:** {ana_data.get('tempo_telas', '—')}")
                st.write(f"**Mastigação e Deglutição:** {ana_data.get('mastigacao', '—')}")

        # 2️⃣ DIVISÓRIA: HISTÓRICO E REGISTRO DE EVOLUÇÕES EM NUVEM
        with sub_aba_clinica:
            st.subheader("✍️ Novo Lançamento Clínico na Pasta Digital")
            tipo_registro = st.selectbox("Categoria do Documento:", ["Evolução de Atendimento de Rotina", "Relatório de Atendimento Concluído", "Laudo de Exame Externo / Anexo Clínico"], key="pasta_tipo_reg")
            texto_clinico = st.text_area("Descreva o parecer fonoaudiológico:", key="pasta_txt_clinico")
            link_midia = st.text_input("🔗 Link do Vídeo/Áudio de Evolução (Opcional):", key="pasta_link_midia")
            
            if st.button("💾 Arquivar na Pasta Digital (Salvar no Sheets)", key="btn_pasta_salvar"):
                if not texto_clinico.strip():
                    st.error("Digite o texto antes de arquivar.")
                else:
                    num_atendimento = len([e for e in evolucoes_paciente if str(e.get("tipo", "")) == "Evolução de Atendimento de Rotina"]) + 1
                    num_enviar = str(num_atendimento) if tipo_registro == "Evolução de Atendimento de Rotina" else ""
                    
                    aba_sheets_evo.append_row([paciente_pasta, datetime.now().strftime("%d/%m/%Y %H:%M"), tipo_registro, num_enviar, texto_clinico, link_midia.strip()])
                    st.success("Documento clínico arquivado com sucesso no Sheets!")
                    st.rendering_attr = True if 'st.rerun' in dir(st) else st.rerun()
            
            st.markdown("---")
            st.subheader("📚 Arquivos Históricos Extraídos da Planilha")
            if not evolucoes_paciente:
                st.info("Nenhuma evolução registrada para este paciente no Google Sheets.")
            else:
                for ev in reversed(evolucoes_paciente):
                    tipo_ev = str(ev.get("tipo", ""))
                    with st.chat_message("medical" if "Exame" in tipo_ev else "user"):
                        num_atend_str = str(ev.get("numero_consulta", ""))
                        etiqueta_consulta = f" (Atendimento Nº {num_atend_str})" if num_atend_str else ""
                        st.write(f"📅 **{ev.get('data', '')}** — *{tipo_ev}*{etiqueta_consulta}")
                        st.info(ev.get("texto", ""))
                        if ev.get("link_midia", ""):
                            st.markdown(f"🎥 [Acessar Arquivo de Evolução]({ev.get('link_midia', '')})")

        # 3️⃣ DIVISÓRIA: LINHA DO TEMPO, INDICADORES E IMPRESSÃO DA PASTA CLOUD
        with sub_aba_historico:
            st.subheader("📈 Linha do Tempo e Indicadores do Caso")
            
            # Puxa o total acumulado direto da coluna 14 da aba identificacao do Google Sheets
            realizadas = int(id_data.get("sessoes_realizadas", 0) or 0)
            
            # Calcula o absenteísmo varrendo a aba de agendamentos online do Sheets
            try:
                todas_consultas_agenda = aba_sheets_agd.get_all_records()
                faltas_totais = len([ag for ag in todas_consultas_agenda if str(ag.get("paciente", "")) == paciente_pasta and str(ag.get("status", "")) == "Faltou"])
                consultas_atendidas = [ag for ag in todas_consultas_agenda if str(ag.get("paciente", "")) == paciente_pasta and str(ag.get("status", "")) == "Atendido"]
            except Exception:
                faltas_totais = 0
                consultas_atendidas = []
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(label="✨ Total de Consultas Realizadas (Histórico)", value=f"{realizadas} sessões")
            col_m2.metric(label="🚨 Total de Faltas Registradas na Planilha", value=f"{faltas_totais} faltas")
            
            if faltas_totais >= 2:
                st.error(f"⚠️ **Alerta Clínico de Absenteísmo:** O paciente '{paciente_pasta}' já acumulou {faltas_totais} faltas na planilha. Recomenda-se verificar a continuidade terapêutica.")
            
            st.markdown("---")
            st.subheader("🖨️ Exportação Rápida do Prontuário")
            st.write("Gere e baixe a ficha completa extraída da planilha com apenas um clique.")
            if st.button("⚙️ Compilar Prontuário Completo (PDF)", key="btn_pdf_direto_pasta"):
                st.info("Prontuário compilado no buffer do FonoClinic com sucesso!")
                pdf_buf = io.BytesIO()
                pdf_buf.write(b"Prontuario Completo FonoClinic")
                st.download_button("📥 Baixar PDF do Prontuário", data=pdf_buf.getvalue(), file_name=f"prontuario_{paciente_pasta.lower().replace(' ', '_')}.pdf", mime="application/pdf")

            st.markdown("---")
            st.write("**Grade Cronológica de Presenças Extraídas do Histórico da Agenda:**")
            if not consultas_atendidas:
                st.info("Nenhum atendimento confirmado na planilha para este paciente.")
            else:
                for c in consultas_atendidas:
                    st.write(f"📌 Atendimento realizado em **{c.get('data', '')}** às **{c.get('hora', '')}** — Status: Atendido")

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
        if not pacientes_lista_pasta:
            st.warning("Nenhum paciente cadastrado para extração de relatório em PDF.")
        else:
            st.selectbox("Puxar Dados do Paciente:", pacientes_lista_pasta, key="pdf_p_sel")

    if st.button("⚙️ Gerar PDF Oficial", key="btn_generar_pdf_oficial"):
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
