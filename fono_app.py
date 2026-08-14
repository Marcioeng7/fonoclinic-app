# ==============================================================================
# BLOCO 1 DE 5: IMPORTAÇÕES, CONFIGURAÇÃO E CONEXÃO SEGURA COM GOOGLE SHEETS
# ==============================================================================
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as SACredentials

# 1. CONFIGURAÇÃO DA PÁGINA (Sempre o primeiro comando do script)
st.set_page_config(
    page_title="FonoClinic v1.3",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CACHE DA CONEXÃO COM O BANCO DE DADOS EM NUVEM
@st.cache_resource
def conectar_google_sheets():
    try:
        escopos = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        # Puxa a chave secreta cadastrada na nuvem do Streamlit
        info_chaves = dict(st.secrets["gcp_service_account"])
        credenciais = SACredentials.from_service_account_info(info_chaves, scopes=escopos)
        
        # Conecta via gspread
        cliente = gspread.authorize(credenciais)
        
        # ID Oficial da Planilha extraído do seu link válido
        id_planilha = "1qLEa7_iEPSkENJSovjy6_3yzVVjtVAKnJDkteG6Skdw"
        return cliente.open_by_key(id_planilha)
    except Exception as e:
        st.error(f"Erro crítico de comunicação com o Google Sheets: {e}")
        st.info("Verifique se o e-mail do robô foi compartilhado na Planilha como Editor.")
        return None

# Inicializa o motor global
gspread_client = conectar_google_sheets()

if gspread_client:
    try:
        aba_identificacao = gspread_client.worksheet("identificacao")
        aba_anamnese = gspread_client.worksheet("anamnese")
        aba_evolucao = gspread_client.worksheet("evolucoes_relatorios")
        aba_agenda = gspread_client.worksheet("agenda")
    except Exception as e:
        st.error(f"Erro ao mapear abas da planilha: {e}")
        st.warning("Verifique se as abas no Sheets estão nomeadas exatamente como: identificacao, anamnese, evolucoes_relatorios e agenda")

# 3. INTERFACE E CRIAÇÃO DOS PAINÉIS EM ABAS
st.title("📝 FonoClinic v1.3 — Prontuário Digital Integrado")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 1. Identificação do Paciente", 
    "🩺 2. Anamnese Clínica", 
    "📈 3. Evoluções e Relatórios", 
    "📅 4. Agenda Integrada",
    "📂 5. Central do Paciente"
])

# ==============================================================================
# BLOCO 2 DE 5: ABA 1 — IDENTIFICAÇÃO E CADASTRO DO PACIENTE COMPLETO
# ==============================================================================
with tab1:
    st.header("👥 Cadastro e Identificação do Paciente")
    st.write("Insira os dados cadastrais do paciente para registrar ou atualizar na nuvem.")
    
    with st.form("form_identificacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            id_paciente = st.text_input("Código/ID do Paciente (Ex: PAC001):", placeholder="PAC001")
            nome_paciente = st.text_input("Nome Completo:", placeholder="Nome do paciente")
            data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA):", placeholder="14/08/2020")
            idade_paciente = st.text_input("Idade:", placeholder="Ex: 6 anos")
        
        with col2:
            nome_responsavel = st.text_input("Nome do Responsável (Se menor):", placeholder="Mãe ou Pai")
            telefone_contato = st.text_input("Telefone de Contato (Com DDD):", placeholder="(21) 99999-9999")
            queixa_principal = st.text_area("Queixa Principal (Breve resumo):", placeholder="Motivo da busca pelo atendimento")
            
        botao_salvar_id = st.form_submit_button("💾 Salvar Identificação na Nuvem")
        
    if botao_salvar_id:
        if not id_paciente or not nome_paciente:
            st.warning("⚠️ Os campos 'Código/ID' e 'Nome Completo' são obrigatórios!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets. Verifique a configuração inicial.")
        else:
            with st.spinner("Gravando dados no Google Sheets..."):
                try:
                    # Prepara os dados na ordem correta da tabela de identificação
                    nova_linha = [
                        id_paciente, 
                        nome_paciente, 
                        data_nascimento, 
                        idade_paciente, 
                        nome_responsavel, 
                        telefone_contato, 
                        queixa_principal
                    ]
                    aba_identificacao.append_row(nova_linha)
                    st.success(f"🎉 Paciente '{nome_paciente}' cadastrado com sucesso na nuvem!")
                except Exception as e:
                    st.error(f"Erro ao salvar dados na nuvem: {e}")

# ==============================================================================
# BLOCO 3 DE 5: ABA 2 — ANAMNESE CLÍNICA DETALHADA E COMPLETA
# ==============================================================================
with tab2:
    st.header("🩺 Anamnese Clínica")
    st.write("Preencha o histórico completo de desenvolvimento e saúde do paciente.")
    
    with st.form("form_anamnese", clear_on_submit=True):
        st.subheader("📍 Vinculação de Prontuário")
        id_paciente_anamnese = st.text_input("Código/ID do Paciente Cadastrado (Deve ser igual ao da Aba 1):", placeholder="PAC001")
        
        st.markdown("---")
        st.subheader("👶 Desenvolvimento Motor e Linguagem")
        col1, col2 = st.columns(2)
        with col1:
            desenv_motor = st.text_area("Marcos de Desenvolvimento Motor (Sentou, andou no tempo esperado?):", placeholder="Descreva os marcos motores...")
            desenv_linguagem = st.text_area("Desenvolvimento da Linguagem (Primeiras palavras, balbucios?):", placeholder="Descreva o início e evolução da fala...")
        with col2:
            compreensao = st.text_area("Compreensão (Atende a comandos, atende quando chamado?):", placeholder="Descreva a capacidade de compreensão...")
            comportamento = st.text_area("Comportamento e Interação Social:", placeholder="Interação com pares, comportamento em casa/escola...")
            
        st.markdown("---")
        st.subheader("🍽️ Funções Estomatognáticas (Alimentação e Respiração)")
        col3, col4 = st.columns(2)
        with col3:
            alimentacao = st.text_area("Histórico de Alimentação (Mastigação, seletividade alimentar, engasgos?):", placeholder="Padrões e dificuldades alimentares...")
        with col4:
            respiracao_sono = st.text_area("Respiração e Sono (Respira pela boca, ronca, sono agitado?):", placeholder="Qualidade do sono e padrão respiratório...")
            
        st.markdown("---")
        st.subheader("🏥 Histórico Médico e Familiar")
        historico_medico = st.text_area("Histórico Médico, Exames e Antecedentes Familiares relevantes:", placeholder="Intervenções, exames realizados, histórico de saúde da família...")
        
        botao_salvar_anamnese = st.form_submit_button("💾 Salvar Anamnese na Nuvem")
        
    if botao_salvar_anamnese:
        if not id_paciente_anamnese:
            st.warning("⚠️ Você precisa informar o 'Código/ID do Paciente' para vincular esta anamnese!")
        elif gspread_client is None:
            st.error("❌ Sem conexão ativa com o Google Sheets. Verifique o Bloco 1.")
        else:
            with st.spinner("Gravando anamnese no Google Sheets..."):
                try:
                    nova_anamnese = [
                        id_paciente_anamnese,
                        desenv_motor,
                        desenv_linguagem,
                        compreensao,
                        comportamento,
                        alimentacao,
                        respiracao_sono,
                        historico_medico
                    ]
                    aba_anamnese.append_row(nova_anamnese)
                    st.success(f"🎉 Anamnese do paciente '{id_paciente_anamnese}' salva com sucesso na nuvem!")
                except Exception as e:
                    st.error(f"Erro ao salvar anamnese na nuvem: {e}")

# ==============================================================================
# BLOCO 4 DE 5: ABA 3 — EVOLUÇÕES CLÍNICAS & ABA 4 — AGENDA AVANÇADA
# ==============================================================================

# --- ABA 3: EVOLUÇÕES E RELATÓRIOS ---
with tab3:
    st.header("📈 Evoluções Clínicas e Acompanhamento Diário")
    st.write("Registre o progresso detalhado das sessões, condutas aplicadas e respostas aos estímulos.")
    
    with st.form("form_evolucao_completa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            id_paciente_evolucao = st.text_input("Código/ID do Paciente:", placeholder="PAC001")
            data_sessao = st.text_input("Data da Sessão (DD/MM/AAAA):", placeholder="14/08/2026")
            tipo_sessao = st.selectbox("Tipo de Atendimento:", ["Fonoterapia", "Avaliação", "Retorno", "Supervisão", "Triagem"])
        with col2:
            descricao_evolucao = st.text_area("Evolução Clínica e Conduta (Detalhamento técnico da sessão):", placeholder="Descreva os exercícios, evolução e comportamento hoje...")
            orientacoes_casa = st.text_area("Orientações para Casa / Planejamento Estratégico Próxima Sessão:", placeholder="Anote as tarefas passadas para a família...")
            
        botao_salvar_evolucao = st.form_submit_button("💾 Salvar Evolução Completa na Nuvem")
        
    if botao_salvar_evolucao:
        if not id_paciente_evolucao or not descricao_evolucao:
            st.warning("⚠️ Os campos 'Código/ID' e 'Evolução Clínica' são obrigatórios para o prontuário!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Gravando evolução no Google Sheets..."):
                try:
                    nova_evolucao = [
                        id_paciente_evolucao,
                        data_sessao,
                        tipo_sessao,
                        descricao_evolucao,
                        orientacoes_casa
                    ]
                    aba_evolucao.append_row(nova_evolucao)
                    st.success(f"🎉 Evolução do paciente '{id_paciente_evolucao}' gravada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar evolução na nuvem: {e}")

# --- ABA 4: AGENDA INTEGRADA E MARCAÇÃO DE CONSULTAS ---
with tab4:
    st.header("📅 Agenda Avançada de Atendimentos")
    st.write("Gerencie os horários, marcações e status das consultas integradas diretamente com a nuvem.")
    
    with st.form("form_agenda_avancada", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_agenda = st.text_input("Data do Atendimento (DD/MM/AAAA):", placeholder="17/08/2026")
            horario_agenda = st.text_input("Horário da Consulta (HH:MM):", placeholder="09:00")
        with col2:
            paciente_agenda = st.text_input("Nome Completo do Paciente:", placeholder="Nome do paciente para a agenda")
            status_agenda = st.selectbox("Status Inicial do Agendamento:", ["Agendado", "Confirmado", "Atendido", "Falta Justificada", "Falta Sem Justificativa", "Cancelado"])
            
        botao_salvar_agenda = st.form_submit_button("💾 Confirmar e Agendar na Nuvem")
        
    if botao_salvar_agenda:
        if not data_agenda or not paciente_agenda:
            st.warning("⚠️ A 'Data' e o 'Nome do Paciente' são campos obrigatórios para reservar o horário!")
        elif gspread_client is None:
            st.error("❌ Não há conexão ativa com o Google Sheets.")
        else:
            with st.spinner("Sincronizando agendamento no Google Sheets..."):
                try:
                    novo_agendamento = [
                        data_agenda,
                        horario_agenda,
                        paciente_agenda,
                        status_agenda
                    ]
                    aba_agenda.append_row(novo_agendamento)
                    st.success(f"🎉 Horário agendado com sucesso para '{paciente_agenda}'!")
                except Exception as e:
                    st.error(f"Erro ao salvar compromisso na nuvem: {e}")

# ==============================================================================
# BLOCO 5 DE 5: ABA 5 — CENTRAL DO PACIENTE (PRONTUÁRIO DIGITAL UNIFICADO)
# ==============================================================================
with tab5:
    st.header("📂 Central do Paciente — Prontuário Digital Único")
    st.write("Busque e visualize o histórico completo e consolidado de qualquer paciente direto da nuvem.")
    
    if gspread_client is None:
        st.error("❌ Conexão com a nuvem indisponível. Não é possível carregar os prontuários.")
    else:
        try:
            # Puxa todas as linhas de identificação cadastrados para alimentar a lista de busca
            registros_id = aba_identificacao.get_all_records()
            
            lista_nomes_pacientes = []
            for p in registros_id:
                nome_p = p.get("Nome Completo", "") or p.get("Nome Completo:", "")
                if nome_p:
                    lista_nomes_pacientes.append(str(nome_p))
            
            # Remove duplicados e ordena em ordem alfabética
            lista_nomes_pacientes = sorted(list(set(lista_nomes_pacientes)))
            
            if not lista_nomes_pacientes:
                st.info("💡 Nenhum paciente cadastrado no Google Sheets até o momento. Vá para a Aba 1.")
            else:
                paciente_selecionado = st.selectbox("🔍 Selecione o Paciente para abrir a Pasta Digital:", lista_nomes_pacientes)
                
                # Localiza o dicionário com os dados cadastrais do paciente escolhido
                dados_cadastrais = None
                for p in registros_id:
                    nome_verificar = p.get("Nome Completo", "") or p.get("Nome Completo:", "")
                    if str(nome_verificar) == paciente_selecionado:
                        dados_cadastrais = p
                        break
                
                if dados_cadastrais:
                    # Captura o ID do paciente de forma flexível de acordo com o cabeçalho
                    id_atual = dados_cadastrais.get("Código/ID do Paciente (Ex: PAC001):", "") or dados_cadastrais.get("ID", "") or dados_cadastrais.get("id", "")
                    if not id_atual and len(dados_cadastrais.values()) > 0:
                        id_atual = list(dados_cadastrais.values())[0] # Fallback se o cabeçalho falhar
                    
                    st.markdown("---")
                    st.subheader("📋 Informações Cadastrais Básicas")
                    col_id1, col_id2 = st.columns(2)
                    with col_id1:
                        st.markdown(f"**ID do Paciente:** `{id_atual}`")
                        st.markdown(f"**Nome Completo:** {paciente_selecionado}")
                        st.markdown(f"**Data de Nascimento:** {dados_cadastrais.get('Data de Nascimento (DD/MM/AAAA):', 'Não informada')}")
                    with col_id2:
                        st.markdown(f"**Idade:** {dados_cadastrais.get('Idade:', '') or dados_cadastrais.get('Idade', 'Não informada')}")
                        st.markdown(f"**Responsável:** {dados_cadastrais.get('Nome do Responsável (Se menor):', 'Não informado')}")
                        st.markdown(f"**Contato:** {dados_cadastrais.get('Telefone de Contato (Com DDD):', 'Não informado')}")
                    
                    queixa = dados_cadastrais.get('Queixa Principal (Breve resumo):', '') or dados_cadastrais.get('Queixa Principal', 'Não registrada')
                    st.info(f"**Queixa Principal Registrada:** {queixa}")
                    
                    # --- PAINEL 2: HISTÓRICO CLÍNICO DA ANAMNESE ---
                    st.markdown("---")
                    st.subheader("🩺 Histórico de Desenvolvimento (Anamnese)")
                    try:
                        registros_anamnese = aba_anamnese.get_all_records()
                        anamnese_paciente = None
                        for a in registros_anamnese:
                            id_an_verificar = a.get("Código/ID do Paciente Cadastrado (Deve ser igual ao da Aba 1):", "") or a.get("ID", "")
                            if not id_an_verificar and len(a.values()) > 0:
                                id_an_verificar = list(a.values())[0]
                            if str(id_an_verificar).strip() == str(id_atual).strip():
                                anamnese_paciente = a
                                break
                        
                        if anamnese_paciente:
                            st.markdown(f"**Marcos do Desenvolvimento Motor:** {anamnese_paciente.get('Marcos de Desenvolvimento Motor (Sentou, andou no tempo esperado?):', 'Não informado')}")
                            st.markdown(f"**Desenvolvimento da Linguagem e Fala:** {anamnese_paciente.get('Desenvolvimento da Linguagem (Primeiras palavras, balbucios?):', 'Não informado')}")
                            st.markdown(f"**Capacidade de Compreensão:** {anamnese_paciente.get('Compreensão (Atende a comandos, atende quando chamado?):', 'Não informado')}")
                            st.markdown(f"**Padrão Comportamental:** {anamnese_paciente.get('Comportamento e Interação Social:', 'Não informado')}")
                            st.markdown(f"**Histórico Alimentar:** {anamnese_paciente.get('Histórico de Alimentação (Mastigação, seletividade alimentar, engasgos?):', 'Não informado')}")
                            st.markdown(f"**Respiração e Sono:** {anamnese_paciente.get('Respiração e Sono (Respira pela boca, ronca, sono agitado?):', 'Não informado')}")
                            st.markdown(f"**Histórico Médico e Antecedentes Familiares:** {anamnese_paciente.get('Histórico Médico, Exames e Antecedentes Familiares relevantes:', 'Não informado')}")
                        else:
                            st.warning("⚠️ Nenhuma anamnese clínica foi preenchida para este ID até o momento.")
                    except Exception as e_an:
                        st.caption(f"Não foi possível processar campos textuais da anamnese: {e_an}")
                        
                    # --- PAINEL 3: LINHA DO TEMPO DAS SESSÕES CLÍNICAS ---
                    st.markdown("---")
                    st.subheader("📈 Linha do Tempo de Atendimentos (Evoluções)")
                    try:
                        registros_evolucoes = aba_evolucao.get_all_records()
                        evolucoes_paciente = []
                        for e in registros_evolucoes:
                            id_ev_verificar = e.get("Código/ID do Paciente:", "") or e.get("ID", "")
                            if not id_ev_verificar and len(e.values()) > 0:
                                id_ev_verificar = list(e.values())[0]
                            if str(id_ev_verificar).strip() == str(id_atual).strip():
                                evolucoes_paciente.append(e)
                        
                        if not evolucoes_paciente:
                            st.info("💡 Nenhuma sessão evolutiva registrada para este paciente ainda.")
                        else:
                            for idx, ev in enumerate(evolucoes_paciente):
                                d_ev = ev.get("Data da Sessão (DD/MM/AAAA):", "Sem Data")
                                t_ev = ev.get("Tipo de Atendimento:", "Sessão")
                                desc_ev = ev.get("Evolução Clínica (Conduta, desempenho e respostas aos estímulos):", "")
                                casa_ev = ev.get("Orientações para Casa / Planejamento Próxima Sessão:", "")
                                
                                with st.expander(f"🗓️ Sessão em {d_ev} — Tipo: {t_ev}"):
                                    st.markdown(f"**Conduta e Evolução:** {desc_ev}")
                                    if casa_ev:
                                        st.markdown(f"**Orientações passadas aos responsáveis:** {casa_ev}")
                    except Exception as e_ev:
                        st.caption(f"Não foi possível processar a linha do tempo de evoluções: {e_ev}")
        except Exception as e:
            st.error(f"Erro ao carregar a Central do Paciente: {e}")
